"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from django.core.management.base import BaseCommand
from arches.app.models.graph import Graph
from django.contrib.auth.models import User
from django.db import connection


class Command(BaseCommand):
    """
    Commands for adding arches test users

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "operation",
            nargs="?",
            choices=[
                "publish",
                "unpublish",
            ],
            help="""
            Operation Type
              'publish' publishes resource models indicated using the --graphs arg.
              'unpublish' unpublishes resource models indicated using the --graphs arg.
               Both publish and unpublish apply to all resource models if a --graphs value is not provided",
            """,
        )
        parser.add_argument(
            "-g",
            "--graphs",
            action="store",
            dest="graphs",
            default=False,
            help="A comma separated list of graphids to which an operation will be applied.",
        )
        parser.add_argument(
            "-u",
            "--username",
            action="store",
            dest="username",
            default="admin",
            help="A username required for the publication of graphs.",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            dest="update",
            help="This will update PublishedGraph instances without creating a new GraphPublication.",
        )
        parser.add_argument(
            "-ui",
            "--update_instances",
            action="store_true",
            dest="update_instances",
            help="Do you want to assign new graph publication ids to all corresponding resource instances?",
        )

    def handle(self, *args, **options):
        if options["graphs"]:
            self.graphs = [
                Graph(graphid.strip()) for graphid in options["graphs"].split(",")
            ]
        else:
            self.graphs = Graph.objects.filter(isresource=True)

        self.update_instances = True if options["update_instances"] else False
        self.update = True if options["update"] else False

        if options["operation"] == "publish":
            self.publish(options["username"])

        if options["operation"] == "unpublish":
            self.unpublish()

    def publish(self, username):
        user = User.objects.get(username=username)
        print("\nPublishing ...")
        graphids = []
        for graph in self.graphs:
            print(graph.name)

            if self.update:
                if graph.publication_id:
                    graph.update_published_graphs()
            else:
                graph.publish(user)

            graphids.append(str(graph.pk))
        if self.update_instances:
            graphids = tuple(graphids)
            with connection.cursor() as cursor:
                cursor.execute(
                    "update resource_instances r set graphpublicationid = publicationid from graphs g where r.graphid = g.graphid and g.graphid in %s;",
                    (graphids,),
                )

    def unpublish(self):
        print("Unpublishing...")
        for graph in self.graphs:
            print(graph.name)
            graph.unpublish()
