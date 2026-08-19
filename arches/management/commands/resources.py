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

from collections import defaultdict

from arches.management.commands import utils
from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.models.system_settings import settings
from django.core.management.base import BaseCommand
import arches.app.utils.data_management.resources.remover as resource_remover


class Command(BaseCommand):
    """
    Commands for managing Arches resources

    """

    help = (
        "Manage Arches resource instances.\n\n"
        "Operations:\n"
        "  remove_resources      Delete resource instances, optionally filtered by graph.\n"
        "  clear_edit_log        Truncate the edit log, optionally filtered by graph.\n"
        "  calculate_descriptors Recalculate and persist the name, description, and\n"
        "                        map_popup descriptors for resource instances without\n"
        "                        triggering an Elasticsearch (re)index.  Useful for\n"
        "                        correcting stale or missing descriptor values after a\n"
        "                        data migration.  Processes resources in batches and\n"
        "                        writes results back via a single bulk_update per batch.\n"
        "\n"
        "Examples:\n"
        "  # Recalculate descriptors for every resource (skips confirmation prompt):\n"
        "  python manage.py resources calculate_descriptors --yes\n"
        "\n"
        "  # Recalculate descriptors for one Resource Model only:\n"
        "  python manage.py resources calculate_descriptors -g <graph-uuid> --yes\n"
        "\n"
        "  # Recalculate descriptors only for resources touched in a given transaction:\n"
        "  python manage.py resources calculate_descriptors -t <transaction-uuid>\n"
        "\n"
        "  # Use a smaller batch size to reduce peak memory usage:\n"
        "  python manage.py resources calculate_descriptors --yes --batch-size 500\n"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "operation",
            nargs="?",
            help=(
                "Operation to perform. One of: "
                "'remove_resources', 'clear_edit_log', 'calculate_descriptors'."
            ),
        )

        parser.add_argument(
            "-y",
            "--yes",
            action="store_true",
            dest="yes",
            help='used to force a yes answer to any user input "continue? y/n" prompt',
        )

        parser.add_argument(
            "-g",
            "--graph",
            action="store",
            dest="graph",
            help=(
                "UUID of the Resource Model (graph) to filter by. "
                "For 'remove_resources': only instances of this graph are deleted. "
                "For 'calculate_descriptors': only resources of this graph have "
                "their descriptors recalculated."
            ),
        )

        parser.add_argument(
            "-e",
            "--editlog",
            action="store_true",
            dest="editlog",
            help="used to clear the edit log. If a graphid is provided, only the edit log for that graph will be cleared.",
        )

        parser.add_argument(
            "-t",
            "--transaction",
            action="store",
            dest="transaction",
            help="A transaction id to limit which resources have their descriptors recalculated.",
        )

        parser.add_argument(
            "-b",
            "--batch-size",
            action="store",
            dest="batch_size",
            type=int,
            default=2000,
            help="Number of resources to process per batch (default: 2000).",
        )

    def handle(self, *args, **options):
        if options["operation"] == "remove_resources":
            self.remove_resources(
                force=options["yes"],
                graphid=options["graph"],
                clear_edit_log=options["editlog"],
            )

        if options["operation"] == "clear_edit_log":
            self.clear_edit_log(graphid=options["graph"])

        if options["operation"] == "calculate_descriptors":
            self.calculate_descriptors(
                force=options["yes"],
                graphid=options["graph"],
                transaction_id=options["transaction"],
                batch_size=options["batch_size"],
            )

    def remove_resources(
        self, load_id="", graphid=None, force=False, clear_edit_log=False
    ):
        """
        Runs the resource_remover command found in data_management.resources
        """
        # resource_remover.delete_resources(load_id)
        if not force:
            if graphid is None:
                if not utils.get_yn_input("all resources will be removed. continue?"):
                    return
            else:
                if not utils.get_yn_input(
                    "All resources associated with the '%s' Resource Model will be removed. continue?"
                    % Graph.objects.get(graphid=graphid).name
                ):
                    return

        if graphid is None:
            resource_remover.clear_resources()
            if clear_edit_log:
                self.clear_edit_log()
        else:
            graph = Graph.objects.get(graphid=graphid)
            graph.delete_instances(verbose=True)
            if clear_edit_log:
                self.clear_edit_log(graphid)

        return

    def clear_edit_log(self, graphid=None):
        """
        Clears the edit log
        """
        if graphid:
            models.EditLog.objects.filter(resourceclassid=graphid).delete()
        else:
            models.EditLog.objects.all().delete()

    def calculate_descriptors(
        self, transaction_id=None, graphid=None, force=False, batch_size=2000
    ):
        """
        Recalculates and bulk-saves resource descriptors (name, description, map_popup).

        Groups resources by graph to fetch descriptor functions once per graph,
        pre-fetches tiles per batch, and writes back via bulk_update to avoid
        per-resource round-trips to the database.
        """
        from arches.app.models.resource import Resource

        resources = Resource.objects.all()

        if transaction_id:
            resource_ids = list(
                models.EditLog.objects.filter(transactionid=transaction_id)
                .values_list("resourceinstanceid", flat=True)
                .distinct()
            )
            resources = resources.filter(resourceinstanceid__in=resource_ids)

        if graphid:
            resources = resources.filter(graph_id=graphid)

        total = resources.count()

        if total == 0:
            self.stdout.write(
                self.style.WARNING("No resources matched the given criteria.")
            )
            return

        elif not force:
            if not utils.get_yn_input(
                f"Descriptors for {total} resources will be recalculated. Continue?"
            ):
                return

        self.stdout.write(f"Processing descriptors for {total} resource(s)...")

        graph_ids = list(resources.values_list("graph_id", flat=True).distinct())
        descriptor_functions_by_graph = {}
        for graph_id in graph_ids:
            funcs = list(
                models.FunctionXGraph.objects.filter(
                    graph_id=graph_id, function__functiontype="primarydescriptors"
                ).select_related("function")
            )
            descriptor_functions_by_graph[str(graph_id)] = funcs

        descriptor_keys = ("name", "description", "map_popup")
        all_resource_ids = list(resources.values_list("resourceinstanceid", flat=True))
        updated = 0

        for batch_start in range(0, len(all_resource_ids), batch_size):
            batch_ids = all_resource_ids[batch_start : batch_start + batch_size]
            batch_resources = list(
                Resource.objects.filter(resourceinstanceid__in=batch_ids)
            )

            # Fetch all tiles for this batch in a single query
            tiles_by_resource = defaultdict(list)
            for tile in models.TileModel.objects.filter(
                resourceinstance_id__in=batch_ids
            ):
                tiles_by_resource[str(tile.resourceinstance_id)].append(tile)

            for resource in batch_resources:
                resource.tiles = tiles_by_resource.get(
                    str(resource.resourceinstanceid), []
                )
                descriptor_function = descriptor_functions_by_graph.get(
                    str(resource.graph_id), []
                )

                if resource.descriptors is None:
                    resource.descriptors = {}
                if resource.name is None:
                    resource.name = {}

                for lang in settings.LANGUAGES:
                    language = resource.get_descriptor_language({"language": lang[0]})
                    context = {"language": language}

                    if len(descriptor_function) == 1:
                        module = descriptor_function[0].function.get_class_module()()
                        for descriptor in descriptor_keys:
                            resource.descriptors[language][descriptor] = (
                                module.get_primary_descriptor_from_nodes(
                                    resource,
                                    descriptor_function[0].config["descriptor_types"][
                                        descriptor
                                    ],
                                    context,
                                    descriptor,
                                )
                            )
                            if (
                                descriptor == "name"
                                and resource.descriptors[language][descriptor]
                                is not None
                            ):
                                resource.name[language] = resource.descriptors[
                                    language
                                ][descriptor]
                    else:
                        for descriptor in descriptor_keys:
                            resource.descriptors[language][descriptor] = None

            Resource.objects.bulk_update(
                batch_resources, ["descriptors", "name"], batch_size=batch_size
            )
            updated += len(batch_resources)
            self.stdout.write(f"  {updated}/{total} resources updated...")

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully recalculated descriptors for {updated} resource(s)."
            )
        )
