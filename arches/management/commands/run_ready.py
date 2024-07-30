import importlib
import os
from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings


class Command(BaseCommand):
    help = "Runs the ready method of the project-level AppConfig"

    def handle(self, *args, **kwargs):
        for app_config in apps.get_app_configs():
            if (
                app_config.name == settings.APP_NAME
                or app_config.verbose_name == settings.APP_NAME
            ):
                self.stdout.write(f"Running ready method for {app_config.name}")
                try:
                    app_config.ready()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully ran ready method for {app_config.name}"
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error running ready method for {app_config.name}: {str(e)}"
                        )
                    )
