create or replace function __arches_get_labels_for_concept_node(
    node_id uuid,
    language_id text default 'en'
) returns table (
    depth int,
    valueid uuid,
    value text,
    conceptid uuid
) as $$
declare
    collector_id uuid;
    value_id uuid;
begin
    select (config->>'rdmCollection')::text into collector_id
    from nodes where nodeid = node_id;

    RETURN QUERY WITH RECURSIVE

        ordered_relationships AS (
        (
            SELECT r.conceptidfrom, r.conceptidto, r.relationtype, (
                SELECT v1.value
                FROM values v1
                WHERE v1.conceptid=r.conceptidto
                AND v1.valuetype in ('prefLabel')
                ORDER BY (
                    CASE WHEN v1.languageid = language_id THEN 10
                    WHEN v1.languageid like (language_id || '%') THEN 5
                    WHEN v1.languageid like (language_id || '%') THEN 2
                    ELSE 0
                    END
                ) desc limit 1
            ) as valuesto,
            (
                SELECT v2.value::int
                FROM values v2
                WHERE v2.conceptid=r.conceptidto
                AND v2.valuetype in ('sortorder')
                limit 1
            ) as sortorder,
            (
                SELECT v3.value
                FROM values v3
                WHERE v3.conceptid=r.conceptidto
                AND v3.valuetype in ('collector')
                limit 1
            ) as collector
            FROM relations r
            WHERE r.conceptidfrom = collector_id
            and (r.relationtype = 'member')
            ORDER BY sortorder, valuesto
        )
        UNION
        (
            SELECT r.conceptidfrom, r.conceptidto, r.relationtype,(
                SELECT v4.value
                FROM values v4
                WHERE v4.conceptid=r.conceptidto
                AND v4.valuetype in ('prefLabel')
                ORDER BY (
                    CASE WHEN v4.languageid = language_id THEN 10
                    WHEN v4.languageid like (language_id || '%') THEN 5
                    WHEN v4.languageid like (language_id || '%') THEN 2
                    ELSE 0
                    END
                ) desc limit 1
            ) as valuesto,
            (
                SELECT v5.value::int
                FROM values v5
                WHERE v5.conceptid=r.conceptidto
                AND v5.valuetype in ('sortorder')
                limit 1
            ) as sortorder,
            (
                SELECT v6.value
                FROM values v6
                WHERE v6.conceptid=r.conceptidto
                AND v6.valuetype in ('collector')
                limit 1
            ) as collector
            FROM relations r
            JOIN ordered_relationships b ON(b.conceptidto = r.conceptidfrom)
            WHERE (r.relationtype = 'member')
            ORDER BY sortorder, valuesto
        )
    ),

    children AS (
        SELECT r.conceptidfrom, r.conceptidto,
            to_char(row_number() OVER (), 'fm000000') as row,
            r.collector,
            1 AS depth       ---|NonRecursive Part
            FROM ordered_relationships r
            WHERE r.conceptidfrom = collector_id
            and (r.relationtype = 'member')
        UNION
            SELECT r.conceptidfrom, r.conceptidto,
            row || '-' || to_char(row_number() OVER (), 'fm000000'),
            r.collector,
            2 as depth      ---|RecursivePart
            FROM ordered_relationships r
            JOIN children b ON(b.conceptidto = r.conceptidfrom)
            WHERE (r.relationtype = 'member')

    )

    select
        c.depth,
        v7.valueid,
        v7.value,
        v7.conceptid
    FROM children c
    join values v7 on v7.conceptid = c.conceptidto
    where v7.valuetype in ('prefLabel')
        and v7.languageid like (language_id || '%')
    order by row;
end $$ language plpgsql volatile;
