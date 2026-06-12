from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("arches_controlled_lists", "0010_arches_82_migration"),
    ]

    add_migrate_to_reference_datatype = """
        INSERT INTO etl_modules (
            etlmoduleid,
            name,
            description,
            etl_type,
            component,
            componentname,
            modulename,
            classname,
            config,
            reversible,
            icon,
            slug,
            helpsortorder,
            helptemplate
        )
        VALUES (
            'b0d3c7e0-7b6f-4a4e-8c8c-1f8a3b9d4d20',
            'Migrate to Reference Datatype',
            'Rewrite tile data on nodes already retyped to the reference datatype but still holding legacy concept or domain values.',
            'edit',
            'views/components/etl_modules/migrate-to-reference-datatype',
            'migrate-to-reference-datatype',
            'migrate_to_reference_datatype.py',
            'MigrateToReferenceDatatype',
            '{ "bgColor": "#1f8af7", "circleColor": "#7fc4ff", "show": true }',
            true,
            'fa fa-exchange',
            'migrate-to-reference-datatype',
            10,
            'migrate-to-reference-datatype-help'
        )
    """
    remove_migrate_to_reference_datatype = """
        DELETE FROM load_errors WHERE loadid IN (
            SELECT loadid FROM load_event WHERE etl_module_id = 'b0d3c7e0-7b6f-4a4e-8c8c-1f8a3b9d4d20'
        );
        DELETE FROM load_staging WHERE loadid IN (
            SELECT loadid FROM load_event WHERE etl_module_id = 'b0d3c7e0-7b6f-4a4e-8c8c-1f8a3b9d4d20'
        );
        DELETE FROM load_event WHERE etl_module_id = 'b0d3c7e0-7b6f-4a4e-8c8c-1f8a3b9d4d20';
        DELETE FROM etl_modules WHERE etlmoduleid = 'b0d3c7e0-7b6f-4a4e-8c8c-1f8a3b9d4d20';
    """

    operations = [
        migrations.RunSQL(
            add_migrate_to_reference_datatype,
            remove_migrate_to_reference_datatype,
        ),
    ]
