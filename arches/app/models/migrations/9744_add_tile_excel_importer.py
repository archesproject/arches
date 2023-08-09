from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '9746_related_resource_post_save_bug'),
    ]

    forward_sql =  """
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
            'b96b8078-23b7-484f-b9d0-8ca304a5f7b6',
            'Tile Excel Exporter',
            'Import a Tile Excel file from Arches',
            'import',
            'views/components/etl_modules/tile-excel',
            'tile-excel',
            'tile_excel.py',
            'ImportTileExcel',
            '{"bgColor": "#f5c60a", "circleColor": "#f9dd6c"}',
            'fa fa-upload',
            'tile-excel-importer',
            6,
            'tile-excel-importer-help');
        """

    reverse_sql = """
        DELETE FROM load_staging WHERE loadid IN (SELECT loadid FROM load_event WHERE etl_module_id = 'b96b8078-23b7-484f-b9d0-8ca304a5f7b6');
        DELETE FROM load_event WHERE etl_module_id = 'b96b8078-23b7-484f-b9d0-8ca304a5f7b6';
        DELETE FROM etl_modules WHERE etlmoduleid = 'b96b8078-23b7-484f-b9d0-8ca304a5f7b6';
    """

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql),
    ]
