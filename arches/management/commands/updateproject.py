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
        """
        This will replace the following files in your project:
        .babelrc, eslintrc.js, .eslintignore, .browserslistrc, .stylelintrc.json, 
        nodemon.json and tsconfig.json, and the entire webpack directory.
        
        Continue?
        """
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

        arches_template_webpack_path = os.path.join(settings.ROOT_DIR, "install", "arches-templates", "project_name", "webpack")

        if os.path.exists(arches_template_webpack_path):
            shutil.copytree(arches_template_webpack_path, project_webpack_path)

        # copy dotfiles
        for dotfile in [".eslintrc.js", ".eslintignore", ".babelrc", ".browserslistrc", ".stylelintrc.json"]:
            dotfile_path = os.path.join(settings.ROOT_DIR, "install", "arches-templates", "project_name", dotfile)
            if os.path.exists(arches_template_webpack_path):

                print("Copying {} to project root directory".format(dotfile))
                shutil.copy2(dotfile_path, settings.APP_ROOT)

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
        # ensure project has a `messages.pot` file
        for dotfile in [
            "nodemon.json", "tsconfig.json", ".babelrc", ".browserslistrc", ".eslintignore", ".eslintrc.js", ".stylelintrc.json", "LICENSE", "MANIFEST.in", "pyproject.toml"
        ]:
            if os.path.exists(os.path.join(settings.APP_ROOT, dotfile)):
                print("Deleting {} from project sub-directory".format(dotfile))
                os.remove(os.path.join(settings.APP_ROOT, dotfile))

            print("Copying {} to project root directory".format(dotfile))
            shutil.copy2(os.path.join(settings.ROOT_DIR, "install", "arches-templates", dotfile), os.path.join(settings.APP_ROOT, '..'))

        for file in [".yarnrc", "yarn.lock"]:
            if os.path.exists(os.path.join(settings.APP_ROOT, file)):
                print("Ensuring {} is deleted from project sub-directory".format(file))
                os.remove(os.path.join(settings.APP_ROOT, file))

        if os.path.isdir(os.path.join(settings.APP_ROOT, 'media', 'node_modules')):
            print("Removing media/node_modules directory")
            shutil.rmtree(os.path.join(settings.APP_ROOT, 'media', 'node_modules'), ignore_errors=True)
    
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
            print("Copying gettext config to project root directory")
            shutil.copy2(os.path.join(settings.ROOT_DIR, "install", "arches-templates", "gettext.config.js"), os.path.join(settings.APP_ROOT, '..'))

        if os.path.isdir(os.path.join(settings.APP_ROOT, 'webpack')):
            print("Removing previous webpack directory")
            shutil.rmtree(os.path.join(settings.APP_ROOT, 'webpack'), ignore_errors=True)

        if os.path.isdir(os.path.join(settings.APP_ROOT, '..', 'webpack')):
            print("Root-level webpack directory detected! Removing...")
            shutil.rmtree(os.path.join(settings.APP_ROOT, '..', 'webpack'), ignore_errors=True)

        print("Creating updated webpack directory at root")
        shutil.copytree(os.path.join(settings.ROOT_DIR, "install", "arches-templates", "webpack"), os.path.join(settings.APP_ROOT, '..', 'webpack'))
        
