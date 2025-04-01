import arches

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
            "This operation will upgrade your project to version 8.0\n"
            "This will replace the following files in your project:\n"
            "  - .github/workflows/main.yml\n"
            "  - webpack/webpack-utils/build-filepath-lookup.js\n"
            "  - webpack/webpack.common.js\n"
            "  - webpack/webpack.config.dev.js\n"
            "  - webpack/webpack.config.prod.js\n"
            "Continue? "
        )

        if answer.lower() in ["y", "yes"]:
            self.update_to_v8()
        else:
            self.stdout.write("Operation aborted.")

    def update_to_v8(self):
        # Updates webpack config files
        if os.path.isdir(os.path.join(settings.APP_ROOT, "..", "webpack")):
            self.stdout.write("Removing previous webpack directory...")
            shutil.rmtree(
                os.path.join(settings.APP_ROOT, "..", "webpack"), ignore_errors=True
            )
            self.stdout.write("Done!")

        self.stdout.write("Creating updated webpack directory at project root...")
        shutil.copytree(
            os.path.join(settings.ROOT_DIR, "install", "arches-templates", "webpack"),
            os.path.join(settings.APP_ROOT, "..", "webpack"),
        )
        self.stdout.write("Done!")

        # Updates github workflows
        self.stdout.write("Copying .github/workflows/main.yml directory to project...")

        os.makedirs(
            os.path.join(settings.APP_ROOT, "..", ".github", "workflows"),
            exist_ok=True,
        )

        shutil.copy(
            os.path.join(
                settings.ROOT_DIR,
                "install",
                "arches-templates",
                ".github",
                "workflows",
                "main.yml",
            ),
            os.path.join(settings.APP_ROOT, "..", ".github", "workflows", "main.yml"),
        )
        self.stdout.write("Done!")

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

        # Interpolates variables
        self.stdout.write("Interpolating copied files...")

        arches_semantic_version = ".".join(
            [str(arches.VERSION[0]), str(arches.VERSION[1]), str(arches.VERSION[2])]
        )
        arches_next_minor_version = ".".join(
            [str(arches.VERSION[0]), str(arches.VERSION[1] + 1), "0"]
        )

        for relative_file_path in [
            os.path.join("..", ".github/workflows/main.yml"),
        ]:  # relative to app root directory
            try:
                file = open(os.path.join(settings.APP_ROOT, relative_file_path), "r")
                file_data = file.read()
                file.close()

                updated_file_data = (
                    file_data.replace(
                        "{{ project_name_title_case }}",
                        settings.APP_NAME.title().replace("_", ""),
                    )
                    .replace("{{ project_name }}", settings.APP_NAME)
                    .replace("{{ arches_semantic_version }}", arches_semantic_version)
                    .replace(
                        "{{ arches_next_minor_version }}", arches_next_minor_version
                    )
                )

                file = open(os.path.join(settings.APP_ROOT, relative_file_path), "w")
                file.write(updated_file_data)
                file.close()
            except FileNotFoundError:
                pass

        self.stdout.write("Done!")
        self.stdout.write("Project successfully updated to version 8.0")
