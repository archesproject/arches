import arches
from django.core.management.base import BaseCommand
from django.core import management
from django.db import connection


class Command(BaseCommand):
    """
    Command for migrating projects between versions

    """

    def handle(self, *args, **options):
        if "7.0.0" in arches.__version__:
            self.update_to_v7()

    def update_to_v7(self):
        with connection.cursor() as cursor:
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
