from django.db import migrations, models


class Migration(migrations.Migration):
    """Creates the ledger table for package migrations.

    PackageMigrationRecorder queries this table through a floating model on its
    own Apps() registry, the way Django's MigrationRecorder does, so the table is
    invisible to makemigrations and has to be declared here by hand.

    Unlike django_migrations it is NOT self-bootstrapped by ensure_schema():
    django_migrations can be, only because its three columns are frozen. This
    one will gain columns, and ensure_schema() has no concept of altering an
    existing table.
    """

    dependencies = [
        ("models", "12779_add_multicard_resource_descriptor"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE arches_package_migrations (
                id bigserial PRIMARY KEY,
                app varchar(255) NOT NULL,
                name varchar(255) NOT NULL,
                applied timestamp with time zone NOT NULL,
                from_publication uuid NULL,
                to_publication uuid NULL,
                resume_cursor jsonb NULL,
                touched_graphs jsonb NULL,
                CONSTRAINT unique_arches_package_migration UNIQUE (app, name)
            );
            """,
            reverse_sql="DROP TABLE arches_package_migrations;",
        ),
    ]
