import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "9068_resource_model_view_defaults"),
    ]

    add_bulk_data_editor = """
        DELETE FROM load_staging WHERE loadid IN (SELECT loadid FROM load_event WHERE etl_module_id = '6d0e7625-5792-4b83-b14b-82f603913706');
        DELETE FROM load_event WHERE etl_module_id = '6d0e7625-5792-4b83-b14b-82f603913706';
        DELETE FROM etl_modules WHERE etlmoduleid = '6d0e7625-5792-4b83-b14b-82f603913706';

        INSERT INTO etl_modules(
            etlmoduleid,name,description,etl_type,component,componentname,modulename,classname,config,icon,slug
        )
        VALUES
            (
                '80fc7aab-cbd8-4dc0-b55b-5facac4cd157',
                'Bulk Data Editor - Trim',
                'Remove Leading and Training Spaces',
                'edit',
                'views/components/etl_modules/bulk-trim-editor',
                'bulk-trim-editor',
                'base_data_editor.py',
                'BaseDataEDitor',
                '{"bgColor": "#7EC8E3", "circleColor": "#AEC6CF", "show": true}',
                'fa fa-edit',
                'bulk-trim-editor'
            ),
            (
                'e4169b44-124a-4ff6-bd11-5521901f98a7',
                'Bulk Data Editor - Captalize',
                'Capitalize the First Letter of Every Words (Title Case)',
                'edit',
                'views/components/etl_modules/bulk-capitalize-editor',
                'bulk-capitalize-editor',
                'base_data_editor.py',
                'BaseDataEDitor',
                '{"bgColor": "#7EC8E3", "circleColor": "#AEC6CF", "show": true}',
                'fa fa-edit',
                'bulk-capitalize-editor'
            ),
            (
                '5bd600f0-0896-46fa-a224-8602ebf45048',
                'Bulk Data Editor - Upper Case',
                'Convert All the Words into Upper Case',
                'edit',
                'views/components/etl_modules/bulk-uppercase-editor',
                'bulk-uppercase-editor',
                'base_data_editor.py',
                'BaseDataEDitor',
                '{"bgColor": "#7EC8E3", "circleColor": "#AEC6CF", "show": true}',
                'fa fa-edit',
                'bulk-uppercase-editor'
            ),
            (
                '11e3cf3e-8530-43c2-9eb4-e7bf7aa00f17',
                'Bulk Data Editor - Lower Case',
                'Convert All the Words into Lower Case',
                'edit',
                'views/components/etl_modules/bulk-lowercase-editor',
                'bulk-lowercase-editor',
                'base_data_editor.py',
                'BaseDataEDitor',
                '{"bgColor": "#7EC8E3", "circleColor": "#AEC6CF", "show": true}',
                'fa fa-edit',
                'bulk-lowercase-editor'
            ),
            (
                '9079b83c-e22b-4fdc-a22e-74487ee7b7f3',
                'Bulk Data Editor - Replace',
                'Replace All the Matching Words with a New Word',
                'edit',
                'views/components/etl_modules/bulk-replace-editor',
                'bulk-replace-editor',
                'base_data_editor.py',
                'BaseDataEDitor',
                '{"bgColor": "#7EC8E3", "circleColor": "#AEC6CF", "show": true}',
                'fa fa-edit',
                'bulk-replace-editor'
            );
    """
    remove_bulk_data_editor = """
        DELETE FROM load_staging WHERE loadid IN (SELECT loadid FROM load_event WHERE etl_module_id IN (
            '80fc7aab-cbd8-4dc0-b55b-5facac4cd157',
            'e4169b44-124a-4ff6-bd11-5521901f98a7',
            '5bd600f0-0896-46fa-a224-8602ebf45048',
            '11e3cf3e-8530-43c2-9eb4-e7bf7aa00f17',
            '9079b83c-e22b-4fdc-a22e-74487ee7b7f3'
        ));
        DELETE FROM load_event WHERE etl_module_id IN (
            '80fc7aab-cbd8-4dc0-b55b-5facac4cd157',
            'e4169b44-124a-4ff6-bd11-5521901f98a7',
            '5bd600f0-0896-46fa-a224-8602ebf45048',
            '11e3cf3e-8530-43c2-9eb4-e7bf7aa00f17',
            '9079b83c-e22b-4fdc-a22e-74487ee7b7f3'
        );
        DELETE FROM etl_modules WHERE etlmoduleid IN (
            '80fc7aab-cbd8-4dc0-b55b-5facac4cd157',
            'e4169b44-124a-4ff6-bd11-5521901f98a7',
            '5bd600f0-0896-46fa-a224-8602ebf45048',
            '11e3cf3e-8530-43c2-9eb4-e7bf7aa00f17',
            '9079b83c-e22b-4fdc-a22e-74487ee7b7f3'
        );

        INSERT INTO etl_modules(
            etlmoduleid,name,description,etl_type,component,componentname,modulename,classname,config,icon,slug
        )
        VALUES (
            '6d0e7625-5792-4b83-b14b-82f603913706',
            'Bulk Data Editor',
            'Edit Existing Data in Arches',
            'edit',
            'views/components/etl_modules/bulk-data-editor',
            'bulk-data-editor',
            'bulk_data_editor.py',
            'BulkDataEditor',
            '{"bgColor": "#7EC8E3", "circleColor": "#AEC6CF", "show": true}',
            'fa fa-edit',
            'bulk-data-editor'
        );
    """
    operations = [
        migrations.RunSQL(
            add_bulk_data_editor,
            remove_bulk_data_editor,
        )
    ]
