import arches

import os
import shutil

from django.core.management.base import BaseCommand
from arches.app.models.system_settings import settings

from arches.app.models.system_settings import settings


class Command(BaseCommand):  # pragma: no cover
    """
    Command for migrating projects between versions

    """

    def handle(self, *args, **options):
        answer = input(
            "This operation will upgrade your project to version 8.0\n"
            "This will replace the following files in your project:\n"
            "  - <project>/apps.py\n"
            "  - .github/actions/build-and-test-branch/action.yml\n"
            "  - .github/workflows/main.yml\n"
            "  - tsconfig.json\n"
            "  - vitest.config.mts\n"
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
        # Removes:
        #   `.frontend-configuration-settings.json`
        #   `.tsconfig-paths.json`
        #   `declarations.test.ts`
        for file_to_delete in [
            ".frontend-configuration-settings.json",
            ".tsconfig-paths.json",
        ]:
            if os.path.exists(os.path.join(settings.APP_ROOT, "..", file_to_delete)):
                self.stdout.write("Deleting {}".format(file_to_delete))
                os.remove(os.path.join(settings.APP_ROOT, "..", file_to_delete))
                self.stdout.write("Done!")

        declarations_test_file_path = os.path.join(
            settings.APP_ROOT, "src", settings.APP_NAME, "declarations.test.ts"
        )

        if os.path.exists(declarations_test_file_path):
            self.stdout.write("Deleting {}".format("declarations.test.ts"))
            os.remove(declarations_test_file_path)
            self.stdout.write("Done!")

        # Update apps.py to remove generate_frontend_configuration
        to_replace_1 = """
from django.conf import settings

from arches.settings_utils import generate_frontend_configuration"""

        to_replace_2 = """
    def ready(self):
        if settings.APP_NAME.lower() == self.name:
            generate_frontend_configuration()"""

        with open(
            os.path.join(settings.APP_ROOT, "apps.py"), "r", encoding="utf-8"
        ) as f:
            apps_file_content = f.read()
        with open(
            os.path.join(settings.APP_ROOT, "apps.py"), "w", encoding="utf-8"
        ) as f:
            new_content = apps_file_content.replace(to_replace_1, "").replace(
                to_replace_2, ""
            )
            f.write(new_content)

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

        # Replaces vitest.config.mts
        self.stdout.write("Updating vitest.config.mts...")

        if os.path.exists(os.path.join(settings.APP_ROOT, "..", "vitest.config.mts")):
            os.remove(os.path.join(settings.APP_ROOT, "..", "vitest.config.mts"))

        shutil.copy2(
            os.path.join(
                settings.ROOT_DIR, "install", "arches-templates", "vitest.config.mts"
            ),
            os.path.join(settings.APP_ROOT, "..", "vitest.config.mts"),
        )
        self.stdout.write("Done!")

        # Updates github workflows
        self.stdout.write(
            "Copying .github/actions/build-and-test-branch/action.yml directory to project..."
        )

        os.makedirs(
            os.path.join(
                settings.APP_ROOT, "..", ".github", "actions", "build-and-test-branch"
            ),
            exist_ok=True,
        )

        shutil.copy(
            os.path.join(
                settings.ROOT_DIR,
                "install",
                "arches-templates",
                ".github",
                "actions",
                "build-and-test-branch",
                "action.yml",
            ),
            os.path.join(
                settings.APP_ROOT,
                "..",
                ".github",
                "actions",
                "build-and-test-branch",
                "action.yml",
            ),
        )
        self.stdout.write("Done!")

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
