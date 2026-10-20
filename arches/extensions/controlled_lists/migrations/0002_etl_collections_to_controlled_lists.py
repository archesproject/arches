from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("arches_controlled_lists", "0001_initial"),
        ("guardian", "0002_generic_permissions_index"),
    ]

    operations = [
        migrations.RunSQL(
            """
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
                --      a concept at the top of a collection does NOT have a parent list item and should have a depth of 0
                --      a concept below the top concepts of the collection will have a parent list item and should have a depth of > 0
                --      a prefLabel and any altLabels for a concept become list item values
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
                    search_only
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
                    false as search_only
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
                -- On each recursion, it checks if the child (aka conceptidto in relations table) is a parent for another concept
                -- All the while, it keeps track of the depth of the child concept, to be used for sorting in the next CTE
                -- The results are stored in a temporary table to avoid re-running non-filtered recursion (done on the whole relations table)
                -- We keep track of the hierarchy path in order to account for concepts that participate in multiple collections
                
                create temporary table temp_collection_hierarchy as
                    with recursive collection_hierarchy as (
                        select conceptidfrom as root_list,
                            conceptidto as child,
                            ARRAY[conceptidfrom] AS path,
                            0 as depth
                        from relations
                        where not exists (
                            select 1 from relations r2 where r2.conceptidto = relations.conceptidfrom
                        ) and relationtype = 'member'
                        union all
                        select ch.root_list,
                            r.conceptidto,
                            ch.path || r.conceptidfrom,
                            ch.depth + 1
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
                    -- Rank prefLabels by user provided language, 
                    -- if no prefLabel in that language exists for a concept, fall back on next prefLabel ordered by languageid
                    ranked_prefLabels as (
                        select ch.root_list,
                            ch.child,
                            ch.depth,
                            v.languageid, v.value, 
                            ROW_NUMBER() OVER (PARTITION BY ch.child ORDER BY (v.languageid = preferred_sort_language) DESC, languages.id) AS language_rank,
                            r.conceptidfrom,
                            ch.path
                        from filtered_collection_hierarchy ch
                        left join values v on v.conceptid = ch.child
                        left join relations r on r.conceptidto = ch.child
                        left join languages on v.languageid = languages.code
                        where v.valuetype = 'prefLabel'
                            and r.relationtype = 'member'
                            and r.conceptidfrom in (select unnest(path) from filtered_collection_hierarchy)
                    ),
                    -- Once we've assigned our root_list, we want to sort the children (to depth n) alphabetically based on their ranked prefLabel
                    -- We also want to take into account the child's parent value, so the relations table is joined back to capture the parent.
                    alpha_sorted_list_item_hierarchy as (
                        select child as id,
                            row_number() over (partition by root_list order by depth, LOWER(value)) - 1 as sortorder,
                            root_list as list_id,
                            case when conceptidfrom = root_list then null -- list items at top of hierarchy have no parent list item
                                else conceptidfrom
                            end as parent_id,
                            depth
                        from ranked_prefLabels rpl
                        where language_rank = 1 and
                            root_list in (select id from arches_controlled_lists_list where name = collection)
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
            """,
            """
                drop function if exists __arches_migrate_collections_to_clm cascade;
            """,
        )
    ]
