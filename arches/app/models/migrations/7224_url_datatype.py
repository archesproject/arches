from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7131_update_annotations_view"),
    ]

    operations = [
        migrations.RunSQL(
            """
            INSERT INTO public.d_data_types(
                datatype, iconclass, modulename, classname, configcomponent, defaultconfig, configname, isgeometric, defaultwidget, issearchable)
            VALUES (
                'url','fa fa-location-arrow','url.py','URLDataType','views/components/datatypes/url',null,'url-datatype-config',
                false,'ca0c43ff-af73-4349-bafd-53ff9f22eebd',true);

            INSERT INTO public.widgets(
            widgetid, name, component, defaultconfig, helptext, datatype)
            VALUES ('ca0c43ff-af73-4349-bafd-53ff9f22eebd','urldatatype','views/components/widgets/urldatatype',
                '{
                    "url_placeholder": "Enter URL... ",
                    "url_label_placeholder": "Enter URL Label... ",
                    "link_color": "#0055a0"
                }',null,'url');
            """,
            """
            DELETE FROM public.widgets
            WHERE widgetid = 'ca0c43ff-af73-4349-bafd-53ff9f22eebd';

            DELETE FROM public.d_data_types
            WHERE datatype = 'url';
            """,
        )
    ]
