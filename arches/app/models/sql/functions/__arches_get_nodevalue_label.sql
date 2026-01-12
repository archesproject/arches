CREATE OR REPLACE FUNCTION public.__arches_get_nodevalue_label(
    node_value jsonb,
    in_nodeid uuid,
    language_id text DEFAULT 'en')
    RETURNS text
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
    declare
        return_label         text := '';
        nodevalue_tileid     text;
        value_nodeid         text;
    begin

        if node_value is null or in_nodeid is null then
            return '';
        end if;

        select n.config ->> 'nodeid'
        into value_nodeid
        from nodes n
        where n.nodeid = in_nodeid::uuid;

        select __arches_get_node_display_value(t.tiledata, value_nodeid, language_id)
        into return_label
        from tiles t
        where t.tileid = node_value::uuid;
        
        if return_label is null then
            return_label := '';
        end if;
        
    return return_label;
    end;                
$BODY$;
