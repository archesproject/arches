-- id, createdtime and last_updated are owned by the database, regardless of
-- whether a row arrives via the ORM, raw SQL (e.g. the ETL loaders), or COPY.
--   INSERT: always assigned here; any supplied values are discarded, so ids
--           stay in insertion order (keyset paging relies on it) and
--           timestamps can't be backdated. Loads that must keep original
--           values (e.g. pg_restore --data-only, historical migrations) need
--           the trigger bypassed (session_replication_role = replica or
--           ALTER TABLE ... DISABLE TRIGGER), followed by
--           `SELECT setval('tiles_id_seq', (SELECT max(id) FROM tiles));`
--   UPDATE: id and createdtime can never change; last_updated is bumped only
--           when some other column actually changed, so blind re-saves are
--           no-ops.
-- TG_ARGV[0] is the sequence that supplies the table's ids.
create or replace function __arches_manage_row_metadata()
returns trigger as $$
begin
    if tg_op = 'INSERT' then
        new.id := nextval(tg_argv[0]::regclass);
        new.createdtime := statement_timestamp();
        new.last_updated := statement_timestamp();
        return new;
    end if;

    new.id := old.id;
    new.createdtime := old.createdtime;
    new.last_updated := old.last_updated;
    if new is distinct from old then
        new.last_updated := statement_timestamp();
    end if;
    return new;
end;
$$ language plpgsql;
