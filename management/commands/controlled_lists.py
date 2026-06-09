from urllib.parse import urlparse, urlunparse, urlsplit, urlunsplit
from django.core.management.base import BaseCommand, CommandError
from django.core import management
from django.db import connection, models, transaction
from django.db.models.expressions import CombinedExpression
from django.db.models.fields.json import KT
from django.db.models.functions import Cast
import uuid

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.fields.i18n import I18n_JSONField
from arches.app.models.graph import Graph
from arches.app.models.models import (
    Language,
    Node,
    Value,
    Widget,
)
from arches_controlled_lists.models import List, ListItem, ListItemValue


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
                "migrate_domain_nodes_to_controlled_lists",
                "change_url_base",
            ],
            help="The operation to perform",
        )

        parser.add_argument(
            "-li",
            "--lists",
            action="store",
            dest="lists",
            default=False,
            help="A comma separated list of the listids of the resources you would like to change the url base for.  If not provided, all controlled lists will be updated.",
        )

        parser.add_argument(
            "-co",
            "--collections",
            action="store",
            dest="collections_to_migrate",
            nargs="*",
            help="One or more collections to migrate to controlled lists. "
            "To migrate all collections, provide an empty string ('') as the only argument.",
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
            help="The graphid or slug which associated concept nodes will be migrated to use the reference datatype",
        )

        parser.add_argument(
            "-n",
            "--node-aliases",
            action="store",
            dest="node_aliases",
            nargs="+",
            help="One or more node aliases to migrate. If omitted, all domain/domain-list nodes in the graph are migrated.",
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

            if not options["overwrite"]:
                for collection_name in options["collections_to_migrate"]:
                    if List.objects.filter(name=collection_name).exists():
                        raise CommandError(
                            f"The controlled list '{collection_name}' already exists."
                        )

            self.migrate_collections_to_controlled_lists(
                collections_to_migrate=options["collections_to_migrate"],
                host=options["host"],
                overwrite=options["overwrite"],
                preferred_sort_language=psl,
            )
        elif options["operation"] == "migrate_concept_nodes_to_reference_datatype":
            graph = options["graph"]
            if not graph or graph is None:
                raise CommandError("Please provide a graph id or slug")
            self.migrate_concept_nodes_to_reference_datatype(graph)
        elif options["operation"] == "migrate_domain_nodes_to_controlled_lists":
            graph = options["graph"]
            if not graph:
                raise CommandError("Please provide a graph id or slug with -g/--graph")
            self.migrate_domain_nodes_to_controlled_lists(
                graph=graph,
                node_aliases=options.get("node_aliases") or [],
                overwrite=options["overwrite"],
                host=options["host"],
            )
        elif options["operation"] == "change_url_base":
            if not options["host"] or options["host"] is None:
                raise CommandError("Please provide a target host")
            if options["lists"]:
                list_ids = options["lists"].split(",")
            else:
                list_ids = []
            self.bulk_change_url_base(
                target_hostname=options["host"], list_ids=list_ids
            )

    def migrate_collections_to_controlled_lists(
        self,
        collections_to_migrate,
        host,
        overwrite,
        preferred_sort_language,
    ):
        """
        Wrapper around __arches_migrate_collections_to_clm Postgres function to migrate
        concept collections to controlled lists for use in the controlled list manager plugin.
        Takes in a list of collection names to migrate, a host URL for URI generation,
        a language code to use for develop sort order of list items based on prefLabel in that language,
        and an overwrite boolean to determine whether to overwrite existing controlled lists or not.

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

        if len(collections_to_migrate) == 1 and collections_to_migrate[0] == "":
            collections_in_db = list(
                Value.objects.filter(
                    valuetype__in=["prefLabel", "identifier"],
                    concept__nodetype="Collection",
                ).values_list("value", flat=True)
            )

            if len(collections_in_db) == 0:
                self.stderr.write(
                    "No collections were found in the database to migrate to controlled lists."
                )

        if len(collections_in_db) == 0:
            self.stderr.write(
                "No collections were found in the database for the provided collection names."
            )

        failed_collections = [
            collection
            for collection in collections_to_migrate
            if collection not in collections_in_db and collection != ""
        ]

        if len(failed_collections) > 0:
            self.stderr.write(
                "Failed to find the following collections in the database: %s"
                % ", ".join(failed_collections)
            )

        if len(collections_in_db) > 0:
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

    def migrate_domain_nodes_to_controlled_lists(
        self, graph, node_aliases, overwrite, host
    ):
        """
        Creates a controlled list for each domain/domain-list node in the given graph,
        using the node alias as the list name and the domain option id as the list item id.
        URIs are minted as <host>/<option-id>.

        Example usage:
            python manage.py controlled_lists
                -o migrate_domain_nodes_to_controlled_lists
                -g <graphid-or-slug>
                -ho http://localhost:8000/plugins/controlled-list-manager/item/

            python manage.py controlled_lists
                -o migrate_domain_nodes_to_controlled_lists
                -g <graphid-or-slug>
                -n <node-alias-1> <node-alias-2>
                -ho http://localhost:8000/plugins/controlled-list-manager/item/
                --overwrite
        """
        try:
            uuid.UUID(graph)
            graph_query = models.Q(graphid=graph)
        except ValueError:
            graph_query = models.Q(slug=graph)

        try:
            graph = Graph.objects.get(graph_query & models.Q(source_identifier=None))
        except Graph.DoesNotExist as e:
            raise CommandError(e)

        nodes_qs = Node.objects.filter(
            graph=graph,
            datatype__in=["domain-value", "domain-value-list"],
        )
        if node_aliases:
            nodes_qs = nodes_qs.filter(alias__in=node_aliases)

        nodes = list(nodes_qs)

        if not nodes:
            raise CommandError(
                "No domain/domain-list nodes found for graph '{0}'{1}".format(
                    graph.name,
                    f" with aliases: {', '.join(node_aliases)}" if node_aliases else "",
                )
            )

        if node_aliases:
            found_aliases = {n.alias for n in nodes}
            missing = set(node_aliases) - found_aliases
            if missing:
                raise CommandError(
                    "Could not find domain nodes with aliases: {0}".format(
                        ", ".join(sorted(missing))
                    )
                )

        if not overwrite:
            for node in nodes:
                if List.objects.filter(name=f"{node.alias}_{node.nodeid}").exists():
                    raise CommandError(
                        f"A controlled list named '{node.alias}_{node.nodeid}' already exists. "
                        "Use --overwrite to replace it."
                    )

        default_language = Language.objects.filter(isdefault=True).first()

        with transaction.atomic():
            for node in nodes:
                list_name = f"{node.alias}_{node.nodeid}"
                options = (node.config or {}).get("options", [])
                if not options:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Node '{node.alias}' has no options, skipping."
                        )
                    )
                    continue

                if overwrite:
                    List.objects.filter(name=list_name).delete()

                controlled_list = List.objects.create(name=list_name)

                new_list_items = []
                new_list_item_values = []

                new_ids_for_current_node = {
                    uuid.UUID(option["id"]) for option in options
                }
                existing_ids = set(
                    ListItem.objects.filter(
                        id__in=new_ids_for_current_node
                    ).values_list("id", flat=True)
                )

                for sortorder, option in enumerate(options):
                    desired_id = uuid.UUID(option["id"])
                    if desired_id in existing_ids:
                        item_id = uuid.uuid4()
                    else:
                        item_id = desired_id
                    list_item = ListItem(
                        id=item_id,
                        uri=f"{host.rstrip('/')}/{desired_id}",
                        list=controlled_list,
                        sortorder=sortorder,
                        parent=None,
                    )
                    new_list_items.append(list_item)

                    text = option.get("text", "")
                    if isinstance(text, dict):
                        for lang_code, label in text.items():
                            if label:
                                new_list_item_values.append(
                                    ListItemValue(
                                        list_item=list_item,
                                        valuetype_id="prefLabel",
                                        language_id=lang_code,
                                        value=label,
                                    )
                                )
                    elif isinstance(text, str) and text and default_language:
                        new_list_item_values.append(
                            ListItemValue(
                                list_item=list_item,
                                valuetype_id="prefLabel",
                                language_id=default_language.code,
                                value=text,
                            )
                        )

                ListItem.objects.bulk_create(new_list_items)
                ListItemValue.objects.bulk_create(new_list_item_values)

                self.stdout.write(
                    self.style.SUCCESS(
                        "Created controlled list '{0}' with {1} items from node '{2}'.".format(
                            controlled_list.name, len(new_list_items), node.alias
                        )
                    )
                )

    def migrate_concept_nodes_to_reference_datatype(self, graph):
        try:
            uuid.UUID(graph)
            query = models.Q(graphid=graph, source_identifier=None)
        except ValueError:
            query = models.Q(slug=graph, source_identifier=None)

        try:
            source_graph = Graph.objects.get(query)
        except Graph.DoesNotExist as e:
            raise CommandError(e)

        draft_graph = source_graph.draft.first()
        if not draft_graph:
            draft_graph = source_graph.create_draft_graph()

        nodes = (
            Node.objects.filter(
                graph=draft_graph,
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
        REFERENCE_FACTORY = DataTypeFactory().get_instance("reference")
        controlled_list_ids = List.objects.all().values_list("id", flat=True)

        errors = []
        # Check that collections have been migrated to controlled lists
        for node in nodes:
            if node.collection_id not in controlled_list_ids:
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
            with transaction.atomic():
                for node in nodes:
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

                    cross_records = node.cardxnodexwidget_set.annotate(
                        config_without_options=CombinedExpression(
                            models.F("config"),
                            "-",
                            models.Value("options", output_field=models.CharField()),
                            output_field=I18n_JSONField(),
                        )
                    )
                    for cross_record in cross_records:
                        # work around for i18n as_sql method issue detailed here: https://github.com/archesproject/arches/issues/11473
                        cross_record.config = {}
                        cross_record.save()

                        # Crosswalk concept version of default values to reference versions
                        original_default_value = (
                            cross_record.config_without_options.get(
                                "defaultValue", None
                            )
                        )
                        if original_default_value:
                            new_default_value = []
                            if isinstance(original_default_value, str):
                                original_default_value = [original_default_value]
                            for value in original_default_value:
                                value_rec = Value.objects.get(pk=value)
                                config = {"controlledList": node.collection_id}
                                new_value = REFERENCE_FACTORY.transform_value_for_tile(
                                    value=value_rec.value,
                                    **config,
                                )
                                if isinstance(new_value, list):
                                    new_default_value.append(new_value[0])
                                else:
                                    raise CommandError(
                                        f"Failed to convert original default value: {value_rec.value} in list: {node.collection_id} for node: {node.name} into a reference datatype instance"
                                    )
                            cross_record.config_without_options["defaultValue"] = (
                                new_default_value
                            )

                        cross_record.config = cross_record.config_without_options
                        cross_record.widget = REFERENCE_SELECT_WIDGET
                        cross_record.full_clean()
                        cross_record.save()

            updated_graph = source_graph.promote_draft_graph_to_active_graph()
            updated_graph.publish(
                notes="Migrated concept/concept-list nodes to reference datatype"
            )

            self.stdout.write(
                "All concept/concept-list nodes for the {0} graph have been successfully migrated to reference datatype".format(
                    source_graph.name
                )
            )

    # Replaces the base URL for all list items in all controlled lists
    def bulk_change_url_base(self, target_hostname: str, list_ids: list) -> str:
        normalized_url = self._normalize_url(target_hostname)
        try:
            with transaction.atomic():
                list_item_query = ListItem.objects.all()
                if list_ids:
                    list_item_query = list_item_query.filter(list_id__in=list_ids)
                for list_item in list_item_query.all():
                    new_uri = self._replace_hostname(list_item.uri, normalized_url)
                    list_item.uri = new_uri
                    list_item.save()
        except Exception as e:
            self.stderr.write(f"Could not change base url: {str(e)}")
            return

        self.stdout.write("Successfully changed URL base.")

    # Ensure that the URL has a scheme and is properly formatted
    def _normalize_url(self, url, default_scheme="https"):
        if not url.startswith("//") and "://" not in url:
            url = f"{default_scheme}://{url.lstrip('/')}"

        parts = urlsplit(url)

        scheme = parts.scheme or default_scheme

        if parts.port is not None:
            is_http_default = scheme == "http" and parts.port == 80
            is_https_default = scheme == "https" and parts.port == 443

            if is_http_default or is_https_default:
                netloc = parts.hostname
            else:
                netloc = parts.netloc
        else:
            netloc = parts.netloc

        return urlunsplit((scheme, netloc, parts.path, parts.query, parts.fragment))

    # Replace the hostname in a given URL with the target hostname
    def _replace_hostname(self, url_string: str, target_hostname: str) -> str:
        try:
            normalized_target = urlparse(target_hostname)
            parsed_url = urlparse(url_string)

            # Should never happen - but abandon ship if it does
            if not parsed_url.netloc:
                print(
                    f"Warning: Invalid URL format, missing network location: {url_string}"
                )
                return url_string

            new_netloc = normalized_target.netloc
            new_scheme = normalized_target.scheme

            updated_url = urlunparse(
                (
                    new_scheme,
                    new_netloc,
                    parsed_url.path,
                    parsed_url.params,
                    parsed_url.query,
                    parsed_url.fragment,
                )
            )

            return updated_url

        except Exception as e:
            print(f"An error occurred while processing the URL: {e}")
            return url_string
