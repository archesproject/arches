from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "10121_workflowhistory"),
    ]

    add_bulk_data_deletion = """
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
            icon,
            slug,
            helpsortorder,
            helptemplate)
        VALUES (
            'db0e9807-b254-458d-bd62-cfb1da21fe95',
            'Bulk Data Deletion',
            'Delete Existing Data in Arches',
            'edit',
            'views/components/etl_modules/bulk-data-deletion',
            'bulk-data-deletion',
            'bulk_data_deletion.py',
            'BulkDataDeletion',
            '{"bgColor": "#abc4ff", "circleColor": "#ccdbfd", "show": true}',
            'fa fa-trash',
            'bulk-data-deletion',
            6,
            'bulk-data-deletion-help');
        """
    remove_bulk_data_deletion = """
        DELETE FROM load_staging WHERE loadid IN (SELECT loadid FROM load_event WHERE etl_module_id = 'db0e9807-b254-458d-bd62-cfb1da21fe95');
        DELETE FROM load_event WHERE etl_module_id = 'db0e9807-b254-458d-bd62-cfb1da21fe95';
        DELETE FROM etl_modules WHERE etlmoduleid = 'db0e9807-b254-458d-bd62-cfb1da21fe95';
    """

    operations = [
        migrations.RunSQL(
            add_bulk_data_deletion,
            remove_bulk_data_deletion,
        )
    ]
