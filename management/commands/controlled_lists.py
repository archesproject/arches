from arches.app.models.fields.i18n import I18n_JSONField
from arches.app.models.models import (
    CardXNodeXWidget,
    GraphModel,
    Language,
    Node,
    Value,
    Widget,
)
from arches.app.models.graph import Graph
from arches_references.models import List
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction
from django.db.models.expressions import CombinedExpression
from django.db.models.fields.json import KT
from django.db.models.functions import Cast


class Command(BaseCommand):
    """
    Commands for running controlled list operations

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--operation",
            action="store",
            dest="operation",
            required=True,
            choices=[
                "migrate_collections_to_controlled_lists",
                "migrate_concept_nodes_to_reference_datatype",
            ],
            help="The operation to perform",
        )

        parser.add_argument(
            "-co",
            "--collections",
            action="store",
            dest="collections_to_migrate",
            nargs="*",
            help="One or more collections to migrate to controlled lists",
        )

        parser.add_argument(
            "-ho",
            "--host",
            action="store",
            dest="host",
            default="http://localhost:8000/plugins/controlled-list-manager/item/",
            help="Provide a host for URI generation. Default is localhost",
        )

        parser.add_argument(
            "-ow",
            "--overwrite",
            action="store_true",
            dest="overwrite",
            default=False,
            help="Overwrite the entire controlled list and its list items/values. Default false.",
        )

        parser.add_argument(
            "-psl",
            "--preferred_sort_language",
            action="store",
            dest="preferred_sort_language",
            default="en",
            help="The language to use for sorting preferred labels. Default 'en'",
        )

        parser.add_argument(
            "-g",
            "--graph",
            action="store",
            dest="graph",
            help="The graphid which associated concept nodes will be migrated to use the reference datatype",
        )

    def handle(self, *args, **options):
        if options["operation"] == "migrate_collections_to_controlled_lists":
            psl = options["preferred_sort_language"]
            try:
                Language.objects.get(code=psl)
            except Language.DoesNotExist:
                raise CommandError(
                    "The preferred sort language, {0}, does not exist in the database.".format(
                        psl
                    )
                )

            if options["collections_to_migrate"] is None:
                raise CommandError("No collections provided to migrate.")

            if not options["overwrite"]:
                for collection_name in options["collections_to_migrate"]:
                    if List.objects.filter(name=collection_name).exists():
                        raise CommandError(
                            f"The collection '{collection_name}' already exists."
                        )

            self.migrate_collections_to_controlled_lists(
                collections_to_migrate=options["collections_to_migrate"],
                host=options["host"],
                overwrite=options["overwrite"],
                preferred_sort_language=psl,
            )
        elif options["operation"] == "migrate_concept_nodes_to_reference_datatype":
            self.migrate_concept_nodes_to_reference_datatype(options["graph"])

    def migrate_collections_to_controlled_lists(
        self,
        collections_to_migrate,
        host,
        overwrite,
        preferred_sort_language,
    ):
        """
        Uses a postgres function to migrate collections to controlled lists

        Example usage:
            python manage.py controlled_lists
                -o migrate_collections_to_controlled_lists
                -co 'Johns list' 'Getty AAT'
                -ho 'http://localhost:8000/plugins/controlled-list-manager/item/'
                -psl 'fr'
                -ow

            for collections that contain an apostrophe, wrap the concept in double quotes, e.g. "John''s list"

        """

        collections_in_db = list(
            Value.objects.filter(
                value__in=collections_to_migrate,
                valuetype__in=["prefLabel", "identifier"],
                concept__nodetype="Collection",
            ).values_list("value", flat=True)
        )

        failed_collections = [
            collection
            for collection in collections_to_migrate
            if collection not in collections_in_db
        ]

        if len(failed_collections) > 0:
            self.stderr.write(
                "Failed to find the following collections in the database: %s"
                % ", ".join(failed_collections)
            )

        if len(collections_in_db) > 0:
            from django.db import connection

            cursor = connection.cursor()
            cursor.execute(
                """
                select * from __arches_migrate_collections_to_clm(
                    ARRAY[%s], %s, %s::boolean, %s
                );
                """,
                [collections_in_db, host, overwrite, preferred_sort_language],
            )
            result = cursor.fetchone()
            self.stdout.write(result[0])

    def migrate_concept_nodes_to_reference_datatype(self, graph_id):
        try:
            source_graph = GraphModel.objects.get(pk=graph_id)
        except (GraphModel.DoesNotExist, ValidationError) as e:
            raise CommandError(e)

        nodes = (
            Node.objects.filter(
                graph_id=source_graph.graphid,
                datatype__in=["concept", "concept-list"],
                is_immutable=False,
            )
            .annotate(
                collection_id=Cast(
                    KT("config__rdmCollection"),
                    output_field=models.UUIDField(),
                )
            )
            .prefetch_related("cardxnodexwidget_set")
        )

        if len(nodes) == 0:
            raise CommandError(
                "No concept/concept-list nodes found for the {0} graph".format(
                    source_graph.name
                )
            )

        REFERENCE_SELECT_WIDGET = Widget.objects.get(name="reference-select-widget")
        controlled_list_ids = List.objects.all().values_list("id", flat=True)

        errors = []
        with transaction.atomic():
            for node in nodes:
                if node.collection_id in controlled_list_ids:
                    if node.datatype == "concept":
                        node.config = {
                            "multiValue": False,
                            "controlledList": str(node.collection_id),
                        }
                    elif node.datatype == "concept-list":
                        node.config = {
                            "multiValue": True,
                            "controlledList": str(node.collection_id),
                        }
                    node.datatype = "reference"
                    node.full_clean()
                    node.save()

                    cross_records = (
                        node.cardxnodexwidget_set.annotate(
                            config_without_i18n=Cast(
                                models.F("config"),
                                output_field=models.JSONField(),
                            )
                        )
                        .annotate(
                            without_default=CombinedExpression(
                                models.F("config_without_i18n"),
                                "-",
                                models.Value(
                                    "defaultValue", output_field=models.CharField()
                                ),
                                output_field=models.JSONField(),
                            )
                        )
                        .annotate(
                            without_default_and_options=CombinedExpression(
                                models.F("without_default"),
                                "-",
                                models.Value(
                                    "options", output_field=models.CharField()
                                ),
                                output_field=I18n_JSONField(),
                            )
                        )
                    )
                    for cross_record in cross_records:
                        # work around for i18n as_sql method issue detailed here: https://github.com/archesproject/arches/issues/11473
                        cross_record.config = {}
                        cross_record.save()

                        cross_record.config = cross_record.without_default_and_options
                        cross_record.widget = REFERENCE_SELECT_WIDGET
                        cross_record.full_clean()
                        cross_record.save()

                elif node.collection_id not in controlled_list_ids:
                    errors.append(
                        {"node_alias": node.alias, "collection_id": node.collection_id}
                    )

        if errors:
            self.stderr.write(
                "The following collections for the associated nodes have not been migrated to controlled lists:"
            )
            for error in errors:
                self.stderr.write(
                    "Node alias: {0}, Collection ID: {1}".format(
                        error["node_alias"], error["collection_id"]
                    )
                )
        else:
            source_graph = Graph.objects.get(pk=graph_id)

            # Refresh the nodes to ensure the changes are reflected in the serialized graph
            for node in source_graph.nodes.values():
                node.refresh_from_db()

            source_graph.create_editable_future_graph()
            source_graph.publish(
                notes="Migrated concept/concept-list nodes to reference datatype"
            )

            self.stdout.write(
                "All concept/concept-list nodes for the {0} graph have been successfully migrated to reference datatype".format(
                    source_graph.name
                )
            )
