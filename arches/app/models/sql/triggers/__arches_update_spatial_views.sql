sv_perform := '';
valid_geom_nodeid := false;
has_att_nodes := 0;
valid_att_nodeids := false;
valid_language_count := 0;

if tg_op = 'INSERT' or tg_op = 'UPDATE' then
    valid_geom_nodeid := (select count(*) from nodes where nodeid = new.geometrynodeid and datatype = 'geojson-feature-collection') > 0;
    if valid_geom_nodeid is false then
        raise exception 'geometrynodeid is not a valid nodeid';
    end if;


    if jsonb_typeof(new.attributenodes::jsonb) = 'array' then
        has_att_nodes := jsonb_array_length(new.attributenodes);
        if has_att_nodes = 0 then
            raise exception 'attributenodes needs at least one attribute dict';
        else
            valid_att_nodeids := (
                with attribute_nodes as (
                    select * from jsonb_to_recordset(new.attributenodes) as x(nodeid uuid, description text)
                )
                select count(*) from attribute_nodes att join nodes n1 on att.nodeid = n1.nodeid
                ) > 0;

            if valid_att_nodeids is false then
                raise exception 'attributenodes contains an invalid nodeid';
            end if;
        end if;
    else
        raise exception 'attributenodes needs to be an array';
    end if;
end if;


if tg_op = 'DELETE' then
    sv_perform := sv_perform || format(
        'select __arches_delete_spatial_view(%L,%L);'
        , old.slug
        , old.schema);

    if sv_perform <> '' then
        execute sv_perform;
    end if;

    return old;

elsif tg_op = 'INSERT' then
    if new.isactive = true then
        sv_perform := sv_perform || format(
            'select __arches_create_spatial_view(%L, %L::uuid, %L::jsonb, %L, %L, %L, %L);'
            , new.slug
            , new.geometrynodeid
            , new.attributenodes
            , new.schema
            , new.description
            , new.ismixedgeometrytypes
            , new.languageid);
    end if;

    if sv_perform <> '' then
        execute sv_perform;
    end if;

    return new;

elsif tg_op = 'UPDATE' then

    if new.isactive = true then
        sv_perform := sv_perform || format(
            'select __arches_update_spatial_view(%L, %L, %L, %L::uuid, %L::jsonb, %L, %L, %L);'
            , old.slug
            , old.schema
            , new.slug
            , new.geometrynodeid
            , new.attributenodes
            , new.schema
            , new.description
            , new.ismixedgeometrytypes
            , new.languageid);
    else
        sv_perform := sv_perform || format(
            'select __arches_delete_spatial_view(%L,%L);'
            , old.slug
            , old.schema);
    end if;

    if sv_perform <> '' then
        execute sv_perform;
    end if;

    return new;
end if;
