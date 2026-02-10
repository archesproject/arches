CREATE OR REPLACE PROCEDURE public.__arches_check_tile_cardinality_violation_for_load(load_id uuid)
AS $$
UPDATE load_staging ls
SET error_message = 'excess tile error',
    passes_validation = false
FROM node_groups ng
WHERE ls.loadid = load_id
AND ls.operation = 'insert'
AND ng.nodegroupid = ls.nodegroupid
AND ng.cardinality = '1'
AND (
        EXISTS (
            SELECT 1
            FROM tiles t
            WHERE t.resourceinstanceid = ls.resourceid
            AND t.nodegroupid = ls.nodegroupid
            AND COALESCE(t.parenttileid, '00000000-0000-0000-0000-000000000000'::uuid)
                =
                COALESCE(ls.parenttileid, '00000000-0000-0000-0000-000000000000'::uuid)
        )
        OR
        EXISTS (
            SELECT 1
            FROM load_staging ls2
            WHERE ls2.loadid = load_id
            AND ls2.operation = 'insert'
            AND ls2.resourceid = ls.resourceid
            AND ls2.nodegroupid = ls.nodegroupid
            AND COALESCE(ls2.parenttileid, '00000000-0000-0000-0000-000000000000'::uuid)
                =
                COALESCE(ls.parenttileid, '00000000-0000-0000-0000-000000000000'::uuid)
            GROUP BY ls2.resourceid, ls2.nodegroupid, ls2.parenttileid
            HAVING COUNT(*) > 1
        )
);
$$ LANGUAGE SQL;