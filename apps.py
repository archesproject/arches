from django.apps import AppConfig

from arches.settings_utils import generate_frontend_configuration


class ArchesReferencesConfig(AppConfig):
    name = "arches_references"
    verbose_name = "Arches References"
    is_arches_application = True

    def ready(self):
        generate_frontend_configuration()
