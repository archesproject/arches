create or replace function __arches_tile_view_insert_row() returns trigger as $$
begin
    return new;
end
$$ language plpgsql;

create or replace function __arches_tile_view_update_row() returns trigger as $$
begin
    return new;
end
$$ language plpgsql;

create or replace function __arches_tile_view_delete_row() returns trigger as $$
begin
    return new;
end
$$ language plpgsql;
