import logging
import uuid

from django.db import connection, transaction
from django.db.models import F, OuterRef, Subquery, UUIDField
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast
from django.utils.translation import gettext as _

from arches.app.etl_modules.base_data_editor import (
    BaseBulkEditor,
    MissingRequiredInputError,
)
from arches.app.etl_modules.decorators import load_data_async
from arches.app.etl_modules.save import save_to_tiles
from arches.app.models.models import (
    ETLModule,
    GraphModel,
    LoadErrors,
    LoadStaging,
    Node,
    TileModel,
    Value,
)
from arches.app.models.system_settings import settings as settings

from arches_controlled_lists.models import List


logger = logging.getLogger(__name__)


CONCEPT_ORIGIN = "concept"
DOMAIN_ORIGIN = "domain"
CELERY_TILE_THRESHOLD = 500


class LegacyValueTranslator:
    """Resolves a legacy tile value (concept valueid or domain option id)
    to the reference-datatype tile representation by delegating to
    `ReferenceDataType.transform_value_for_tile`. First attempts to resolve
    the legacy id directly (works when the legacy id was preserved as the
    ListItem.id during retype); if that yields no items, falls back to the
    legacy value's label and retries. Results are memoized per legacy id
    so repeated tile values only hit the datatype once.

    Subclasses provide `_build_label_index`, returning a mapping
    {legacy_id_str: label_string} sourced from either `node.config["options"]`
    (domain) or the Value/Concept tables (concept).
    """

    def __init__(
        self, node, list_id, language_code, reference_datatype, legacy_ids=None
    ):
        self.node = node
        self.list_id = list_id
        self.language_code = language_code
        self.reference_datatype = reference_datatype
        self.label_for_legacy_id = self._build_label_index(legacy_ids or set())
        self.legacy_id_to_reference_val_cache = {}

    def _build_label_index(self, legacy_ids):
        return {}

    def resolve(self, legacy_id):
        """Return a list of reference tile-value dicts for `legacy_id`, or
        None if neither the id nor its label resolves against the target
        list. Caches per legacy id."""
        if legacy_id is None:
            return None
        legacy_str = str(legacy_id)
        if legacy_str in self.legacy_id_to_reference_val_cache:
            return self.legacy_id_to_reference_val_cache[legacy_str]

        resolved = self.reference_datatype.transform_value_for_tile(
            [legacy_str], controlledList=self.list_id
        )
        if not resolved:
            label = self.label_for_legacy_id.get(legacy_str)
            if label:
                resolved = self.reference_datatype.transform_value_for_tile(
                    [label], controlledList=self.list_id
                )

        self.legacy_id_to_reference_val_cache[legacy_str] = resolved or None
        return self.legacy_id_to_reference_val_cache[legacy_str]


class DomainLegacyValueTranslator(LegacyValueTranslator):
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


