import logging

from django.contrib.auth.models import User
from django.db import connection, transaction
from django.utils.translation import gettext as _

from arches.app.etl_modules.base_data_editor import (
    BaseBulkEditor,
    MissingRequiredInputError,
)
from arches.app.etl_modules.decorators import load_data_async
from arches.app.etl_modules.save import save_to_tiles
from arches.app.models.models import (
    GraphModel,
    LoadErrors,
    LoadStaging,
    Node,
    TileModel,
    Value,
)
from arches.app.models.system_settings import settings as arches_settings

from arches_controlled_lists.models import ListItem


logger = logging.getLogger(__name__)


CONCEPT_ORIGIN = "concept"
DOMAIN_ORIGIN = "domain"
CONCEPT_LEGACY_DATATYPES = ("concept", "concept-list")
DOMAIN_LEGACY_DATATYPES = ("domain-value", "domain-value-list")


def _config_marker(origin):
    return "options" if origin == DOMAIN_ORIGIN else "rdmCollection"


class ValueResolver:
    """Caches list-item lookups for one (node, list) pair and resolves a
    legacy tile value to a ListItem via either an id match or a label
    fallback.

    The id branch mirrors `ReferenceDataType.transform_value_for_tile`'s UUID
    path; the label branch mirrors its label path. Both branches read from
    in-memory dicts so per-tile resolution is O(1).

    Subclasses provide `_build_label_index`, returning a mapping
    {legacy_id_str: label_string} sourced from either `node.config["options"]`
    (domain) or the Value/Concept tables (concept).
    """

    def __init__(self, node, list_id, language_code, legacy_ids=None):
        self.node = node
        self.list_id = list_id
        self.language_code = language_code

        items = list(
            ListItem.objects.filter(list_id=list_id).prefetch_related(
                "list_item_values"
            )
        )
        self.list_items_by_id = {str(item.pk): item for item in items}
        self.list_items_by_label = {}
        for item in items:
            for liv in item.list_item_values.all():
                key = (liv.value or "").casefold()
                if key:
                    self.list_items_by_label.setdefault(key, item)

        self.label_for_legacy_id = self._build_label_index(legacy_ids or set())

    def _build_label_index(self, legacy_ids):
        return {}

    def resolve(self, legacy_id):
        if legacy_id is None:
            return None
        legacy_str = str(legacy_id)
        item = self.list_items_by_id.get(legacy_str)
        if item is not None:
            return item
        label = self.label_for_legacy_id.get(legacy_str)
        if not label:
            return None
        return self.list_items_by_label.get(label.casefold())


class DomainValueResolver(ValueResolver):
    def _build_label_index(self, legacy_ids):
        labels = {}
        for option in (self.node.config or {}).get("options") or []:
            option_id = option.get("id")
            text = option.get("text")
            label = None
            if isinstance(text, dict):
                label = text.get(self.language_code) or next(
                    (val for val in text.values() if val), None
                )
            elif isinstance(text, str):
                label = text
            if option_id and label:
                labels[str(option_id)] = label
        return labels


class ConceptValueResolver(ValueResolver):
    def _build_label_index(self, legacy_ids):
        labels = {}
        if not legacy_ids:
            return labels
        valueid_to_concept = dict(
            Value.objects.filter(pk__in=legacy_ids).values_list("pk", "concept_id")
        )
        concept_ids = set(valueid_to_concept.values())
        if not concept_ids:
            return labels

        preferred = {
            row["concept_id"]: row["value"]
            for row in Value.objects.filter(
                concept_id__in=concept_ids,
                valuetype_id="prefLabel",
                language_id=self.language_code,
            ).values("concept_id", "value")
        }
        fallback = {
            row["concept_id"]: row["value"]
            for row in Value.objects.filter(
                concept_id__in=concept_ids,
                valuetype_id="prefLabel",
            )
            .exclude(concept_id__in=preferred.keys())
            .values("concept_id", "value")
        }
        for valueid, concept_id in valueid_to_concept.items():
            label = preferred.get(concept_id) or fallback.get(concept_id)
            if label:
                labels[str(valueid)] = label
        return labels


