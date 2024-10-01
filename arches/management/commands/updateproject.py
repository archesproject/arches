# pragma: no cover

import arches
import os
import shutil

from django.core.management.base import BaseCommand
from django.core import management
from django.db import connection
from arches.app.models.system_settings import settings


class Command(BaseCommand):  # pragma: no cover
    """
    Command for migrating projects between versions

    """

    def handle(self, *args, **options):
        answer = input(
            "This will replace the following files in your project:\n"
            ".babelrc, eslintrc.js, .eslintignore, .browserslistrc, .stylelintrc.json,\n"
            ".yarnrc, .gitattributes, nodemon.json, .prettierrc,\n"
            ".pre-commit-config.yaml, tsconfig.json, and the entire webpack directory.\n\n"
            "Continue? "
        )

        if answer.lower() in ["y", "yes"]:
            self.update_to_v7()
            self.update_to_v7_5()
            self.update_to_v7_6()
        else:
            self.stdout.write("Operation aborted.")

    def update_to_v7(self):
        # copy webpack config files to project
        self.stdout.write("Copying webpack directory to project root directory")
        project_webpack_path = os.path.join(settings.APP_ROOT, "webpack")

        if os.path.exists(project_webpack_path):
            shutil.rmtree(project_webpack_path)

        arches_template_webpack_path = os.path.join(
            settings.ROOT_DIR, "install", "arches-templates", "project_name", "webpack"
        )

        if os.path.exists(arches_template_webpack_path):
            shutil.copytree(arches_template_webpack_path, project_webpack_path)

        # ensure project has a `media/img` directory
        if not os.path.isdir(os.path.join(settings.APP_ROOT, "media", "img")):
            self.stdout.write("Creating /media/img directory")
            os.mkdir(os.path.join(settings.APP_ROOT, "media", "img"))

        #  check if temp_graph_status table exists
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM 
                        pg_tables
                    WHERE 
                        schemaname = 'public' AND 
                        tablename  = 'temp_graph_status'
                );
                """
            )
            result = cursor.fetchone()

            # publish graphs that were previously active
            if result[0]:  # parses result from row
                cursor.execute("select * from temp_graph_status;")
                rows = cursor.fetchall()
                graphs = []
                for row in rows:
                    graphid = str(row[0])
                    active = row[1]
                    if active:
                        graphs.append(graphid)
                management.call_command(
                    "graph",
                    operation="publish",
                    update_instances=True,
                    graphs=",".join(graphs),
                )
                cursor.execute("drop table if exists temp_graph_status")

    def update_to_v7_5(self):
        # Republish to pick up CardsXNodeXWidget changes from
        # migration 10150_add_default_value_file_list.py
        management.call_command("graph", operation="publish", update=True)
        self.stdout.write("Publishing finished! \n\n")

    def update_to_v7_6(self):
        path_to_possible_outermost_init = os.path.normpath(
            os.path.join(settings.APP_ROOT, "..", "__init__.py")
        )
        if os.path.exists(path_to_possible_outermost_init):
            os.remove(path_to_possible_outermost_init)

        for file_to_delete in [".eslintrc.js", ".eslintignore", ".yarnrc", "yarn.lock"]:
            if os.path.exists(os.path.join(settings.APP_ROOT, file_to_delete)):
                self.stdout.write(
                    "Deleting {} from project root directory".format(file_to_delete)
                )
                os.remove(os.path.join(settings.APP_ROOT, file_to_delete))

        if os.path.exists(os.path.join(settings.APP_ROOT, "media", "node_modules")):
            self.stdout.write("Deleting node_modules folder from media directory")
            shutil.rmtree(os.path.join(settings.APP_ROOT, "media", "node_modules"))

        for project_metadata_file in ["LICENSE", "MANIFEST.in", "pyproject.toml"]:
            if os.path.exists(
                os.path.join(settings.APP_ROOT, "..", project_metadata_file)
            ):
                if project_metadata_file == "pyproject.toml":
                    self.stderr.write(
                        "Existing pyproject.toml detected. "
                        "Manually reconcile existing file with new template.",
                    )
            else:
                self.stdout.write(
                    "Copying {} to project directory".format(project_metadata_file)
                )
                shutil.copy2(
                    os.path.join(
                        settings.ROOT_DIR,
                        "install",
                        "arches-templates",
                        project_metadata_file,
                    ),
                    os.path.join(settings.APP_ROOT, ".."),
                )

        for config_file in [
            "nodemon.json",
            "tsconfig.json",
            ".coveragerc",
            ".gitattributes",
            ".babelrc",
            ".browserslistrc",
            ".stylelintrc.json",
            "gettext.config.js",
            "vitest.config.mts",
            "vitest.setup.mts",
            "eslint.config.mjs",
            ".prettierrc",
            ".pre-commit-config.yaml",
        ]:
            if os.path.exists(os.path.join(settings.APP_ROOT, config_file)):
                self.stdout.write(
                    "Deleting {} from project root directory".format(config_file)
                )
                os.remove(os.path.join(settings.APP_ROOT, config_file))

            self.stdout.write("Copying {} to project directory".format(config_file))
            shutil.copy2(
                os.path.join(
                    settings.ROOT_DIR, "install", "arches-templates", config_file
                ),
                os.path.join(settings.APP_ROOT, ".."),
            )

        if os.path.exists(
            os.path.join(settings.APP_ROOT, "..", ".github", "workflows", "main.yml")
        ):
            self.stderr.write(
                "Existing .github/workflows/main.yml detected. "
                "Manually reconcile existing file with new template.",
            )
        else:
            self.stdout.write("Copying .github/workflows/main.yml directory to project")

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
                os.path.join(
                    settings.APP_ROOT, "..", ".github", "workflows", "main.yml"
                ),
            )

        for action_name in ["build-and-test-branch", "install-arches-applications"]:
            if os.path.exists(
                os.path.join(
                    settings.APP_ROOT,
                    "..",
                    ".github",
                    "actions",
                    action_name,
                    "action.yml",
                )
            ):
                self.stderr.write(
                    f"Existing .github/workflows/{action_name}.yml detected. "
                    + "Manually reconcile existing file with new template.",
                )
            else:
                self.stdout.write(
                    f"Copying .github/actions/{action_name}/action.yml directory to project"
                )

                os.makedirs(
                    os.path.join(
                        settings.APP_ROOT, "..", ".github", "actions", action_name
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
                        action_name,
                        "action.yml",
                    ),
                    os.path.join(
                        settings.APP_ROOT,
                        "..",
                        ".github",
                        "actions",
                        action_name,
                        "action.yml",
                    ),
                )

        if os.path.exists(os.path.join(settings.APP_ROOT, "..", "tests")):
            self.stderr.write(
                "Existing tests directory detected. "
                "Manually reconcile existing file with new template."
            )
        else:
            self.stdout.write("Copying tests directory to project")
            test_directory_path = os.path.join(settings.APP_ROOT, "..", "tests")

            shutil.copytree(
                os.path.join(settings.ROOT_DIR, "install", "arches-templates", "tests"),
                test_directory_path,
            )

            for dirpath, dirnames, filenames in os.walk(test_directory_path):
                for filename in filenames:
                    if filename.endswith(".py-tpl"):
                        os.rename(
                            os.path.join(dirpath, filename),
                            os.path.join(dirpath, filename[:-7] + ".py"),
                        )

        if os.path.isfile(os.path.join(settings.APP_ROOT, "hosts.py")):
            self.stderr.write(
                "Existing hosts.py detected. "
                "Manually reconcile existing file with new template."
            )
        else:
            self.stdout.write("Copying hosts.py to project directory")
            shutil.copy2(
                os.path.join(
                    settings.ROOT_DIR,
                    "install",
                    "arches-templates",
                    "project_name",
                    "hosts.py-tpl",
                ),
                settings.APP_ROOT,
            )
            os.rename(
                os.path.join(settings.APP_ROOT, "hosts.py-tpl"),
                os.path.join(settings.APP_ROOT, "hosts.py-tpl"[:-7] + ".py"),
            )

        if os.path.isfile(os.path.join(settings.APP_ROOT, "apps.py")):
            self.stderr.write(
                "Existing apps.py detected. Manually reconcile existing file with new template.",
            )
        else:
            self.stdout.write("Copying apps.py to project root")
            shutil.copy2(
                os.path.join(
                    settings.ROOT_DIR,
                    "install",
                    "arches-templates",
                    "project_name",
                    "apps.py-tpl",
                ),
                settings.APP_ROOT,
            )
            os.rename(
                os.path.join(settings.APP_ROOT, "apps.py-tpl"),
                os.path.join(settings.APP_ROOT, "apps.py"),
            )

        if os.path.isfile(
            os.path.join(settings.APP_ROOT, "search_indexes", "sample_index.py")
        ):
            self.stderr.write(
                "Existing sample_index.py detected. Skipping creation of sample_index.py",
            )
        else:
            self.stdout.write(
                f"Creating /{settings.APP_NAME}/search_indexes/sample_index.py"
            )
            src_path = os.path.join(settings.APP_ROOT, "search_indexes")
            if not os.path.isdir(src_path):
                os.mkdir(src_path)

            shutil.copy2(
                os.path.join(
                    settings.ROOT_DIR,
                    "install",
                    "arches-templates",
                    "project_name",
                    "search_indexes",
                    "sample_index.py",
                ),
                src_path,
            )
            self.stdout.write(
                f"Creating /{settings.APP_NAME}/search_indexes/__init__.py"
            )
            shutil.copy2(
                os.path.join(
                    settings.ROOT_DIR,
                    "install",
                    "arches-templates",
                    "project_name",
                    "search_indexes",
                    "__init__.py",
                ),
                src_path,
            )

        if os.path.isfile(
            os.path.join(
                settings.APP_ROOT, "src", settings.APP_NAME, "declarations.d.ts"
            )
        ):
            self.stderr.write(
                "Existing declarations.d.ts detected. Manually reconcile existing file with new template.",
            )
        else:
            self.stdout.write(f"Creating /src/{settings.APP_NAME}/declarations.d.ts")
            src_path = os.path.join(settings.APP_ROOT, "src")
            src_project_subdir = os.path.join(src_path, settings.APP_NAME)
            if not os.path.isdir(src_path):
                os.mkdir(src_path)
            if not os.path.isdir(src_project_subdir):
                os.mkdir(src_project_subdir)

            shutil.copy2(
                os.path.join(
                    settings.ROOT_DIR,
                    "install",
                    "arches-templates",
                    "project_name",
                    "src",
                    "project_name",
                    "declarations.d.ts",
                ),
                os.path.join(settings.APP_ROOT, "src", settings.APP_NAME),
            )
            self.stdout.write(f"Creating /src/{settings.APP_NAME}/declarations.test.ts")
            shutil.copy2(
                os.path.join(
                    settings.ROOT_DIR,
                    "install",
                    "arches-templates",
                    "project_name",
                    "src",
                    "project_name",
                    "declarations.test.ts",
                ),
                os.path.join(settings.APP_ROOT, "src", settings.APP_NAME),
            )

        if not os.path.isfile(
            os.path.join(settings.APP_ROOT, "locale", "messages.pot")
        ):
            self.stdout.write("Creating /locale/messages.pot")
            if not os.path.isdir(os.path.join(settings.APP_ROOT, "locale")):
                os.mkdir(os.path.join(settings.APP_ROOT, "locale"))

            open(os.path.join(settings.APP_ROOT, "locale", "messages.pot"), "w").close()

        if os.path.isdir(os.path.join(settings.APP_ROOT, "webpack")):
            self.stdout.write("Non-root-level webpack directory detected! Removing...")
            shutil.rmtree(
                os.path.join(settings.APP_ROOT, "webpack"), ignore_errors=True
            )

        if os.path.isdir(os.path.join(settings.APP_ROOT, "..", "webpack")):
            self.stdout.write("Removing previous webpack directory")
            shutil.rmtree(
                os.path.join(settings.APP_ROOT, "..", "webpack"), ignore_errors=True
            )

        self.stdout.write("Creating updated webpack directory at project root")
        shutil.copytree(
            os.path.join(settings.ROOT_DIR, "install", "arches-templates", "webpack"),
            os.path.join(settings.APP_ROOT, "..", "webpack"),
        )

        # updates all instances of `{{ project_name }}` with project name
        arches_semantic_version = ".".join(
            [str(arches.VERSION[0]), str(arches.VERSION[1]), str(arches.VERSION[2])]
        )
        arches_next_minor_version = ".".join(
            [str(arches.VERSION[0]), str(arches.VERSION[1] + 1), "0"]
        )

        for relative_file_path in [
            os.path.join("..", "gettext.config.js"),
            os.path.join("..", ".coveragerc"),
            os.path.join("..", ".github/workflows/main.yml"),
            os.path.join("..", ".pre-commit-config.yaml"),
            os.path.join("..", "tsconfig.json"),
            os.path.join("..", "tests/test_settings.py"),
            os.path.join("..", "tests/search_indexes/sample_index_tests.py"),
            os.path.join("..", "pyproject.toml"),
            os.path.join("..", "vitest.config.mts"),
            os.path.join("..", "vitest.setup.mts"),
            "hosts.py",
            "apps.py",
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
