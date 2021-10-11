create or replace function __arches_tile_view_update() returns trigger as $$
    begin
        if (tg_op = 'delete') then
            delete from public.tiles where tileid = old.tileid;
            return old;
        elsif (tg_op = 'update') then
            -- update public.tiles
            -- set tiledata = __arches_get_json_data_for_view(new),
            --     nodegroupid = new.nodegroupid,
            --     parenttileid = __arches_get_parent_id_for_view(new),
            --     resourceinstanceid = new.resourceinstanceid
            -- where tileid = new.tileid;
            return new;
        elsif (tg_op = 'insert') then
            -- insert into public.tiles(
            --     tiledata,
            --     nodegroupid,
            --     parenttileid,
            --     resourceinstanceid
            -- ) values (
            --     __arches_get_json_data_for_view(new),
            --     new.nodegroupid,
            --     __arches_get_parent_id_for_view(new)
            --     new.resourceinstanceid
            -- );
            return new;
        end if;
    end;
$$ language plpgsql;
