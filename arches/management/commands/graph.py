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
            """
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

    def handle(self, *args, **options):
        if options["graphs"]:
            graphs = [Graph(graphid.strip()) for graphid in options["graphs"].split(",")]
        else:
            graphs = Graph.objects.filter(isresource=True)

        if options["operation"] == "publish":
            self.publish(options["username"], graphs)

        if options["operation"] == "unpublish":
            self.unpublish(graphs)

    def publish(self, username, graphs=None):
        user = User.objects.get(username=username)
        print("\nPublishing ...")
        for graph in graphs:
            print(graph.name)
            graph.publish(user)

    def unpublish(self, graphs=None):
        print("Unpublishing...")
        for graph in graphs:
            print(graph.name)
            graph.unpublish()
