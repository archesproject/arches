from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "4921_file_data_type"),
    ]

    operations = [
        migrations.RunSQL(
            """create or replace function TileBBox (z int, x int, y int, srid int = 3857)
                returns geometry
                language plpgsql immutable as
            $func$
            declare
                max numeric := 20037508.34;
                res numeric := (max*2)/(2^z);
                bbox geometry;
            begin
                bbox := ST_MakeEnvelope(
                    -max + (x * res),
                    max - (y * res),
                    -max + (x * res) + res,
                    max - (y * res) - res,
                    3857
                );
                if srid = 3857 then
                    return bbox;
                else
                    return ST_Transform(bbox, srid);
                end if;
            end;
            $func$;""",
            reverse_sql="drop function if exists TileBBox(z int, x int, y int, srid int) restrict;",
            elidable=False,
        ),
    ]
