from django.apps import AppConfig, apps


class ArchesControlledListsConfig(AppConfig):
    name = "arches.extensions.controlled_lists"
    # Pinned so that database tables, migration history and app_label-scoped
    # model references survive the move into arches.extensions.
    label = "arches_controlled_lists"
    verbose_name = "Arches Controlled Lists"
    is_arches_application = True

    def ready(self):
        if apps.get_app_config("arches_querysets"):
            from arches.extensions.controlled_lists.datatypes.datatypes import (
                ReferenceField,
                ReferenceSerializer,
            )
            from arches.extensions.querysets.rest_framework.serializers import (
                TileAliasedDataSerializer,
            )

            TileAliasedDataSerializer.register_custom_datatype_field(
                ReferenceField, ReferenceSerializer
            )
