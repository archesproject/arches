from django.db import migrations


class Migration(migrations.Migration):

    forward_sql = """
    create or replace function __arches_migrate_collections_to_clm(
        collection_names text[] default null, -- one or more collections to be migrated to controlled lists
        host text default 'http://localhost:8000/plugins/controlled-list-manager/item/',
        overwrite boolean default FALSE,
        preferred_sort_language text default 'en'
    )
    returns text as $$
    declare failed_collections text[];
        collection text;
        listitems_to_update_with_multiple_values uuid[];
    begin
        -- RDM Collections to Controlled Lists & List Items Migration --
        -- To use, run: 
        --      select * from __arches_migrate_collections_to_clm(
        --          ARRAY['Getty AAT', 'http://vocab.getty.edu/aat'],
        --          'http://localhost:8000/plugins/controlled-list-manager/item/',
        --          True,
        --          'en'
        --       );
        -- where the input array values are concept prefLabels or identifiers and the optional language is used for sorting
        -- for collections that contain an apostrophe, use two single quotes, e.g. 'John''s list'

        -- Conceptually:
        --      a collection becomes a list
        --      a concept belonging to a collection becomes a list item
        --      a prefLabel and any altLabels for a concept become list item values
        --      a concept with no sortorder value will sorted alphabetically around its siblings 
        --          under a given parent by the concept's best prefLabel
        --      a concept with an existing sortorder value will be sorted ahead of any siblings with no sortorder value
        --      a concept that participates in multiple collections and/or exists at n-locations in the collection
        -- 			will have distinct list items for each occurrence in the hierarchy beyond the first

        --      in the RDM concepts are sorted alphabetically, but list items are explicitly ordered using sortorder...
        --      sort order is calculated at the list level and ordered alphabetically within each leaf of the hierarchy

        -- Check if collection_names are provided
        if collection_names is null or array_length(collection_names, 1) = 0 then
            raise exception 'No collection names or identifiers provided.';
        end if;

        -- Check if input collection names or identifiers exist in the database
        failed_collections := array(
            select names
            from unnest(collection_names) as names
            where names not in (
                select value 
                from values v
                left join concepts c on c.conceptid = v.conceptid
                where c.nodetype = 'Collection' and
                    (v.valuetype = 'prefLabel' or
                    v.valuetype = 'identifier')
            )
        );
        
        -- If all provided names do not match any collections, end operation
        if array_length(collection_names, 1) = array_length(failed_collections, 1) then
            raise exception 'Failed to find the following collections in the database: %', array_to_string(failed_collections, ', ')
            using hint = 'Please ensure the provided name or identifier matches a valid collection';
        end if;
        
        -- Remove user provided values from collection_names if they aren't a collection (identifier or prefLabel)
        if array_length(failed_collections, 1) > 0 then
            raise warning 'Failed to find the following collections in the database: %', array_to_string(failed_collections, ', ');
            collection_names := array(
                select array_agg(elem)
                from unnest(collection_names) elem
                where elem <> all(failed_collections)
            );
        end if;

        -- If overwrite flag is provided, completely recreate the list/items/values
        if overwrite then
            delete from arches_controlled_lists_listitemvalue
            where list_item_id in (
                select id
                from arches_controlled_lists_listitem
                where list_id in (
                    select id
                    from arches_controlled_lists_list
                    where name = any(collection_names)
                )
            );

            delete from arches_controlled_lists_listitem
            where list_id in (
                select id
                from arches_controlled_lists_list
                where name = any(collection_names)
            );

            delete from arches_controlled_lists_list
            where name = any(collection_names);
        end if;

        -- Migrate Collection -> Controlled List
        insert into arches_controlled_lists_list (
            id,
            name,
            dynamic,
            searchable
        )
        with identifier_conceptids as (
            select c.conceptid
            from concepts c
            full join values v on
                c.conceptid = v.conceptid
            where nodetype = 'Collection' and
                v.valuetype = 'identifier' and
                value = ANY(collection_names)
            )
        select c.conceptid as id,
            value as name,
            false as dynamic,
            false as searchable
        from concepts c
        full join values v on
            c.conceptid = v.conceptid
        where nodetype = 'Collection' and
            v.valuetype = 'prefLabel' and
            (
                c.conceptid in (select * from identifier_conceptids) or
                value = ANY(collection_names)
            );

        -- Migrate Concepts participating in Collections -> Controlled List Items

        create temporary table temp_collection_hierarchy as
        -- The recursive CTE below is used to assign the conceptid of the list at the root to each concept to be migrated
        -- On each recursion, it checks if the child (aka conceptidto in relations table) is a parent for another concept.
        -- The results are stored in a temporary table to avoid re-running non-filtered recursion (done on the whole relations table)
        -- We keep track of the hierarchy path in order to account for concepts that participate in multiple collections
        with recursive collection_hierarchy as (
            select conceptidfrom as root_list,
                conceptidto as child,
                ARRAY[conceptidfrom] AS path,
                conceptidfrom as parent_id
            from relations
            where not exists (
                select 1 from relations r2 where r2.conceptidto = relations.conceptidfrom
            ) and relationtype = 'member'
            union all
            select ch.root_list,
                r.conceptidto,
                ch.path || r.conceptidfrom,
                r.conceptidfrom as parent_id
            from collection_hierarchy ch
            join relations r on ch.child = r.conceptidfrom
            where relationtype = 'member'
        ),
        -- Filter out any collections that are not intended to be migrated in this execution
        filtered_hierarchy as (
            select
                root_list as list_id,
                child as list_item_id,
                parent_id,
                path,
                v.value::int as sortorder
            from collection_hierarchy ch
            left join values v on v.conceptid = ch.child and v.valuetype = 'sortorder'
            where root_list in (select id from arches_controlled_lists_list where name = ANY(collection_names))
        ),
        -- Assign row number to help identify concepts that participate in multiple collections
        -- or exist already as listitems and therefore need new listitem_id's and listitemvalue_id's
        assign_row_num as (
            select list_item_id,
                sortorder,
                list_id,
                parent_id,
                existing_item_id,
                path,
                ROW_NUMBER() OVER (
                    PARTITION BY list_item_id
                    ORDER BY existing_item_id NULLS LAST, sortorder ASC, list_id, parent_id
                ) as num_concept_occurrence
            from (
                select fh.list_item_id,
                    fh.sortorder,
                    fh.list_id,
                    fh.parent_id,
                    fh.path,
                    li.id as existing_item_id
                from filtered_hierarchy fh
                left join arches_controlled_lists_listitem li on fh.list_item_id = li.id 
            ) as t
        ),
        -- For items that occur in multiple places in the hierarchy or already exist as list items
        -- we need to create a new list item for each occurrence of that node in the concept graph
        mint_new_ids as (
            select
                list_item_id as legacy_list_item_id,
                case 
                    when existing_item_id is not null or num_concept_occurrence > 1 then uuid_generate_v4()
                    else list_item_id
                end as list_item_id,
                list_id,
                parent_id,
                path,
                sortorder
            from assign_row_num
        ),
        -- Make sure we can point back to the original concept records so we can easily get its associated values
        -- and join prefLabels to begin process of creating sortorder for list items that don't have it
        new_items_with_best_label as (
            select mni.list_item_id,
                mni.list_id,
                case
                    when parent_crosswalk.list_item_id = mni.list_id then null -- list items at top of hierarchy have no parent list item
                    else parent_crosswalk.list_item_id -- map to correct parent if new id was minted for it
                end as parent_id,
                mni.legacy_list_item_id,
                mni.parent_id as legacy_parent_id,
                mni.sortorder,
                v.languageid,
                v.value as prefLabel
            from mint_new_ids mni
            left join mint_new_ids as parent_crosswalk 
                on mni.parent_id = parent_crosswalk.legacy_list_item_id
                and mni.list_id = parent_crosswalk.list_id
                -- ensure we're getting the right lineage by comparing the path of the parent & child(minus last element)
                and mni.path[1:array_length(mni.path, 1)-1] = parent_crosswalk.path
            left join (
                -- Get the best prefLabel for each list item based on user supplied preferred_sort_language / fall back
                select conceptid, value, languageid, valuetype,
                    ROW_NUMBER() OVER (
                        PARTITION BY conceptid
                        ORDER BY (v.languageid = preferred_sort_language) DESC, languages.id
                    ) AS list_item_language_rank
                from values v
                left join languages on v.languageid = languages.code
                where valuetype = 'prefLabel'
            ) v on mni.legacy_list_item_id = v.conceptid and v.list_item_language_rank = 1
        )
        -- Calculate sortorder relative to siblings
        -- and join URI's stored as identifiers if they exist
        -- and crosswalk `collector` label to `guide` flag
        select list_item_id,
            list_id,
            parent_id,
            legacy_list_item_id,
            legacy_parent_id,
            ROW_NUMBER() OVER (
                PARTITION BY parent_id, list_id
                ORDER BY sortorder NULLS LAST, lower(prefLabel)
            )-1 AS sortorder,
            prefLabel,
            identifier.value as uri,
            guide.value as guide
        from new_items_with_best_label
        left join (
            select conceptid, value
            from values
            where valuetype = 'identifier'
        ) identifier on legacy_list_item_id = identifier.conceptid
        left join (
            select conceptid, value
            from values
            where valuetype = 'collector'
        ) guide on legacy_list_item_id = guide.conceptid;


        insert into arches_controlled_lists_listitem (
            id,
            uri,
            sortorder,
            guide,
            list_id,
            parent_id
        )
        select
            list_item_id,
            case when uri is not null then uri
                else host || legacy_list_item_id
            end as uri,
            sortorder,
            case when guide is not null then True
                else False
            end as guide,
            list_id,
            parent_id
        from temp_collection_hierarchy;
        

        -- Migrate concept values -> controlled list item values
        insert into arches_controlled_lists_listitemvalue (
            id,
            value,
            list_item_id,
            languageid,
            valuetype_id
        )
        select
            uuid_generate_v4() as id,
            v.value,
            tch.list_item_id,
            v.languageid,
            v.valuetype
        from temp_collection_hierarchy tch
        join values v on tch.legacy_list_item_id = v.conceptid
        where valuetype in (
            select valuetype from d_value_types where category in ('note', 'label')
        );
        
        drop table if exists temp_collection_hierarchy;
        drop table if exists temp_list_items_and_values;

        return format('Collection(s) %s migrated to controlled list(s)', array_to_string(collection_names, ', '));
    end;
    $$ language plpgsql volatile;
    """

    reverse_sql = """
    create or replace function __arches_migrate_collections_to_clm(
        collection_names text[] default null, -- one or more collections to be migrated to controlled lists
        host text default 'http://localhost:8000/plugins/controlled-list-manager/item/',
        overwrite boolean default FALSE,
        preferred_sort_language text default 'en'
    )
    returns text as $$
    declare failed_collections text[];
        collection text;
        listitems_to_update_with_multiple_values uuid[];
    begin
        -- RDM Collections to Controlled Lists & List Items Migration --
        -- To use, run: 
        --      select * from __arches_migrate_collections_to_clm(
        --          ARRAY['Getty AAT', 'http://vocab.getty.edu/aat'],
        --          'http://localhost:8000/plugins/controlled-list-manager/item/',
        --          True,
        --          'en'
        --       );
        -- where the input array values are concept prefLabels or identifiers and the optional language is used for sorting
        -- for collections that contain an apostrophe, use two single quotes, e.g. 'John''s list'

        -- Conceptually:
        --      a collection becomes a list
        --      a concept belonging to a collection becomes a list item
        --      a prefLabel and any altLabels for a concept become list item values
        --      a concept with no sortorder value will sorted alphabetically around its siblings 
        --          under a given parent by the concept's best prefLabel
        --      a concept with an existing sortorder value will be sorted ahead of any siblings with no sortorder value
        --      a concept that participates in multiple collections will have distinct list items for each new list it belongs to

        --      in the RDM concepts are sorted alphabetically, but list items are explicitly ordered using sortorder...
        --      sort order is calculated at the list level and ordered alphabetically within each leaf of the hierarchy

        -- Check if collection_names are provided
        if collection_names is null or array_length(collection_names, 1) = 0 then
            raise exception 'No collection names or identifiers provided.';
        end if;

        -- Check if input collection names or identifiers exist in the database
        failed_collections := array(
            select names
            from unnest(collection_names) as names
            where names not in (
                select value 
                from values v
                left join concepts c on c.conceptid = v.conceptid
                where c.nodetype = 'Collection' and
                    (v.valuetype = 'prefLabel' or
                    v.valuetype = 'identifier')
            )
        );
        
        -- If all provided names do not match any collections, end operation
        if array_length(collection_names, 1) = array_length(failed_collections, 1) then
            raise exception 'Failed to find the following collections in the database: %', array_to_string(failed_collections, ', ')
            using hint = 'Please ensure the provided name or identifier matches a valid collection';
        end if;
        
        -- Remove user provided values from collection_names if they aren't a collection (identifier or prefLabel)
        if array_length(failed_collections, 1) > 0 then
            raise warning 'Failed to find the following collections in the database: %', array_to_string(failed_collections, ', ');
            collection_names := array(
                select array_agg(elem)
                from unnest(collection_names) elem
                where elem <> all(failed_collections)
            );
        end if;

        -- If overwrite flag is provided, completely recreate the list/items/values
        if overwrite then
            delete from arches_controlled_lists_listitemvalue
            where list_item_id in (
                select id
                from arches_controlled_lists_listitem
                where list_id in (
                    select id
                    from arches_controlled_lists_list
                    where name = any(collection_names)
                )
            );

            delete from arches_controlled_lists_listitem
            where list_id in (
                select id
                from arches_controlled_lists_list
                where name = any(collection_names)
            );

            delete from arches_controlled_lists_list
            where name = any(collection_names);
        end if;

        -- Migrate Collection -> Controlled List
        insert into arches_controlled_lists_list (
            id,
            name,
            dynamic,
            searchable
        )
        with identifier_conceptids as (
            select c.conceptid
            from concepts c
            full join values v on
                c.conceptid = v.conceptid
            where nodetype = 'Collection' and
                v.valuetype = 'identifier' and
                value = ANY(collection_names)
            )
        select c.conceptid as id,
            value as name,
            false as dynamic,
            false as searchable
        from concepts c
        full join values v on
            c.conceptid = v.conceptid
        where nodetype = 'Collection' and
            v.valuetype = 'prefLabel' and
            (
                c.conceptid in (select * from identifier_conceptids) or
                value = ANY(collection_names)
            );

        -- Migrate Concepts participating in Collections -> Controlled List Items & Controlled List Item Values

        -- The recursive CTE below is used to assign the conceptid of the list at the root to each concept to be migrated
        -- On each recursion, it checks if the child (aka conceptidto in relations table) is a parent for another concept.
        -- The results are stored in a temporary table to avoid re-running non-filtered recursion (done on the whole relations table)
        -- We keep track of the hierarchy path in order to account for concepts that participate in multiple collections
        
        create temporary table temp_collection_hierarchy as
            with recursive collection_hierarchy as (
                select conceptidfrom as root_list,
                    conceptidto as child,
                    ARRAY[conceptidfrom] AS path
                from relations
                where not exists (
                    select 1 from relations r2 where r2.conceptidto = relations.conceptidfrom
                ) and relationtype = 'member'
                union all
                select ch.root_list,
                    r.conceptidto,
                    ch.path || r.conceptidfrom
                from collection_hierarchy ch
                join relations r on ch.child = r.conceptidfrom
                where relationtype = 'member'
            )
            select * from collection_hierarchy;
        
        -- This temp table is used to stage list items and values 
        create temporary table temp_list_items_and_values (
            list_item_id uuid,
            sortorder bigint,
            list_id uuid,
            parent_id uuid,
            legacy_conceptid uuid,
            listitemvalue_id uuid,
            listitemvalue text,
            listitemvalue_languageid text,
            listitemvalue_valuetype text,
            rownumber int
        );

        -- Build the new hierarchies at the list level, mainly to account for concepts that participate in multiple collections
        -- then stash results in temp table for preprocessing before inserting into CLM tables
        foreach collection in array collection_names loop
            with filtered_collection_hierarchy as (
                select * 
                from temp_collection_hierarchy
                where root_list in (select id from arches_controlled_lists_list where name = collection)
            ),
            items_with_sortorder as (
                select ch.child,
                    v.value as sortorder
                from filtered_collection_hierarchy ch
                join values v on v.conceptid = ch.child
                where v.valuetype = 'sortorder'
            ),
            -- Rank prefLabels by user provided language, 
            -- if no prefLabel in that language exists for a concept, fall back on next prefLabel ordered by languageid
            ranked_prefLabels as (
                select ch.root_list,
                    ch.child,
                    iso.sortorder::int,
                    v.languageid,
                    v.value,
                    ROW_NUMBER() OVER (PARTITION BY ch.child ORDER BY (v.languageid = preferred_sort_language) DESC, languages.id) AS language_rank,
                    r.conceptidfrom,
                    ch.path
                from filtered_collection_hierarchy ch
                left join values v on v.conceptid = ch.child
                left join relations r on r.conceptidto = ch.child
                left join languages on v.languageid = languages.code
                left join items_with_sortorder iso on iso.child = ch.child
                where v.valuetype = 'prefLabel'
                    and r.relationtype = 'member'
                    and r.conceptidfrom in (select unnest(path) from filtered_collection_hierarchy)
            ),
            -- Once we've found the best prefLabel for each concept, we can use it to alphabetically sort concepts that don't have a sortorder value
            -- prioritizing concepts that do have an existing sortorder value
            alpha_sorted_list_item_hierarchy as (
                select child as id,
                    row_number() over (partition by conceptidfrom order by sortorder, LOWER(value)) - 1 as sortorder,
                    case when conceptidfrom = root_list then null -- list items at top of hierarchy have no parent list item
                        else conceptidfrom
                    end as parent_id,
                    root_list as list_id
                from ranked_prefLabels rpl
                where language_rank = 1
            )
            insert into temp_list_items_and_values (
                list_item_id,
                sortorder,
                list_id,
                parent_id,
                legacy_conceptid,
                listitemvalue_id,
                listitemvalue,
                listitemvalue_languageid,
                listitemvalue_valuetype
            )
            select lih.id as list_item_id,
                lih.sortorder,
                lih.list_id,
                lih.parent_id,
                lih.id as legacy_conceptid,
                v.valueid as listitemvalue_id,
                v.value,
                v.languageid,
                v.valuetype
            from alpha_sorted_list_item_hierarchy lih
            join values v on v.conceptid = lih.id
            where valuetype in (
                select valuetype from d_value_types where category in ('note', 'label')
            );
        end loop;

        -- Assign row number to help identify concepts that participate in multiple collections
        -- or exist already as listitems and therefore need new listitem_id's and listitemvalue_id's
        with assign_row_num as (
            select list_item_id,
                sortorder,
                list_id,
                parent_id,
                existing_item,
                ROW_NUMBER() OVER (PARTITION BY list_item_id ORDER BY existing_item DESC, sortorder ASC) as init_rownumber
            from (
                select list_item_id,
                    sortorder,
                    list_id,
                    parent_id,
                    FALSE as existing_item
                from temp_list_items_and_values
                union all
                select id as list_item_id,
                    sortorder,
                    list_id,
                    parent_id,
                    TRUE as existing_item
                from arches_controlled_lists_listitem
                ) as t
        )
        update temp_list_items_and_values t
        set rownumber = init_rownumber
        from assign_row_num a
        where t.list_item_id = a.list_item_id 
            and t.list_id = a.list_id;

        -- For concepts that participate in multiple collections, mint new listitem_id's and listitemvalue_id's
        -- However, if a concept needs a new listitem_id, and has multiple values associated with it, ensure that
        -- the new listitem_id is the same for all listitemvalues
        listitems_to_update_with_multiple_values := array(
            select list_item_id
            from temp_list_items_and_values
            where rownumber > 1
            group by list_item_id
            having count(*) > 1
        );

        with new_list_item_ids as (
            select legacy_list_item_id,
                uuid_generate_v4() as new_list_item_id
            from unnest(listitems_to_update_with_multiple_values) as t(legacy_list_item_id)
        )
        update temp_list_items_and_values t
        set list_item_id = new_list_item_id
        from new_list_item_ids n
        where t.list_item_id = n.legacy_list_item_id
            and rownumber > 1;

        -- Update list_item_ids for items that don't have multiple values (like prefLabel)
        if array_length(listitems_to_update_with_multiple_values, 1) > 0 then 
            update temp_list_items_and_values
            set list_item_id = uuid_generate_v4()
            where rownumber > 1
                and legacy_conceptid != any(listitems_to_update_with_multiple_values)
                and list_item_id = legacy_conceptid;
        else
            update temp_list_items_and_values
            set list_item_id = uuid_generate_v4()
            where rownumber > 1
                and list_item_id = legacy_conceptid;
        end if;

        -- Update listitemvalue_ids
        update temp_list_items_and_values
        set listitemvalue_id = uuid_generate_v4()
        where rownumber > 1;
        
        insert into arches_controlled_lists_listitem (
            id,
            uri,
            sortorder,
            guide,
            list_id,
            parent_id
        )
        select distinct on (list_item_id, list_id)
            list_item_id,
            host || legacy_conceptid as uri,
            sortorder,
            false as guide,
            list_id,
            parent_id
        from temp_list_items_and_values;

        -- Migrate concept values -> controlled list item values
        insert into arches_controlled_lists_listitemvalue (
            id,
            value,
            list_item_id,
            languageid,
            valuetype_id
        )
        select listitemvalue_id,
            listitemvalue,
            list_item_id,
            listitemvalue_languageid,
            listitemvalue_valuetype
        from temp_list_items_and_values;
        
        drop table if exists temp_collection_hierarchy;
        drop table if exists temp_list_items_and_values;

        return format('Collection(s) %s migrated to controlled list(s)', array_to_string(collection_names, ', '));
    end;
    $$ language plpgsql volatile;
    """

    dependencies = [
        ('arches_controlled_lists', '0008_ensure_languages_in_sync'),
    ]

    operations = [
        migrations.RunSQL(
            forward_sql,
            reverse_sql,
        ),
    ]
