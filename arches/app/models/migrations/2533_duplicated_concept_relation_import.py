# -*- coding: utf-8 -*-


import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '0010_4_1_0'),
    ]

    operations = [
            migrations.RunSQL("""
                CREATE OR REPLACE FUNCTION public.__arches_check_dup_relations(
                	p_conceptid1 uuid,
                	p_conceptid2 uuid,
                	p_relationtype text)
                    RETURNS text
                    LANGUAGE 'plpgsql'

                    COST 100
                    VOLATILE

                AS $BODY$

                declare
                v_return text;

                BEGIN
                    IF
                        (	SELECT count(*) from relations
                            WHERE 1=1
                             AND conceptidfrom = p_conceptid1
                             AND conceptidto = p_conceptid2
                             AND relationtype = p_relationtype ) > 0
                         THEN v_return = 'duplicate';

                     ELSIF
                        (	SELECT count(*) from relations
                            WHERE 1=1
                             AND conceptidfrom = p_conceptid2
                             AND conceptidto = p_conceptid1
                             AND relationtype = p_relationtype ) > 0
                         THEN v_return = 'duplicate';

                     ELSE v_return = 'unique';

                    END IF;

                RETURN v_return;

                END;

                $BODY$;


                CREATE OR REPLACE RULE relations_check_insert AS ON INSERT TO relations
                    WHERE (select * from __arches_check_dup_relations(new.conceptidfrom,new.conceptidto,new.relationtype)) = 'duplicate'
                    DO INSTEAD NOTHING;

                CREATE OR REPLACE RULE relations_check_update AS ON UPDATE TO relations
                    WHERE (select * from __arches_check_dup_relations(new.conceptidfrom,new.conceptidto,new.relationtype)) = 'duplicate'
                    DO INSTEAD NOTHING;
                """,

                """
                    DROP RULE relations_check_insert ON relations;

                    DROP rule relations_check_update ON relations;

                    DROP FUNCTION public.__arches_check_dup_relations(
                	p_conceptid1 uuid,
                	p_conceptid2 uuid,
                	p_relationtype text);
                """),
    ]
