import arches
import os
import shutil

from django.core.management.base import BaseCommand
from django.core import management
from django.db import connection
from arches.app.models.system_settings import settings


class Command(BaseCommand):
    """
    Command for migrating projects between versions

    """

    def handle(self, *args, **options):
        answer = input(
            "This will replace the following files in your project:\n"
            ".babelrc, eslintrc.js, .eslintignore, .browserslistrc, .stylelintrc.json,\n"
            ".yarnrc, .gitignore, nodemon.json and tsconfig.json, and the entire webpack directory.\n\n"
            "Continue? "
        )
        
        if answer.lower() in ["y","yes"]:
            self.update_to_v7()
            self.update_to_v7_5()
            self.update_to_v7_6()
        else:
            print("Operation aborted.")

    def update_to_v7(self):
        # copy webpack config files to project
        print("Copying webpack directory to project root directory")
        project_webpack_path = os.path.join(settings.APP_ROOT, "webpack")

        if os.path.exists(project_webpack_path):
            shutil.rmtree(project_webpack_path)

        shutil.copytree(os.path.join(settings.ROOT_DIR, "install", "arches-templates", "project_name", "webpack"), project_webpack_path)

        # ensure project has a `media/img` directory
        if not os.path.isdir(os.path.join(settings.APP_ROOT, "media", "img")):
            print("Creating /media/img directory")
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
                management.call_command("graph", operation="publish", update_instances=True, graphs=",".join(graphs))
                cursor.execute("drop table if exists temp_graph_status")

    def update_to_v7_5(self):
        # Republish to pick up CardsXNodeXWidget changes from
        # migration 10150_add_default_value_file_list.py
        management.call_command("graph", operation="publish", update=True)

    def update_to_v7_6(self):
        for dotfile in [".eslintrc.js", ".eslintignore", ".babelrc", ".browserslistrc", ".stylelintrc.json", ".yarnrc"]:
            previous_dotfile_path = os.path.join(settings.APP_ROOT, dotfile)
            if os.path.exists(previous_dotfile_path):
                print("Deleting {} from project root directory".format(dotfile))
                os.remove(previous_dotfile_path)

            print("Copying {} to project directory".format(dotfile))
            shutil.copy2(os.path.join(settings.ROOT_DIR, "install", "arches-templates", dotfile), os.path.join(settings.APP_ROOT, ".."))

        for config_file in ["nodemon.json", "tsconfig.json", ".coveragerc", ".gitignore"]:
            print("Copying {} to project directory".format(config_file))
            shutil.copy2(os.path.join(settings.ROOT_DIR, "install", "arches-templates", config_file), os.path.join(settings.APP_ROOT, ".."))

        if not os.path.exists(os.path.join(settings.APP_ROOT, "..", ".github")):
            print("Copying .github directory to project")
            shutil.copytree(os.path.join(settings.ROOT_DIR, "install", "arches-templates", ".github"), os.path.join(settings.APP_ROOT, "..", ".github"))
    
        if not os.path.exists(os.path.join(settings.APP_ROOT, "..", "tests")):
            print("Copying tests directory to project")
            test_directory_path = os.path.join(settings.APP_ROOT, "..", "tests")

            shutil.copytree(os.path.join(settings.ROOT_DIR, "install", "arches-templates", "tests"), test_directory_path)

            for dirpath, dirnames, filenames in os.walk(test_directory_path):
                for filename in filenames:
                    if filename.endswith('.py-tpl'):
                        os.rename(
                            os.path.join(dirpath, filename), 
                            os.path.join(dirpath, filename[:-7] + '.py')
                    )

        if not os.path.isfile(os.path.join(settings.APP_ROOT, "install", "requirements_dev.txt")):
            print("Copying requirements_dev.txt to project install directory")
            shutil.copy2(os.path.join(settings.ROOT_DIR, "install", "arches-templates", "project_name", "install", "requirements_dev.txt"), os.path.join(settings.APP_ROOT, 'install'))
    
        if not os.path.isfile(os.path.join(settings.APP_ROOT, "src", "declarations.d.ts")):
            print("Creating /src/declarations.d.ts")
            if not os.path.isdir(os.path.join(settings.APP_ROOT, "src")):
                os.mkdir(os.path.join(settings.APP_ROOT, "src"))

            shutil.copy2(os.path.join(settings.ROOT_DIR, "install", "arches-templates", "project_name", "src", "declarations.d.ts"), os.path.join(settings.APP_ROOT, 'src'))

        if not os.path.isfile(os.path.join(settings.APP_ROOT, "locale", "messages.pot")):
            print("Creating /locale/messages.pot")
            if not os.path.isdir(os.path.join(settings.APP_ROOT, "locale")):
                os.mkdir(os.path.join(settings.APP_ROOT, "locale"))

            open(os.path.join(settings.APP_ROOT, "locale", "messages.pot"), 'w').close()

        if not os.path.isfile(os.path.join(settings.APP_ROOT, "gettext.config.js")):
            print("Copying gettext config to project directory")
            shutil.copy2(os.path.join(settings.ROOT_DIR, "install", "arches-templates", "gettext.config.js"), os.path.join(settings.APP_ROOT, '..'))

        # updates all instances of `{{ project_name }}` with project name
        path_to_project = os.path.join(settings.APP_ROOT, "..")
        for relative_file_path in [
            '.coveragerc', '.gitignore', "tsconfig.json", ".yarnrc", "tests/test_settings.py", "tests/search_indexes/sample_index_tests.py"
        ]:  # relative to app root directory
            try:
                file = open(os.path.join(path_to_project, relative_file_path),'r')
                file_data = file.read()
                file.close()

                updated_file_data = (
                    file_data.replace("{{ project_name }}", settings.APP_NAME)
                )

                file = open(os.path.join(path_to_project, relative_file_path),'w')
                file.write(updated_file_data)
                file.close()
            except FileNotFoundError:
                pass

