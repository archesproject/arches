CREATE OR REPLACE PROCEDURE public.__arches_check_tile_cardinality_violation_for_load(load_id uuid)
AS $$
    UPDATE load_staging
        SET error_message = 'excess tile error', passes_validation = false
        WHERE loadid = load_id
        AND operation = 'insert'
        AND (resourceid, nodegroupid, COALESCE(parenttileid::text, '')) IN (
            SELECT t.resourceinstanceid, t.nodegroupid, COALESCE(t.parenttileid::text, '')
                FROM tiles t, node_groups ng
                WHERE t.nodegroupid = ng.nodegroupid
                AND ng.cardinality = '1'
            UNION
            SELECT ls.resourceid, ls.nodegroupid, COALESCE(ls.parenttileid::text, '')
                FROM load_staging ls, node_groups ng
                WHERE ls.nodegroupid = ng.nodegroupid
                AND ng.cardinality = '1'
                GROUP BY ls.resourceid, ls.nodegroupid, COALESCE(ls.parenttileid::text, ''), ls.loadid
                HAVING count(*) > 1
                AND ls.loadid = load_id
        );
$$ LANGUAGE SQL;