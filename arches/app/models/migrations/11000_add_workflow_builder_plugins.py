from django.db import migrations

add_wb_plugin = """
    INSERT INTO plugins (
        pluginid,
        name,
        icon,
        component,
        componentname,
        config,
        slug,
        sortorder)
    VALUES (
        '577a8b37-c092-49b0-adb0-17e87d648e7f',
        'Workflow Builder',
        'fa fa-folder-open',
        'views/components/plugins/workflow-builder',
        'workflow-builder',
        '{"show": true}',
        'workflow-builder',
        0);
"""

remove_wb_plugin = """
    DELETE FROM PLUGINS WHERE pluginid = '577a8b37-c092-49b0-adb0-17e87d648e7f';
"""

add_wb_editor_plugin = """
    INSERT INTO plugins (
        pluginid,
        name,
        icon,
        component,
        componentname,
        config,
        slug,
        sortorder)
    VALUES (
        'b10573c9-dbb2-4834-9677-cc3844c192d0',
        'Workflow Builder Editor',
        'fa fa-folder-open',
        'views/components/plugins/workflow-builder-editor',
        'workflow-builder-editor',
        '{"show": false}',
        'workflow-builder-editor',
        0);
"""

remove_wb_editor_plugin = """
    DELETE FROM PLUGINS WHERE pluginid = 'b10573c9-dbb2-4834-9677-cc3844c192d0';
"""


class Migration(migrations.Migration):
    dependencies = [("migrations", "10999_update_principaluser")]

    operations = [
        migrations.RunSQL(
            add_wb_plugin,
            remove_wb_plugin,
        )
    ]