class ConceptLegacyValueTranslator(LegacyValueTranslator):
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
    each tile touching a candidate node, the legacy id value(s) are
    translated to either a ListItem.id or a label string and handed to
    ReferenceDataType.transform_value_for_tile, which returns the
    reference-shaped tile slot.
    """

    def __init__(self, request=None, loadid=None, userid=None, **kwargs):
        super().__init__(request=request, loadid=loadid)
        if request is None:
            self.userid = userid
            self.moduleid = kwargs.get("moduleid") or str(
                ETLModule.objects.get(slug="migrate-to-reference-datatype").pk
            )
            if self.loadid is None:
                self.loadid = str(uuid.uuid4())
        self._graph_id = kwargs.get("graph_id")
        self._origin = kwargs.get("origin")
        self._language_code = kwargs.get("language_code")

    def validate(self, request):
        return {"success": True, "data": {}}

    def validate_inputs(self, graph_id, origin):
        if not graph_id:
            raise MissingRequiredInputError(
                _("Missing required value: {label}").format(label=_("Resource Model"))
            )
        if not origin:
            raise MissingRequiredInputError(
                _("Missing required value: {label}").format(label=_("Origin Datatype"))
            )
        if origin not in {CONCEPT_ORIGIN, DOMAIN_ORIGIN}:
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
        list_name_subquery = Subquery(
            List.objects.filter(
                id=Cast(
                    KeyTextTransform("controlledList", OuterRef("config")),
                    UUIDField(),
                )
            ).values("name")[:1]
        )
        nodes = list(
            self._get_candidate_nodes_queryset(graph_id, origin)
            .annotate(
                nodegroup_name=F("nodegroup__grouping_node__alias"),
                list_name=list_name_subquery,
            )
            .order_by("nodegroup__grouping_node__alias", "alias")
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
                    "nodegroup": node.nodegroup_name,
                    "list_name": node.list_name,
                    "tile_count": tile_count,
                }
            )
        return {"success": True, "data": node_payload}

    def _get_candidate_nodes_queryset(self, graph_id, origin):
        queryset = Node.objects.filter(
            graph_id=graph_id, datatype="reference"
        ).prefetch_related("nodegroup")
        if origin == DOMAIN_ORIGIN:
            queryset = queryset.filter(**{"config__has_key": "options"})
        elif origin == CONCEPT_ORIGIN:
            queryset = queryset.exclude(**{"config__has_key": "options"})
        return queryset

    def _count_candidate_tiles(self, graph_id, origin):
        candidate_node_ids = [
            str(pk)
            for pk in self._get_candidate_nodes_queryset(graph_id, origin).values_list(
                "pk", flat=True
            )
        ]
        if not candidate_node_ids:
            return 0
        nodegroup_ids = set(
            Node.objects.filter(pk__in=candidate_node_ids).values_list(
                "nodegroup_id", flat=True
            )
        )
        return TileModel.objects.filter(
            nodegroup_id__in=nodegroup_ids,
            data__has_any_keys=candidate_node_ids,
        ).count()

    def write(self, request):
        graph_id = request.POST.get("graph_id") if request else self._graph_id
        origin = request.POST.get("origin") if request else self._origin
        language_code = (
            request.POST.get("language_code") if request else self._language_code
        ) or settings.LANGUAGE_CODE

        try:
            self.validate_inputs(graph_id, origin)
        except MissingRequiredInputError as e:
            return {
                "success": False,
                "data": {"title": _("Missing input error"), "message": str(e)},
            }

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

        tile_count = self._count_candidate_tiles(graph_id, origin)
        if tile_count > CELERY_TILE_THRESHOLD:
            return self.run_load_task_async(request, self.loadid)

        return self.run_load_task(
            self.userid,
            self.loadid,
            self.moduleid,
            graph_id,
            origin,
            language_code,
        )

    @load_data_async
    def run_load_task_async(self, request):
        from arches_controlled_lists import tasks as cl_tasks

        graph_id = request.POST["graph_id"]
        origin = request.POST["origin"]
        language_code = request.POST.get("language_code") or settings.LANGUAGE_CODE
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
            self._stage_tile_edits(graph_id, origin, language_code)
        except Exception as e:
            logger.exception(e)
            with connection.cursor() as cursor:
                self.log_event(cursor, "failed")
            return {
                "success": False,
                "data": {"title": _("Error"), "message": str(e)},
            }

        save_to_tiles(userid, loadid)
        return {"success": True, "data": "done"}

    def _stage_tile_edits(self, graph_id, origin, language_code):
        candidate_nodes = list(self._get_candidate_nodes_queryset(graph_id, origin))
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

        candidates_by_node_id = {str(node.pk): node for node in candidate_nodes}
        candidate_node_ids = list(candidates_by_node_id.keys())
        nodegroup_ids = {node.nodegroup_id for node in candidate_nodes}

        translators = self._build_translators(
            candidates_by_node_id, origin, language_code, nodegroup_ids
        )
        sibling_datatypes_by_nodegroup = {}

        tiles = TileModel.objects.filter(
            nodegroup_id__in=nodegroup_ids,
            data__has_any_keys=candidate_node_ids,
        ).iterator()

        staged_count = 0
        errored_count = 0
        staging_records = []
        error_records = []
        with transaction.atomic():
            for tile in tiles:
                sibling_datatypes = sibling_datatypes_by_nodegroup.get(
                    tile.nodegroup_id
                )
                if sibling_datatypes is None:
                    sibling_datatypes = {
                        str(sibling.pk): sibling.datatype
                        for sibling in Node.objects.filter(
                            nodegroup_id=tile.nodegroup_id
                        )
                    }
                    sibling_datatypes_by_nodegroup[tile.nodegroup_id] = (
                        sibling_datatypes
                    )

                staged, errored = self._rewrite_tile(
                    tile=tile,
                    candidates_by_node_id=candidates_by_node_id,
                    translators=translators,
                    origin=origin,
                    sibling_datatypes=sibling_datatypes,
                )
                if staged:
                    staging_records.append(staged)
                    staged_count += 1
                if errored:
                    error_records.append(errored)
                    errored_count += 1
            LoadStaging.objects.bulk_create(staging_records)
            LoadErrors.objects.bulk_create(error_records)

        with connection.cursor() as cursor:
            self.log_event_details(
                cursor,
                f"done|Staged {staged_count} tile(s); "
                f"{errored_count} skipped due to unresolvable values.",
            )

    def _build_translators(
        self, candidates_by_node_id, origin, language_code, nodegroup_ids
    ):
        """Construct one translator per candidate node, sharing per-node
        legacy-id collection so concept-side label indexing only fires for
        the values actually referenced by tiles."""
        translator_cls = (
            DomainLegacyValueTranslator
            if origin == DOMAIN_ORIGIN
            else ConceptLegacyValueTranslator
        )
        reference_datatype = self.datatype_factory.get_instance("reference")

        legacy_ids_by_node_id = {node_id: set() for node_id in candidates_by_node_id}
        if origin == CONCEPT_ORIGIN:
            for tile_data in TileModel.objects.filter(
                nodegroup_id__in=nodegroup_ids,
                data__has_any_keys=list(candidates_by_node_id.keys()),
            ).values_list("data", flat=True):
                for node_id in candidates_by_node_id:
                    value = (tile_data or {}).get(node_id)
                    if isinstance(value, list):
                        legacy_ids_by_node_id[node_id].update(
                            item for item in value if item
                        )
                    elif value:
                        legacy_ids_by_node_id[node_id].add(value)

        translators = {}
        for node_id, node in candidates_by_node_id.items():
            list_id = (node.config or {}).get("controlledList")
            if not list_id:
                continue
            translators[node_id] = translator_cls(
                node,
                list_id,
                language_code,
                reference_datatype,
                legacy_ids=legacy_ids_by_node_id[node_id],
            )
        return translators

    def _rewrite_tile(
        self,
        *,
        tile,
        candidates_by_node_id,
        translators,
        origin,
        sibling_datatypes,
    ) -> tuple[LoadStaging | None, LoadErrors | None]:
        load_staging_record = None
        load_error_record = None
        rewritten_values_by_node_id = {}
        unresolved_per_node = {}

        for node_id, node in candidates_by_node_id.items():
            if node.nodegroup_id != tile.nodegroup_id:
                continue
            translator = translators.get(node_id)
            if translator is None:
                continue
            legacy_value = (tile.data or {}).get(node_id)
            if legacy_value in (None, [], ""):
                continue
            legacy_ids = (
                legacy_value if isinstance(legacy_value, list) else [legacy_value]
            )

            resolved_entries = []
            missing = []
            for legacy_id in legacy_ids:
                entries = translator.resolve(legacy_id)
                if not entries:
                    missing.append(legacy_id)
                else:
                    resolved_entries.extend(entries)

            if missing:
                unresolved_per_node[node_id] = (node, translator.list_id, missing)
                continue

            if (
                not bool((node.config or {}).get("multiValue"))
                and len(resolved_entries) > 1
            ):
                resolved_entries = resolved_entries[:1]
            rewritten_values_by_node_id[node_id] = resolved_entries

        if unresolved_per_node:
            for node_id, (node, list_id, missing) in unresolved_per_node.items():
                load_error_record = LoadErrors(
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
            return load_staging_record, load_error_record

        if not rewritten_values_by_node_id:
            return load_staging_record, load_error_record

        staged_value = self._build_staged_value(
            tile, rewritten_values_by_node_id, sibling_datatypes
        )
        load_staging_record = LoadStaging(
            load_event_id=self.loadid,
            nodegroup_id=tile.nodegroup_id,
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
        return load_staging_record, load_error_record

    @staticmethod
    def _build_staged_value(tile, rewritten_values_by_node_id, sibling_datatypes):
        staged = {}
        for nodeid, node_val in (tile.data or {}).items():
            if nodeid in rewritten_values_by_node_id:
                staged[nodeid] = {
                    "value": rewritten_values_by_node_id[nodeid],
                    "valid": True,
                    "source": "bulk_edit",
                    "notes": "",
                    "datatype": "reference",
                }
            else:
                staged[nodeid] = {
                    "value": node_val,
                    "valid": True,
                    "source": "bulk_edit",
                    "notes": "",
                    "datatype": sibling_datatypes.get(nodeid, "string"),
                }
        for node_id, new_value in rewritten_values_by_node_id.items():
            if node_id not in staged:
                staged[node_id] = {
                    "value": new_value,
                    "valid": True,
                    "source": "bulk_edit",
                    "notes": "",
                    "datatype": "reference",
                }
        return staged
