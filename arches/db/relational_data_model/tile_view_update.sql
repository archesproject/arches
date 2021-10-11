create or replace function __arches_tile_view_update() returns trigger as $$
    declare
        group_id uuid;
        parent_id uuid;
        json_data json;
    begin
        if (TG_OP = 'DELETE') then
            delete from public.tiles where tileid = old.tileid;
            return old;
        else
            select obj_description('person.name_part'::regclass, 'pg_class') into group_id;
            select __arches_get_json_data_for_view(new, tg_table_schema, tg_table_name) into json_data;
            select __arches_get_parent_id_for_view(new, tg_table_schema, tg_table_name) into parent_id;
            if (TG_OP = 'UPDATE') then
                update public.tiles
                set tiledata = json_data,
                    nodegroupid = group_id,
                    parenttileid = parent_id,
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
                    json_data,
                    group_id,
                    parent_id,
                    new.resourceinstanceid
                );
                return new;
            end if;
        end if;
    end;
$$ language plpgsql;
