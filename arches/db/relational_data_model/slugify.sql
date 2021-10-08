create extension if not exists "unaccent";

create or replace function __arches_slugify(
    "value" text
) returns text as $$
    -- removes accents (diacritic signs) from a given string
    with "unaccented" as (
        select unaccent("value") as "value"
    ),
    -- lowercases the string
    "lowercase" as (
        select lower("value") as "value"
        from "unaccented"
    ),
    -- remove single and double quotes
    "removed_quotes" as (
        select regexp_replace("value", '[''"]+', '', 'gi') as "value"
        from "lowercase"
    ),
    -- replaces anything that's not a letter, number, hyphen('-'), or underscore('_') with an underscore('_')
    "separated" as (
        select regexp_replace("value", '[^a-z0-9\\-_]+', '_', 'gi') as "value"
        from "removed_quotes"
    ),
    -- trims hyphens('-') if they exist on the head or tail of the string
    "trimmed" as (
        select regexp_replace(regexp_replace("value", '\-+$', ''), '^\-', '') as "value"
        from "separated"
    )
select "value"
from "trimmed";
$$ language sql strict immutable;
