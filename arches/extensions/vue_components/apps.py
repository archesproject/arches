from django.apps import AppConfig


class ArchesVueComponentsConfig(AppConfig):
    name = "arches.extensions.vue_components"
    # Pinned so that database tables, migration history and app_label-scoped
    # model references survive the move into arches.extensions.
    label = "arches_vue_components"
    is_arches_application = True
