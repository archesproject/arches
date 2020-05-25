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

from arches.app.models.graph import Graph
from arches.app.models.system_settings import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from arches.app.utils.betterJSONSerializer import JSONSerializer


class Command(BaseCommand):
    """
    Commands for caching models

    """

    def add_arguments(self, parser):
        parser.add_argument("operation", nargs="?", help="operation 'livereload' starts livereload for this project on port 35729")

    def handle(self, *args, **options):
        if options["operation"] == "graphs":
            self.cache_graphs()

        if options["operation"] == "verify_cache":
            self.verify_cache()

        if options["operation"] == "clear":
            self.clear()

    def clear(self):
        cache.clear()

    def cache_graphs(self):
        graphs = Graph.objects.all()
        for graph in graphs:
            print("caching", graph.name)
            cache.set(f"graph_{graph.graphid}", JSONSerializer().serializeToPython(graph), settings.GRAPH_MODEL_CACHE_TIMEOUT)

    def verify_cache(self):
        graphs = Graph.objects.all()
        for graph in graphs:
            graphc = cache.get(f"graph_{graph.graphid}")
            graph_from_cache = JSONSerializer().serialize(graphc)
            graph_from_db = JSONSerializer().serialize(graph)
            print(f"Cache for {graph.name} is valid: {len(graph_from_cache) == len(graph_from_db)}")
