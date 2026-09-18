"""Write a graph's JSON into the package that owns it.

This is the analogue of editing models.py. You author a graph in the Graph
Designer, export it here, and the committed JSON becomes the desired state that
makepkgmigrations diffs against, which is what lets generation run without a
database and produce the same migration on every machine.
"""

import json
import os

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from arches.app.models import models


class Command(BaseCommand):
    help = "Exports a published graph to its Arches application's pkg/graphs directory."

    def add_arguments(self, parser):
        parser.add_argument("app_label", help="Arches application that owns the graph.")
        parser.add_argument("graph", help="Graph slug or id.")

    def handle(self, *args, **options):
        app_config = apps.get_app_config(options["app_label"])
        if not getattr(app_config, "is_arches_application", False):
            raise CommandError(
                "'%s' is not an Arches application." % options["app_label"]
            )

        graph = self._graph(options["graph"])
        if graph.has_unpublished_changes:
            raise CommandError(
                "Graph '%s' has unpublished changes. Publish it before exporting, "
                "or the exported JSON will not match any publication."
                % options["graph"]
            )

        published = graph.get_published_graph()
        if published is None:
            raise CommandError(
                "Graph '%s' has never been published." % options["graph"]
            )

        # Same shape `packages -o load_package` reads, so exporting keeps the
        # package installable. makepkgmigrations projects it in memory.
        archesfile = {"graph": [published.serialized_graph]}
        path = self._path(app_config, graph)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as destination:
            json.dump(archesfile, destination, indent=4, sort_keys=True)
            destination.write("\n")

        if options["verbosity"] >= 1:
            self.stdout.write("Wrote %s" % os.path.relpath(path))

    def _graph(self, identifier):
        graph = models.GraphModel.objects.filter(slug=identifier).first()
        if graph is None:
            graph = models.GraphModel.objects.filter(pk=identifier).first()
        if graph is None:
            raise CommandError("No graph found for '%s'." % identifier)
        if graph.source_identifier_id:
            raise CommandError("'%s' is a draft graph." % identifier)
        return graph

    def _path(self, app_config, graph):
        # The on-disk layout load_package already globs: it looks for these two
        # literal subdirectories and only WARNS when they are absent, so a flat
        # pkg/graphs/<slug>.json would silently import nothing.
        subdirectory = "resource_models" if graph.isresource else "branches"
        return os.path.join(
            app_config.path,
            "pkg",
            "graphs",
            subdirectory,
            "%s.json" % (graph.slug or graph.graphid),
        )