class MigrateToReferenceDatatype(BaseBulkEditor):
    """Bulk editor that rewrites tile data for nodes which have already been
    retyped from concept/concept-list/domain/domain-list to reference. For
    each tile touching a candidate node, the legacy id value(s) are resolved
    to ListItem instances and the tile slot is replaced with the reference-
    datatype shape via ListItem.build_tile_value.
    """

    def validate(self, request):
        return {"success": True, "data": {}}

    def validate_inputs(self, request):
        required = {
            "graph_id": _("Resource Model"),
            "origin": _("Origin Datatype"),
        }
        for key, label in required.items():
            if not request.POST.get(key):
                raise MissingRequiredInputError(
                    _("Missing required value: {label}").format(label=label)
                )
        if request.POST.get("origin") not in {CONCEPT_ORIGIN, DOMAIN_ORIGIN}:
            raise MissingRequiredInputError(
                _("Origin must be either 'concept' or 'domain'.")
            )

    def get_candidate_nodes(self, request):
        graph_id = request.POST.get("graph_id")
        origin = request.POST.get("origin")
        if not graph_id or origin not in {CONCEPT_ORIGIN, DOMAIN_ORIGIN}:
            return {
                "success": False,
                "data": {"message": _("Missing graph or origin.")},
            }
        nodes = list(
            Node.objects.filter(graph_id=graph_id, datatype="reference")
            .filter(**{"config__has_key": _config_marker(origin)})
            .order_by("name")
        )
        node_payload = []
        for node in nodes:
            tile_count = TileModel.objects.filter(
                nodegroup_id=node.nodegroup_id,
                data__has_key=str(node.pk),
            ).count()
            node_payload.append(
                {
                    "nodeid": str(node.pk),
                    "alias": node.alias,
                    "name": str(node.name),
                    "list_id": (node.config or {}).get("controlledList"),
                    "tile_count": tile_count,
                }
            )
        return {"success": True, "data": node_payload}

    def write(self, request):
        try:
            self.validate_inputs(request)
        except MissingRequiredInputError as e:
            return {
                "success": False,
                "data": {"title": _("Missing input error"), "message": str(e)},
            }

        graph_id = request.POST["graph_id"]
        origin = request.POST["origin"]
        language_code = (
            request.POST.get("language_code") or arches_settings.LANGUAGE_CODE
        )

        graph_name = str(GraphModel.objects.get(pk=graph_id).name)
        load_details = {
            "graph": graph_name,
            "operation": "migrate_to_reference_datatype",
            "details": {"origin": origin, "language_code": language_code},
        }

        with connection.cursor() as cursor:
            event_created = self.create_load_event(cursor, load_details)
            if not event_created["success"]:
                self.log_event(cursor, "failed")
                return {"success": False, "data": event_created["message"]}

        return self.run_load_task_async(request, self.loadid)

    @load_data_async
    def run_load_task_async(self, request):
        from arches_controlled_lists import tasks as cl_tasks

        graph_id = request.POST["graph_id"]
        origin = request.POST["origin"]
        language_code = (
            request.POST.get("language_code") or arches_settings.LANGUAGE_CODE
        )
        edit_task = cl_tasks.migrate_to_reference_datatype.apply_async(
            (
                self.userid,
                self.loadid,
                self.moduleid,
                graph_id,
                origin,
                language_code,
            ),
        )
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET taskid = %s WHERE loadid = %s""",
                (edit_task.task_id, self.loadid),
            )

    def run_load_task(
        self,
        userid,
        loadid,
        module_id,
        graph_id,
        origin,
        language_code,
    ):
        self.userid = userid
        self.loadid = loadid
        self.moduleid = module_id
        try:
            self._migrate_graph(graph_id, origin, language_code)
        except Exception as exc:
            logger.exception(exc)
            with connection.cursor() as cursor:
                self.log_event(cursor, "failed")
            return {
                "success": False,
                "data": {"title": _("Error"), "message": str(exc)},
            }

        save_to_tiles(userid, loadid)
        return {"success": True, "data": "done"}

    def _migrate_graph(self, graph_id, origin, language_code):
        marker = _config_marker(origin)
        candidate_nodes = list(
            Node.objects.filter(graph_id=graph_id, datatype="reference").filter(
                **{"config__has_key": marker}
            )
        )
        with connection.cursor() as cursor:
            if not candidate_nodes:
                self.log_event_details(
                    cursor,
                    f"done|No reference nodes with legacy {origin} markers found.",
                )
                return
            self.log_event_details(
                cursor,
                f"done|Found {len(candidate_nodes)} candidate node(s) to migrate.",
            )

        total_staged = 0
        total_errored = 0
        for node in candidate_nodes:
            staged, errored = self._migrate_node(node, origin, language_code)
            total_staged += staged
            total_errored += errored

        with connection.cursor() as cursor:
            self.log_event_details(
                cursor,
                f"done|Staged {total_staged} tile(s); "
                f"{total_errored} skipped due to unresolvable values.",
            )

    def _migrate_node(self, node, origin, language_code):
        list_id = (node.config or {}).get("controlledList")
        if not list_id:
            with connection.cursor() as cursor:
                self.log_event_details(
                    cursor,
                    f"done|Skipping node '{node.alias}' - no controlledList in config.",
                )
            return 0, 0

        nodeid_str = str(node.pk)
        multi_value = bool((node.config or {}).get("multiValue"))

        tile_qs = TileModel.objects.filter(
            nodegroup_id=node.nodegroup_id,
            data__has_key=nodeid_str,
        )

        legacy_ids = set()
        if origin == CONCEPT_ORIGIN:
            for tile_data in tile_qs.values_list("data", flat=True):
                value = (tile_data or {}).get(nodeid_str)
                if isinstance(value, list):
                    legacy_ids.update(item for item in value if item)
                elif value:
                    legacy_ids.add(value)

        resolver_cls = (
            DomainValueResolver if origin == DOMAIN_ORIGIN else ConceptValueResolver
        )
        resolver = resolver_cls(node, list_id, language_code, legacy_ids=legacy_ids)

        sibling_node_datatypes = {
            str(n.pk): n.datatype
            for n in Node.objects.filter(nodegroup_id=node.nodegroup_id)
        }

        staged_count = 0
        errored_count = 0
        with transaction.atomic():
            for tile in tile_qs.iterator():
                legacy_value = (tile.data or {}).get(nodeid_str)
                if legacy_value in (None, [], ""):
                    continue
                ids = legacy_value if isinstance(legacy_value, list) else [legacy_value]

                resolved = []
                missing = []
                for legacy_id in ids:
                    item = resolver.resolve(legacy_id)
                    if item is None:
                        missing.append(legacy_id)
                    else:
                        resolved.append(item)

                if missing:
                    LoadErrors.objects.create(
                        load_event_id=self.loadid,
                        nodegroup_id=node.nodegroup_id,
                        node_id=node.pk,
                        type="WARNING",
                        error="UnresolvedLegacyValue",
                        source="migrate_to_reference_datatype",
                        value=", ".join(str(item) for item in missing),
                        message=(
                            f"Could not resolve legacy {origin} id(s) "
                            f"{missing} on tile {tile.pk} for node "
                            f"'{node.alias}' against list {list_id}."
                        ),
                        datatype="reference",
                    )
                    errored_count += 1
                    continue

                new_value = [item.build_tile_value() for item in resolved]
                if not multi_value and len(new_value) > 1:
                    new_value = new_value[:1]

                staged_value = self._build_staged_value(
                    tile, nodeid_str, new_value, sibling_node_datatypes
                )

                LoadStaging.objects.create(
                    load_event_id=self.loadid,
                    nodegroup_id=node.nodegroup_id,
                    resourceid=tile.resourceinstance_id,
                    legacyid=str(tile.resourceinstance_id),
                    tileid=tile.pk,
                    parenttileid=tile.parenttile_id,
                    value=staged_value,
                    sortorder=tile.sortorder or 0,
                    nodegroup_depth=0,
                    source_description="migrate_to_reference_datatype",
                    operation="update",
                    passes_validation=True,
                )
                staged_count += 1

        return staged_count, errored_count

    @staticmethod
    def _build_staged_value(tile, target_nodeid, new_value, sibling_node_datatypes):
        staged = {}
        for key, val in (tile.data or {}).items():
            if key == target_nodeid:
                staged[key] = {
                    "value": new_value,
                    "valid": True,
                    "source": "bulk_edit",
                    "notes": "",
                    "datatype": "reference",
                }
            else:
                staged[key] = {
                    "value": val,
                    "valid": True,
                    "source": "bulk_edit",
                    "notes": "",
                    "datatype": sibling_node_datatypes.get(key, "string"),
                }
        if target_nodeid not in staged:
            staged[target_nodeid] = {
                "value": new_value,
                "valid": True,
                "source": "bulk_edit",
                "notes": "",
                "datatype": "reference",
            }
        return staged
