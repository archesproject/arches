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
        self.update_to_v7()

    def update_to_v7(self):
        # copy webpack config files to project
        print("Copying webpack directory to project root directory")
        project_webpack_path = os.path.join(settings.APP_ROOT, "webpack")

        if os.path.exists(project_webpack_path):
            shutil.rmtree(project_webpack_path)

        shutil.copytree(os.path.join(settings.ROOT_DIR, "install", "arches-templates", "project_name", "webpack"), project_webpack_path)

        # copy dotfiles
        for dotfile in [".eslintrc.js", ".eslintignore", ".babelrc", ".browserslistrc", ".stylelintrc.json"]:
            print("Copying {} to project root directory".format(dotfile))
            shutil.copy2(os.path.join(settings.ROOT_DIR, dotfile), settings.APP_ROOT)

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
