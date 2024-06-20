from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("controlledlists", "0001_initial"),
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

                -- Conceptually:
                --      a collection becomes a list
                --      a concept belonging to a collection becomes a list item
                --      a concept at the top of a collection does NOT have a parent list item and should have a depth of 0
                --      a concept below the top concepts of the collection will have a parent list item and should have a depth of > 0
                --      a prefLabel and any altLabels for a concept become list item values

                --      in the RDM concepts are sorted alphabetically, but are explicitly ordered using a list item's sortorder...
                --      sort order is calculated at the list level and ordered alphabetically within each leaf of the hierarchy

                -- Check if collection_names are provided
                if collection_names is null or array_length(collection_names, 1) = 0 then
                    return 'No collection names or identifiers provided.';
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
                    delete from controlled_list_item_values
                    where itemid in (
                        select id
                        from controlled_list_items
                        where listid in (
                            select id
                            from controlled_lists
                            where name = any(collection_names)
                        )
                    );

                    delete from controlled_list_items
                    where listid in (
                        select id
                        from controlled_lists
                        where name = any(collection_names)
                    );

                    delete from controlled_lists
                    where name = any(collection_names);
                end if;

                -- Migrate Collection -> Controlled List
                insert into controlled_lists (
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
                with recursive collection_hierarchy as (
                    select conceptidfrom as root_list,
                        conceptidto as child, 
                        0 as depth
                    from relations
                    where not exists (
                        select 1 from relations r2 where r2.conceptidto = relations.conceptidfrom
                    ) and relationtype = 'member'
                    union all
                    select ch.root_list,
                        r.conceptidto,
                        ch.depth + 1
                    from collection_hierarchy ch
                    join relations r on ch.child = r.conceptidfrom
                    where relationtype = 'member'
                ),
                -- Rank prefLabels by user provided language, 
                -- if no prefLabel in that language exists for a concept, fall back on next prefLabel ordered by languageid
                ranked_prefLabels as (
                    select ch.root_list,
                        ch.child,
                        ch.depth,
                        v.languageid, v.value, 
                        ROW_NUMBER() OVER (PARTITION BY ch.child ORDER BY (v.languageid = preferred_sort_language) DESC, languages.id) AS language_rank,
                        r.conceptidfrom
                    from collection_hierarchy ch
                    left join values v on v.conceptid = ch.child
                    left join relations r on r.conceptidto = ch.child
                    left join languages on v.languageid = languages.code
                    where v.valuetype = 'prefLabel' and 
                        r.relationtype = 'member' 
                ),
                -- Once we've assigned our root_list, we want to sort the children (to depth n) alphabetically based on their ranked prefLabel
                -- We also want to take INTO account the child's parent value, so the relations table is joined back to capture the parent.
                alpha_sorted_list_item_hierarchy as (
                    select child as id,
                        row_number() over (partition by root_list order by depth, LOWER(value)) - 1 as sortorder,
                        root_list as listid,
                        case when conceptidfrom = root_list then null -- list items at top of hierarchy have no parent list item
                            else conceptidfrom
                        end as parent_id,
                        depth
                    from ranked_prefLabels rpl
                    where language_rank = 1 and
                        root_list in (select id from controlled_lists where name = ANY(collection_names))
                )
                insert into controlled_list_items(
                    id,
                    uri,
                    sortorder,
                    guide,
                    listid,
                    parent_id
                )
                select id,
                    host || id as uri,
                    sortorder,
                    false as guide,
                    listid,
                    parent_id
                from alpha_sorted_list_item_hierarchy;


                -- Migrate concept values -> controlled list item values
                insert into controlled_list_item_values (
                    id,
                    value,
                    itemid,
                    languageid,
                    valuetype_id
                )
                select distinct (v.valueid) id,
                    value,
                    r.conceptidto as itemid,
                    languageid,
                    valuetype as valuetype_id
                from relations r
                full join values v on r.conceptidto = v.conceptid
                where relationtype = 'member' and
                    (valuetype = 'prefLabel' or valuetype = 'altLabel') and
                    r.conceptidto in (
                        select id from controlled_list_items where listid in (
                            select id from controlled_lists where name = ANY(collection_names)
                        )
                    );

                return format('Collection(s) %s migrated to controlled list(s)', array_to_string(collection_names, ', '));
            end;
            $$ language plpgsql volatile;
            """,
            """
                drop function if exists __arches_migrate_collections_to_clm cascade;
            """,
        )
    ]
