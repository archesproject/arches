create or replace function __arches_tile_view_update() returns trigger as $$
    begin
        if (TG_OP = 'DELETE') then
            delete from public.tiles where tileid = old.tileid;
            return old;
        elsif (TG_OP = 'UPDATE') then
            raise notice '%', tg_table_name;
            update public.tiles
            set tiledata = __arches_get_json_data_for_view(new, tg_table_schema, tg_table_name),
                nodegroupid = new.nodegroupid,
                parenttileid = __arches_get_parent_id_for_view(new, tg_table_schema, tg_table_name),
                resourceinstanceid = new.resourceinstanceid
            where tileid = new.tileid;
            return new;
        elsif (TG_OP = 'INSERT') then
            insert into public.tiles(
                tiledata,
                nodegroupid,
                parenttileid,
                resourceinstanceid
            ) values (
                __arches_get_json_data_for_view(new, tg_table_schema, tg_table_name),
                new.nodegroupid,
                __arches_get_parent_id_for_view(new, tg_table_schema, tg_table_name),
                new.resourceinstanceid
            );
            return new;
        end if;
    end;
$$ language plpgsql;
