import os
import shutil

from django.core.management.base import BaseCommand
from arches.app.models.system_settings import settings


class Command(BaseCommand):  # pragma: no cover
    """
    Command for migrating projects between versions

    """

    def handle(self, *args, **options):
        answer = input(
            "This operation will upgrade your project to version 8.0\n" "Continue? "
        )

        if answer.lower() in ["y", "yes"]:
            self.update_to_v8()
        else:
            self.stdout.write("Operation aborted.")

    def update_to_v8(self):
        # Replaces vitest config files
        self.stdout.write("Updating vitest configuration files...")

        for config_file in [
            "vitest.config.mts",
            "vitest.setup.mts",
        ]:
            self.stdout.write("Copying {} to project directory".format(config_file))
            shutil.copy2(
                os.path.join(
                    settings.ROOT_DIR, "install", "arches-templates", config_file
                ),
                os.path.join(settings.APP_ROOT, ".."),
            )

        self.stdout.write("Done!")

        # Removes unnecessary files
        self.stdout.write("Removing unnecessary files...")

        declarations_test_file_path = os.path.join(
            settings.APP_ROOT, "src", settings.APP_NAME, "declarations.test.ts"
        )

        if os.path.exists(declarations_test_file_path):
            self.stdout.write("Deleting {}".format("declarations.test.ts"))
            os.remove(declarations_test_file_path)

        self.stdout.write("Done!")
