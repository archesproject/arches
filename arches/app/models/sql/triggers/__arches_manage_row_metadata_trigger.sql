-- See __arches_manage_row_metadata(); each table passes its own id sequence.
create trigger __arches_manage_row_metadata_trigger
    before insert or update on resource_instances
    for each row
    execute function __arches_manage_row_metadata('resource_instances_id_seq');

create trigger __arches_manage_row_metadata_trigger
    before insert or update on tiles
    for each row
    execute function __arches_manage_row_metadata('tiles_id_seq');
