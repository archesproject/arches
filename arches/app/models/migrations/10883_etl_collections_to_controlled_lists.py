from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '10541_controlled_list_manager'),
    ]

    operations = [
        migrations.RunSQL(
            """
            create or replace function __arches_migrate_collections_to_clm(
                collection_names text[] default null -- one or more collections to be migrated to controlled lists
            )
            returns text as $$
            declare failed_collections text[];
            begin
                -- RDM Collections to Controlled Lists & List Items Migration --
                -- To use, run: 
                --      select * from __arches_migrate_collections_to_clm(ARRAY['Getty AAT', 'http://vocab.getty.edu/aat']);
                -- where the input values are concept prefLabels or identifiers

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
                    return 'No collection names provided.';
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
                
                if array_length(failed_collections, 1) > 0 then
                    raise warning 'Failed to find the following collections in the database: %s', array_to_string(failed_collections, ', ');
                    collection_names := array(
                        select array_agg(elem)
                        from unnest(collection_names) elem
                        where elem <> all(failed_collections)
                    );
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
                -- Once we've assigned our root_list, we want to sort the children (to depth n) alphabetically based on their prefLabel
                -- We also want to take INTO account the child's parent value, so the relations table is joined back to capture the parent.
                alpha_sorted_list_item_hierarchy as (
                    select child as id,
                        row_number() over (partition by root_list order by depth, v.value) - 1 as sortorder, 
                        root_list as listid,
                        case when r.conceptidfrom = root_list then null -- list items at top of hierarchy have no parent list item
                            else r.conceptidfrom
                        end as parent_id
                    from collection_hierarchy ch
                    left join values v on v.conceptid = ch.child
                    join relations r on r.conceptidto = ch.child
                    where v.valuetype = 'prefLabel' and 
                        r.relationtype = 'member' and
                        root_list in (select id from controlled_lists) -- 
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
                    null as uri, -- TODO: dynamic handling of URI generation/ETL
                    sortorder,
                    false as guide, -- What does this mean in context of CLM?
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
                select v.valueid as id,
                    value,
                    r.conceptidto as itemid,
                    languageid,
                    valuetype as valuetype_id
                from relations r
                full join values v on r.conceptidto = v.conceptid
                where relationtype = 'member' and
                    (valuetype = 'prefLabel' or valuetype = 'altLabel') and
                    r.conceptidto in (select id from controlled_list_items); -- don't create values for list items that don't exist

                return format('collection(s) %s migrated to controlled list(s)', collection_names);
            end;
            $$ language plpgsql volatile;
            """,
                """
                drop function if exists __arches_migrate_collections_to_clm cascade;
            """,
        )
    ]
