create or replace function __arches_instance_view_update() returns trigger as $$
    declare
        view_namespace text;
        model_id uuid;
        instance_id uuid;
    begin
        if (TG_OP = 'DELETE') then
            delete from public.resource_instances where resourceinstanceid = old.resourceinstanceid;
            return old;
        else
            view_namespace = format('%s.%s', tg_table_schema, tg_table_name);
            select obj_description(view_namespace::regclass, 'pg_class') into model_id;
            instance_id = new.resourceinstanceid;
            if instance_id is null then
                instance_id = public.uuid_generate_v1mc();
            end if;
            if (TG_OP = 'UPDATE') then
                update public.resource_instances
                set createdtime = new.createdtime,
                    legacyid = new.legacyid
                where resourceinstanceid = instance_id;
                return new;
            elsif (TG_OP = 'INSERT') then
                insert into public.resource_instances(
                    resourceinstanceid,
                    graphid,
                    legacyid,
                    createdtime
                ) values (
                    instance_id,
                    model_id,
                    new.legacyid,
                    now()
                );
                raise notice 'instance "%" created.', instance_id;
                return new;
            end if;
        end if;
    end;
$$ language plpgsql;
