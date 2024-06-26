from django.db import connection, migrations


def add_resource_instance_lifecycle_state_constraint(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE FUNCTION validate_resource_instance_lifecycle_state() RETURNS trigger AS $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM jsonb_each((SELECT states FROM resource_instance_lifecycles WHERE graph_id = NEW.graphid)) AS each
                    WHERE each.key = NEW.lifecycle_state
                ) THEN
                    RAISE EXCEPTION 'Invalid choice for lifecycle_state';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER verify_resource_instance_lifecycle_state_trigger
            BEFORE INSERT OR UPDATE ON resource_instances
            FOR EACH ROW
            EXECUTE FUNCTION validate_resource_instance_lifecycle_state();
        """
        )


def remove_resource_instance_lifecycle_state_constraint(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            DROP TRIGGER IF EXISTS verify_resource_instance_lifecycle_state_trigger ON resource_instances;
            DROP FUNCTION IF EXISTS validate_resource_instance_lifecycle_state();
        """
        )


def add_initial_resource_instance_lifecycle_state_constraint(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE FUNCTION validate_initial_resource_instance_lifecycle_state_constraint() RETURNS TRIGGER AS $$
            DECLARE
                resource_instance_lifecycle_initial_state_count INTEGER;
            BEGIN
                SELECT COUNT(*) INTO resource_instance_lifecycle_initial_state_count
                FROM jsonb_each(NEW.states) AS each
                WHERE each.value->>'initial_state' = 'true';
                
                IF resource_instance_lifecycle_initial_state_count != 1 THEN
                    RAISE EXCEPTION 'Exactly one initial_state must be true';
                END IF;
                
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER check_initial_resource_instance_lifecycle_state
            BEFORE INSERT OR UPDATE ON resource_instance_lifecycles
            FOR EACH ROW
            EXECUTE FUNCTION validate_initial_resource_instance_lifecycle_state_constraint();
        """
        )


def remove_initial_resource_instance_lifecycle_state_constraint(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            DROP TRIGGER IF EXISTS check_initial_resource_instance_lifecycle_state ON resource_instance_lifecycles;
            DROP FUNCTION IF EXISTS validate_initial_resource_instance_lifecycle_state_constraint();
        """
        )


class Migration(migrations.Migration):

    dependencies = [
        ("models", "11042_add_resource_instance_lifecycle"),
    ]

    operations = [
        migrations.RunPython(
            add_resource_instance_lifecycle_state_constraint,
            remove_resource_instance_lifecycle_state_constraint,
        ),
        migrations.RunPython(
            add_initial_resource_instance_lifecycle_state_constraint,
            remove_initial_resource_instance_lifecycle_state_constraint,
        ),
    ]
