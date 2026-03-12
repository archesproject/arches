import arches

import os
import shutil

from django.core import management
from django.core.management.base import BaseCommand
from arches.app.models.system_settings import settings

from arches.app.models.system_settings import settings


class Command(BaseCommand):  # pragma: no cover
    """
    Command for migrating projects between versions

    """

    def handle(self, *args, **options):
        answer = input(
            "This operation will upgrade your project to version 8.1\n"
            "This will replace the following files in your project:\n"
            "  - <project>/apps.py\n"
            "  - .github/actions/build-and-test-branch/action.yml\n"
            "  - .github/dependabot.yml\n"
            "  - .github/workflows/main.yml\n"
            "  - eslint.config.mjs\n"
            "  - tsconfig.json\n"
            "  - vitest.config.mts\n"
            "  - webpack/webpack-utils/build-filepath-lookup.js\n"
            "  - webpack/webpack.common.js\n"
            "  - webpack/webpack.config.dev.js\n"
            "  - webpack/webpack.config.prod.js\n"
            "Continue? "
        )

        if answer.lower() in ["y", "yes"]:
            self.update_to_v8_1()
        else:
            self.stdout.write("Operation aborted.")

    def update_to_v8_1(self):
        self.stdout.write("Updating project to version 8.1...")

        # Replaces eslint.config.mjs
        self.stdout.write("Updating eslint.config.mjs...")

        if os.path.exists(os.path.join(settings.APP_ROOT, "..", "eslint.config.mjs")):
            os.remove(os.path.join(settings.APP_ROOT, "..", "eslint.config.mjs"))

        shutil.copy2(
            os.path.join(
                settings.ROOT_DIR, "install", "arches-templates", "eslint.config.mjs"
            ),
            os.path.join(settings.APP_ROOT, "..", "eslint.config.mjs"),
        )
        self.stdout.write("Done!")

        # Adds .github/dependabot.yml
        self.stdout.write("Copying .github/dependabot.yml to project...")
        shutil.copy(
            os.path.join(
                settings.ROOT_DIR,
                "install",
                "arches-templates",
                ".github",
                "dependabot.yml",
            ),
            os.path.join(settings.APP_ROOT, "..", ".github", "dependabot.yml"),
        )
        self.stdout.write("Done!")

        self.stdout.write("Project successfully updated to version 8.1")
