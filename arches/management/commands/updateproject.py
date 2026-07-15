import arches
import os
import re
import shutil

from django.core.management.base import BaseCommand
from arches.app.models.system_settings import settings


class Command(BaseCommand):  # pragma: no cover
    """
    Command for migrating projects between versions

    """

    def handle(self, *args, **options):
        answer = input(
            "This operation will upgrade your project to version 8.2\n"
            "This will replace the following files in your project:\n"
            "  - .github/dependabot.yml\n"
            "  - eslint.config.mjs\n"
            "This will also delete your project's entire webpack/ directory and recreate it "
            "from scratch, including:\n"
            "  - webpack/webpack-utils/build-filepath-lookup.js\n"
            "  - webpack/webpack-utils/patch-vue-compiler-sfc-type-resolution.js\n"
            "  - webpack/webpack.common.js\n"
            "  - webpack/webpack.config.dev.js\n"
            "  - webpack/webpack.config.prod.js\n"
            "Any other files you've added under webpack/ will be lost.\n"
            "Continue? "
        )

        if answer.lower() in ["y", "yes"]:
            self.update_to_v8_1()
            self.update_to_v8_2()
        else:
            self.stdout.write("Operation aborted.")

    def update_to_v8_2(self):
        self.stdout.write("Updating project to version 8.2...")

        project_root = os.path.join(settings.APP_ROOT, "..")

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

        self._update_ci_workflow(project_root)

        self.stdout.write("Project successfully updated to version 8.2")

    def _update_ci_workflow(self, project_root):
        workflow_path = os.path.join(project_root, ".github", "workflows", "main.yml")
        if not os.path.exists(workflow_path):
            self.stdout.write(".github/workflows/main.yml not found, skipping...")
            return

        self.stdout.write("Updating CI Python version matrix...")

        with open(workflow_path) as f:
            content = f.read()

        content = re.sub(
            r'(python-version:\s*\[)[^\]]*"3\.11"[^\]]*\]',
            'python-version: ["3.12", "3.13", "3.14"]',
            content,
        )

        with open(workflow_path, "w") as f:
            f.write(content)

        self.stdout.write("Done!")

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

        self.stdout.write("Project successfully updated to version 8.1")
