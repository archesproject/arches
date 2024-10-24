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
        # Removes unnecessary files
        self.stdout.write("Removing unnecessary files...")

        for file_to_delete in [
            ".frontend-configuration-settings.json",
            ".tsconfig-paths.json",
        ]:
            if os.path.exists(os.path.join(settings.APP_ROOT, "..", file_to_delete)):
                self.stdout.write("Deleting {}".format(file_to_delete))
                os.remove(os.path.join(settings.APP_ROOT, "..", file_to_delete))

        self.stdout.write("Done!")

        # Updates webpack
        self.stdout.write("Creating updated webpack directory...")

        if os.path.isdir(os.path.join(settings.APP_ROOT, "..", "webpack")):
            shutil.rmtree(
                os.path.join(settings.APP_ROOT, "..", "webpack"), ignore_errors=True
            )

        shutil.copytree(
            os.path.join(settings.ROOT_DIR, "install", "arches-templates", "webpack"),
            os.path.join(settings.APP_ROOT, "..", "webpack"),
        )

        self.stdout.write("Done!")

        # Replaces tsconfig.json
        self.stdout.write("Updating tsconfig.json...")

        if os.path.exists(os.path.join(settings.APP_ROOT, "..", "tsconfig.json")):
            os.remove(os.path.join(settings.APP_ROOT, "..", "tsconfig.json"))

        shutil.copy2(
            os.path.join(
                settings.ROOT_DIR, "install", "arches-templates", "tsconfig.json"
            ),
            os.path.join(settings.APP_ROOT, "..", "tsconfig.json"),
        )

        self.stdout.write("Done!")
