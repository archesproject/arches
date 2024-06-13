from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "9748_alter_graphmodel_functions_alter_icon_id"),
    ]

    forward_sql = """
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
            'Import Tile Excel',
            'Import a Tile Excel file to Arches',
            'import',
            'views/components/etl_modules/tile-excel-importer',
            'tile-excel-importer',
            'tile_excel_importer.py',
            'TileExcelImporter',
            '{"bgColor": "#f5c60a", "circleColor": "#f9dd6c"}',
            'fa fa-upload',
            'tile-excel-importer',
            6,
            'tile-excel-importer-help');

        UPDATE etl_modules SET
        	description = 'Loads resource data in Branch Excel format',
            component = 'views/components/etl_modules/branch-excel-importer',
            componentname = 'branch-excel-importer',
            modulename = 'branch_excel_importer.py',
            classname = 'BranchExcelImporter',
            slug = 'branch-excel-importer',
            helptemplate = 'import-branch-excel-help'
        WHERE etlmoduleid = '3b19a76a-0b09-450e-bee1-65accb096eaf';
    """

    reverse_sql = """
        DELETE FROM load_errors WHERE loadid IN (SELECT loadid FROM load_event WHERE etl_module_id = 'b96b8078-23b7-484f-b9d0-8ca304a5f7b6');
        DELETE FROM load_staging WHERE loadid IN (SELECT loadid FROM load_event WHERE etl_module_id = 'b96b8078-23b7-484f-b9d0-8ca304a5f7b6');
        DELETE FROM load_event WHERE etl_module_id = 'b96b8078-23b7-484f-b9d0-8ca304a5f7b6';
        DELETE FROM etl_modules WHERE etlmoduleid = 'b96b8078-23b7-484f-b9d0-8ca304a5f7b6';
        UPDATE etl_modules SET
        	description = 'Loads resource data in branch excel format',
		    component = 'views/components/etl_modules/branch-csv-importer',
		    componentname = 'branch-csv-importer',
		    modulename = 'branch_csv_importer.py',
		    classname = 'BranchCsvImporter',
		    slug = 'branch-csv-importer',
		    helptemplate = 'import-branch-csv-help'
        WHERE etlmoduleid = '3b19a76a-0b09-450e-bee1-65accb096eaf';
    """

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql),
    ]
