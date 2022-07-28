import json
from django.db import migrations
from arches.app.models.fields.i18n import I18n_String, I18n_JSON


class Migration(migrations.Migration):
    dependencies = [
        ("models", "8400_remove_collector_references"),
    ]

    def change_i18n_null_values_to_empty_string(apps, schema_editor):
        def _update_cards(apps):
            CardModel = apps.get_model("models", "CardModel")

            for card in CardModel.objects.all():
                has_updated_attribute = False

                for attribute_name in ['name', 'description', 'instructions', 'helptitle', 'helptext']:
                    attribute = getattr(card, attribute_name)
                    i18n_dict = json.loads(attribute.value)

                    has_updated_value = False
                    
                    for key in i18n_dict.keys():
                        if i18n_dict[key] is None:
                            i18n_dict[key] = ""
                            has_updated_value = True

                    if has_updated_value:
                        setattr(card, attribute_name, I18n_String(i18n_dict))
                        has_updated_attribute = True

                if has_updated_attribute:
                    card.save()


        def _update_cards_x_nodes_x_widgets(apps):
            CardXNodeXWidget = apps.get_model("models", "CardXNodeXWidget")

            for card_x_node_x_widget in CardXNodeXWidget.objects.all():
                config = json.loads(card_x_node_x_widget.config.value)
                i18n_properties = config.get('i18n_properties')

                if i18n_properties:
                    has_updated_config = False

                    for attribute_name in i18n_properties:
                        i18n_dict = config[attribute_name]

                        has_updated_value = False
                    
                        for key in i18n_dict.keys():
                            if i18n_dict[key] is None:
                                i18n_dict[key] = ""
                                has_updated_value = True

                        if has_updated_value:
                            config[attribute_name] = i18n_dict
                            has_updated_config = True

                    if has_updated_config:
                        setattr(card_x_node_x_widget, 'config', I18n_JSON(config))
                        card_x_node_x_widget.save()


        _update_cards(apps)
        _update_cards_x_nodes_x_widgets(apps)

    def undo_change_i18n_null_values_to_empty_string(apps, schema_editor):
        pass

    operations = [
        migrations.RunPython(change_i18n_null_values_to_empty_string, reverse_code=undo_change_i18n_null_values_to_empty_string),
    ]
