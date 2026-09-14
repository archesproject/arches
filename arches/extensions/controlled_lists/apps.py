from django.apps import AppConfig, apps


class ArchesControlledListsConfig(AppConfig):
    name = "arches_controlled_lists"
    verbose_name = "Arches Controlled Lists"
    is_arches_application = True

    def ready(self):
        if apps.get_app_config("arches_querysets"):
            from arches_controlled_lists.datatypes.datatypes import (
                ReferenceField,
                ReferenceSerializer,
            )
            from arches_querysets.rest_framework.serializers import (
                TileAliasedDataSerializer,
            )

            TileAliasedDataSerializer.register_custom_datatype_field(
                ReferenceField, ReferenceSerializer
            )
