"""Bulk import of Arches JSON business data through the ETL loader."""

import json
import logging
import os
import time
import uuid
import zipfile
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files import File as DjangoFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import connection, transaction
from django.http import HttpRequest
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.etl_modules.base_import_module import BaseImportModule
from arches.app.etl_modules.decorators import load_data_async
from arches.app.etl_modules.save import (
    _post_save_edit_log,
    disable_tile_triggers,
    log_event_details,
    reenable_tile_triggers,
)
from arches.app.models.models import (
    EditLog,
    ETLModule,
    File,
    GraphModel,
    LoadErrors,
    LoadEvent,
    LoadStaging,
    Node,
    NodeGroup,
    ResourceInstance,
    ResourceInstanceLifecycleState,
    TileModel,
)
from arches.app.models.system_settings import settings
from arches.app.utils.decorators import user_created_transaction_match
from arches.app.utils.file_validator import FileValidator

logger = logging.getLogger(__name__)

# file-list metadata that Arches 8 stores as {lang: {value, direction}}.  A bare
# string here poisons the Elasticsearch mapping for every later document.
LOCALIZED_FILE_KEYS = ("altText", "attribution", "description", "title")

# Cap the per-node validation memo.  It pays for itself on low-cardinality nodes
# (concepts, dates) and is pure leak on free text; without a bound a 300k load
# retains every distinct string it has ever seen.
MEMO_MAX_VALUES_PER_NODE = 5000

# Advisory lock key.  disable_tile_triggers() is an ALTER TABLE -- database-wide,
# not session-scoped -- so two concurrent bulk loads would race, the first to
# finish re-enabling triggers while the second is still inserting.
TILE_TRIGGER_LOCK_KEY = 8202514
# How many rows a set-based existence check may ask about at once. Keeps the IN
# clause under Postgres' 65,535 bind parameters and the unnest arrays small
# enough to build without a memory spike.
DB_CHECK_BATCH_SIZE = 20000


class ArchesJsonImporter(BaseImportModule):
    def __init__(
        self,
        request=None,
        loadid=None,
        temp_dir=None,
        params=None,
        userid=None,
        moduleid=None,
    ):
        self.loadid = request.POST.get("load_id") if request else loadid
        if request:
            self.userid = request.user.id
        elif userid is not None:
            self.userid = userid
        else:
            self.userid = settings.DEFAULT_RESOURCE_IMPORT_USER["userid"]
        self.mode = "cli" if not request and params else "ui"
        try:
            self.user = User.objects.get(pk=self.userid)
        except User.DoesNotExist:
            raise User.DoesNotExist(
                _(
                    "The userid {} does not exist. Probably DEFAULT_RESOURCE_IMPORT_USER is not configured correctly in settings.py.".format(
                        self.userid
                    )
                )
            )
        if not request and params:
            request = HttpRequest()
            request.user = self.user
            request.method = "POST"
            for k, v in params.items():
                request.POST.__setitem__(k, v)
        self.request = request
        self.moduleid = request.POST.get("module") if request else moduleid
        self.config = (
            ETLModule.objects.get(pk=self.moduleid).config if self.moduleid else {}
        )
        self.datatype_factory = DataTypeFactory()
        self.temp_dir = temp_dir
        self.validated_data = {}
        self._memo_disabled_nodes = set()
        self._graph_cache = {}
        self._source_paths = []
        self._overwrite = False
        self._counts = {}

    # --------------------------------------------------------------- options

    # read(), write() and the Celery task are separate requests with separate
    # instances, so the user's choices have to live on the load_event.
    def start(self, request):
        self.temp_dir = os.path.join(settings.UPLOADED_FILES_DIR, "tmp", self.loadid)
        options = {
            "overwrite": self._flag(request, "overwrite"),
            "index": self._flag(request, "index", default=True),
        }
        LoadEvent.objects.create(
            loadid=self.loadid,
            etl_module_id=self.moduleid,
            complete=False,
            status="running",
            load_start_time=timezone.now(),
            user_id=self.userid,
            load_details={"config": options},
        )
        return {"success": True, "data": {"started": True, "message": ""}}

    @staticmethod
    def _flag(request, name, default=False):
        raw = request.POST.get(name)
        if raw is None:
            return default
        return raw in ("true", "True", True)

    def _load_options(self, loadid=None):
        details = (
            LoadEvent.objects.filter(loadid=loadid or self.loadid)
            .values_list("load_details", flat=True)
            .first()
        ) or {}
        return (details or {}).get("config", {})

    # ------------------------------------------------------------------ read

    def read(self, request=None, source=None):
        self.prepare_temp_dir(request)
        self.cumulative_files_size = 0

        if request:
            content = request.FILES.get("file")
        else:
            file_stat = os.stat(source)
            content = InMemoryUploadedFile(
                open(source, "rb"),
                "file",
                os.path.basename(source),
                self._content_type(source),
                file_stat.st_size,
                None,
            )

        result = {
            "summary": {
                "name": content.name,
                "size": self.filesize_format(content.size),
                "files": {},
            }
        }

        try:
            validator = FileValidator()
            extension = content.name.split(".")[-1].lower()
            if extension not in ("json", "jsonl", "zip"):
                return {
                    "success": False,
                    "data": {
                        "title": _("Invalid file"),
                        "message": _("Upload a .json, .jsonl or .zip file"),
                    },
                }
            if extension == "zip" and validator.validate_file_type(content, extension):
                return {
                    "success": False,
                    "data": {
                        "title": _("Invalid zip file"),
                        "message": _("Upload a valid .zip file"),
                    },
                }

            if extension == "zip":
                self._read_zip(content, result)
            else:
                self.cumulative_files_size += content.size
                result["summary"]["files"][content.name] = {
                    "size": self.filesize_format(content.size)
                }
                default_storage.save(
                    os.path.join(self.temp_dir, content.name), DjangoFile(content)
                )
            result["summary"]["cumulative_files_size"] = self.cumulative_files_size
        finally:
            content.file.close()

        if not result["summary"]["files"]:
            return {
                "success": False,
                "data": {
                    "title": _("Invalid Uploaded File"),
                    "message": _("No .json or .jsonl file was found in the upload."),
                },
            }
        return {"success": True, "data": result}

    @staticmethod
    def _content_type(source):
        return (
            "application/zip" if source.lower().endswith(".zip") else "application/json"
        )

    def _read_zip(self, content, result):
        with zipfile.ZipFile(content, "r") as zip_ref:
            for member in zip_ref.infolist():
                if member.is_dir() or member.filename.startswith("__MACOSX"):
                    continue
                if member.filename.split(".")[-1].lower() not in ("json", "jsonl"):
                    summary = result["summary"]
                    summary["ignored_files"] = summary.get("ignored_files", 0) + 1
                    continue
                self.cumulative_files_size += member.file_size
                result["summary"]["files"][member.filename] = {
                    "size": self.filesize_format(member.file_size)
                }
                with zip_ref.open(member) as opened:
                    default_storage.save(
                        Path(self.temp_dir) / Path(member.filename).name,
                        DjangoFile(opened),
                    )

    # -------------------------------------------------------------- streaming

    def _iter_resources(self, filename):
        path = os.path.join(self.temp_dir, os.path.basename(filename))
        if filename.lower().endswith(".jsonl"):
            with default_storage.open(path, mode="rb") as handle:
                for line in handle:
                    line = line.strip()
                    if line:
                        yield json.loads(line)
        else:
            with default_storage.open(path, mode="rb") as handle:
                payload = json.load(handle)
            business_data = payload.get("business_data", payload)
            for resource in business_data.get("resources", []):
                yield resource

    # ------------------------------------------------------- pass 1: validate

    def stage_files(self, files, summary, cursor):
        try:
            self._stage_files(files, summary)
        except Exception as e:
            logger.exception(e)
            try:
                self._flush_failures(
                    [
                        self._failure(
                            ", ".join(files) if files else None,
                            _("Import failed while reading the file"),
                            message="{}: {}".format(type(e).__name__, e),
                        )
                    ]
                )
            except Exception:
                logger.exception("Could not record the import failure")
                raise e

    def _stage_files(self, files, summary):
        self._overwrite = bool(self._load_options().get("overwrite"))
        self._source_paths = list(files)
        seen_resourceids = {}
        legacyids = {}
        tile_owners = {}
        file_owners = {}
        constraint_candidates = {}
        cardinality_keys = {}
        counts = {}
        failures = []
        total = 0

        # Validation writes nothing until it finishes, so without this a large
        # load looks hung for its whole first phase.
        started = time.monotonic()
        for filename in self._source_paths:
            logger.info("validating %s", filename)
            for resource in self._iter_resources(filename):
                total += 1
                if total % 10000 == 0:
                    elapsed = time.monotonic() - started
                    logger.info(
                        "validated %s resources (%.0f/s, %.0fs elapsed)",
                        total,
                        total / elapsed if elapsed else 0,
                        elapsed,
                    )
                errors = self._validate_resource(
                    resource,
                    filename,
                    seen_resourceids,
                    legacyids,
                    constraint_candidates,
                    cardinality_keys,
                    counts,
                    tile_owners,
                    file_owners,
                )
                failures.extend(errors)
                # Checked as they stream: holding every tile id of a 200k-resource
                # load would cost hundreds of MB.
                if len(tile_owners) >= DB_CHECK_BATCH_SIZE:
                    failures.extend(self._check_existing_tiles(tile_owners))
                    tile_owners.clear()
                if len(failures) >= 1000:
                    self._flush_failures(failures)
                    failures = []

        failures.extend(self._check_existing_tiles(tile_owners))
        failures.extend(self._check_existing_resources(seen_resourceids))
        failures.extend(self._check_existing_files(file_owners))
        failures.extend(self._check_existing_legacyids(legacyids))
        failures.extend(self._check_global_constraints(constraint_candidates))
        failures.extend(self._check_existing_cardinality(cardinality_keys))
        self._flush_failures(failures)

        logger.info(
            "validation finished: %s resources in %.0fs",
            total,
            time.monotonic() - started,
        )
        self._counts = counts
        summary["resources"] = total
        summary["by_graph"] = {str(gid): value for gid, value in counts.items()}
        LoadEvent.objects.filter(loadid=self.loadid).update(
            load_details={"config": self._load_options(), "summary": summary}
        )

    def _validate_resource(
        self,
        resource,
        source,
        seen_resourceids,
        legacyids,
        constraint_candidates,
        cardinality_keys,
        counts,
        tile_owners,
        file_owners,
    ):
        failures = []
        instance = resource.get("resourceinstance")
        if not instance:
            return [self._failure(source, _("Resource has no resourceinstance block"))]

        resourceid = instance.get("resourceinstanceid")
        graphid = instance.get("graph_id")
        if not resourceid:
            return [self._failure(source, _("Resource is missing resourceinstanceid"))]
        if not graphid:
            return [
                self._failure(
                    source, _("Resource {} is missing graph_id").format(resourceid)
                )
            ]
        if resourceid in seen_resourceids:
            return [
                self._failure(
                    source,
                    _("Duplicate resourceinstanceid {} within the import").format(
                        resourceid
                    ),
                )
            ]
        seen_resourceids[resourceid] = source

        try:
            graph = self._graph_info(graphid)
        except GraphModel.DoesNotExist:
            return [self._failure(source, _("Graph {} does not exist").format(graphid))]
        except ValueError as unpublished:
            return [self._failure(source, str(unpublished))]

        if instance.get("legacyid"):
            legacyids.setdefault(instance["legacyid"], (resourceid, source))

        bucket = counts.setdefault(graphid, {"resources": 0, "tiles": 0})
        bucket["resources"] += 1

        for tile in resource.get("tiles") or []:
            bucket["tiles"] += 1
            tile_owners[str(tile.get("tileid"))] = (resourceid, source)
            for file_id in self._file_ids(tile.get("data") or {}, graph):
                if file_id in file_owners:
                    failures.append(
                        self._failure(
                            source,
                            _("File {} is used more than once in the import").format(
                                file_id
                            ),
                        )
                    )
                file_owners.setdefault(file_id, (resourceid, source))
            failures.extend(
                self._validate_tile(
                    tile,
                    resourceid,
                    graph,
                    source,
                    constraint_candidates,
                    cardinality_keys,
                )
            )
        return failures

    def _validate_tile(
        self, tile, resourceid, graph, source, constraint_candidates, cardinality_keys
    ):
        failures = []
        nodegroupid = tile.get("nodegroup_id")
        if not nodegroupid:
            return [
                self._failure(
                    source, _("Tile {} has no nodegroup_id").format(tile.get("tileid"))
                )
            ]
        if str(nodegroupid) not in graph["cardinality"]:
            return [
                self._failure(
                    source,
                    _("Nodegroup {} is not in graph {}").format(
                        nodegroupid, graph["graphid"]
                    ),
                )
            ]

        if graph["cardinality"].get(str(nodegroupid)) == "1":
            cardinality_keys.setdefault(
                (resourceid, str(nodegroupid), tile.get("parenttile_id")), []
            ).append(tile.get("tileid"))

        for nodeid, value in (tile.get("data") or {}).items():
            node = graph["nodes"].get(str(nodeid))
            if node is None:
                failures.append(
                    self._failure(
                        source,
                        _("Node {} is not in graph {}").format(
                            nodeid, graph["graphid"]
                        ),
                        nodeid=None,
                        nodegroupid=nodegroupid,
                    )
                )
                continue
            if value is None:
                continue

            if node["datatype"] == "file-list":
                shape_error = self._check_file_list_shape(value)
                if shape_error:
                    failures.append(
                        self._failure(
                            source,
                            shape_error,
                            nodeid=nodeid,
                            nodegroupid=nodegroupid,
                            datatype=node["datatype"],
                            value=value,
                        )
                    )
                    continue

            for error in self._validate_value(node, nodeid, value):
                failures.append(
                    self._failure(
                        source,
                        error.get("title") or _("Invalid value"),
                        message=error.get("message"),
                        nodeid=nodeid,
                        nodegroupid=nodegroupid,
                        datatype=node["datatype"],
                        value=value,
                    )
                )

        self._collect_constraint_candidates(
            tile, resourceid, graph, constraint_candidates
        )
        return failures

    # Validate only, never transform: the source is already a tile value, and
    # transform_value_for_tile would mint new file_ids and orphan the files.
    def _validate_value(self, node, nodeid, value):
        memo_key = None
        if nodeid not in self._memo_disabled_nodes:
            try:
                hash(value)
                memo_key = value
            except TypeError:
                memo_key = json.dumps(value, sort_keys=True, default=str)
            cached = self.validated_data.get(nodeid, {}).get(memo_key)
            if cached is not None:
                return cached

        # Config is splatted in as kwargs so a datatype can validate against it.
        # Node.config is an I18n_JSONField, so an empty config arrives as
        # {"en": ""} and a datatype without a **kwargs sink dies on it.
        config = dict(node["config"] or {})
        config["nodeid"] = nodeid
        try:
            errors = self.datatype_factory.get_instance(node["datatype"]).validate(
                value, **config
            )
        except Exception as e:
            logger.debug("validation raised for node %s: %s", nodeid, e)
            errors = [
                {
                    "title": _("Invalid {} value").format(node["datatype"]),
                    "message": str(e),
                }
            ]

        if memo_key is not None:
            node_memo = self.validated_data.setdefault(nodeid, {})
            if len(node_memo) >= MEMO_MAX_VALUES_PER_NODE:
                self._memo_disabled_nodes.add(nodeid)
                self.validated_data.pop(nodeid, None)
            else:
                node_memo[memo_key] = errors
        return errors

    @staticmethod
    def _check_file_list_shape(value):
        """Reject bare-string localized metadata before it reaches the index."""
        if not isinstance(value, list):
            return _("file-list value must be a list")
        for entry in value:
            if not isinstance(entry, dict):
                return _("file-list entries must be objects")
            if not entry.get("file_id"):
                return _("file-list entry is missing file_id")
            for key in LOCALIZED_FILE_KEYS:
                if key in entry and entry[key] is not None:
                    if not isinstance(entry[key], dict):
                        return _(
                            "file-list '{}' must be a localized object "
                            "({{language: {{value, direction}}}}), not a bare string"
                        ).format(key)
        return None

    # ------------------------------------------------------- graph metadata

    def _graph_info(self, graphid):
        key = str(graphid)
        if key in self._graph_cache:
            return self._graph_cache[key]

        graph = GraphModel.objects.select_related(
            "publication", "resource_instance_lifecycle"
        ).get(pk=graphid)
        if graph.publication_id is None:
            raise ValueError(
                _("Graph '{}' is not published; publish it before importing.").format(
                    graph.name
                )
            )

        nodes = {}
        cardinality = {}
        for node in Node.objects.filter(graph_id=graphid).select_related("nodegroup"):
            if node.nodegroup_id:
                cardinality[str(node.nodegroup_id)] = node.nodegroup.cardinality
            if node.datatype == "semantic":
                continue
            nodes[str(node.nodeid)] = {
                "datatype": node.datatype,
                "config": node.config,
                "nodegroupid": str(node.nodegroup_id) if node.nodegroup_id else None,
            }
        lifecycle_state_id = None
        try:
            lifecycle_state_id = graph.resource_instance_lifecycle.resource_instance_lifecycle_states.get(
                is_initial_state=True
            ).pk
        except (AttributeError, ResourceInstanceLifecycleState.DoesNotExist):
            pass

        info = {
            "graphid": key,
            "nodes": nodes,
            "cardinality": cardinality,
            "publication_id": graph.publication_id,
            "lifecycle_state_id": lifecycle_state_id,
            "constraints": self._constraints_for_nodegroups(cardinality.keys()),
        }
        self._graph_cache[key] = info
        return info

    @staticmethod
    def _constraints_for_nodegroups(nodegroupids):
        """uniquetoallinstances constraints, keyed by nodegroup."""
        from arches.app.models.models import ConstraintModel

        constraints = {}
        for constraint in (
            ConstraintModel.objects.filter(
                card__nodegroup_id__in=list(nodegroupids), uniquetoallinstances=True
            )
            .select_related("card")
            .prefetch_related("nodes")
        ):
            node_ids = sorted(str(n.nodeid) for n in constraint.nodes.all())
            if node_ids:
                constraints.setdefault(str(constraint.card.nodegroup_id), []).append(
                    node_ids
                )
        return constraints

    # ------------------------------------------------- set-based DB checks

    # Only the overwrite=False path reaches the checks below, and a 331k-resource
    # load asks them about ~4.2M tiles -- past Postgres' bind-parameter limit.
    @staticmethod
    def _in_batches(items, size=None):
        # Read at call time, not bound as a default, so a test can shrink it.
        size = size or DB_CHECK_BATCH_SIZE
        items = list(items)
        for start in range(0, len(items), size):
            yield items[start : start + size]

    @staticmethod
    def _collect_constraint_candidates(tile, resourceid, graph, constraint_candidates):
        nodegroupid = str(tile.get("nodegroup_id"))
        for node_ids in graph["constraints"].get(nodegroupid, []):
            data = tile.get("data") or {}
            values = [data.get(nid) for nid in node_ids]
            if any(v is None for v in values):
                continue
            group = constraint_candidates.setdefault((nodegroupid, tuple(node_ids)), {})
            group.setdefault(json.dumps(values, sort_keys=True), []).append(resourceid)

    def _check_global_constraints(self, constraint_candidates):
        failures = []
        for (nodegroupid, node_ids), group in constraint_candidates.items():
            for key, resourceids in group.items():
                if len(resourceids) > 1:
                    failures.append(
                        self._failure(
                            None,
                            _(
                                "Unique constraint violated within the import on "
                                "nodegroup {}: {} resources share a value"
                            ).format(nodegroupid, len(resourceids)),
                            nodegroupid=nodegroupid,
                        )
                    )

            build = ", ".join(["t.tiledata -> %s"] * len(node_ids))
            sql = f"""
                SELECT DISTINCT jsonb_build_array({build})::text, t.resourceinstanceid
                FROM tiles t
                WHERE t.nodegroupid = %s
                  AND jsonb_build_array({build}) IN (
                      SELECT jsonb_array_elements(%s::jsonb)
                  )
            """
            # importing is built from the whole group, not the batch: a
            # colliding resource may sit in a different batch.
            importing = {rid for rids in group.values() for rid in rids}
            collisions = []
            for batch in self._in_batches(group):
                params = (
                    list(node_ids)
                    + [nodegroupid]
                    + list(node_ids)
                    + [json.dumps([json.loads(k) for k in batch])]
                )
                with connection.cursor() as cursor:
                    cursor.execute(sql, params)
                    collisions.extend(cursor.fetchall())

            for raw_key, colliding_resourceid in collisions:
                if self._overwrite and str(colliding_resourceid) in importing:
                    # This resource is being replaced; its own value is not a clash.
                    continue
                failures.append(
                    self._failure(
                        None,
                        _(
                            "Unique constraint violated on nodegroup {}: value "
                            "already exists on resource {}"
                        ).format(nodegroupid, colliding_resourceid),
                        nodegroupid=nodegroupid,
                        value=raw_key,
                    )
                )
        return failures

    def _check_existing_resources(self, resourceids):
        if self._overwrite or not resourceids:
            return []
        existing = [
            pk
            for batch in self._in_batches(resourceids)
            for pk in ResourceInstance.objects.filter(
                resourceinstanceid__in=batch
            ).values_list("resourceinstanceid", flat=True)
        ]
        return [
            self._failure(
                resourceids.get(str(pk)),
                _(
                    "Resource {} already exists. Tick Replace resources that already "
                    "exist to replace it."
                ).format(pk),
            )
            for pk in existing
        ]

    # Both modes: overwrite only clears a resource's own tiles, so a tile id held
    # by a different resource would still collide on insert.
    def _check_existing_tiles(self, tile_owners):
        failures = []
        for batch in self._in_batches(tile_owners):
            for tileid, owner in TileModel.objects.filter(tileid__in=batch).values_list(
                "tileid", "resourceinstance_id"
            ):
                resourceid, source = tile_owners.get(str(tileid), (None, None))
                if str(owner) != str(resourceid):
                    failures.append(
                        self._failure(
                            source,
                            _("Tile {} already belongs to resource {}").format(
                                tileid, owner
                            ),
                        )
                    )
        return failures

    # A load without overwrite must only create, so undoing it can never remove a
    # file that was there before; with overwrite a resource may keep its own files.
    def _check_existing_files(self, file_owners):
        failures = []
        for batch in self._in_batches(file_owners):
            for fileid, owner in File.objects.filter(fileid__in=batch).values_list(
                "fileid", "tile__resourceinstance_id"
            ):
                resourceid, source = file_owners.get(str(fileid), (None, None))
                if self._overwrite and str(owner) == str(resourceid):
                    continue
                failures.append(
                    self._failure(
                        source,
                        _("File {} is already in the database").format(fileid),
                    )
                )
        return failures

    def _check_existing_legacyids(self, legacyids):
        if not legacyids:
            return []
        failures = []
        logger.info(
            "checking %s legacyid(s) against existing resources", len(legacyids)
        )
        existing = [
            row
            for batch in self._in_batches(legacyids)
            for row in ResourceInstance.objects.filter(legacyid__in=batch).values_list(
                "legacyid", "resourceinstanceid"
            )
        ]
        for legacyid, existing_resourceid in existing:
            resourceid, source = legacyids[legacyid]
            if str(existing_resourceid) == str(resourceid):
                continue  # same resource, an update rather than a collision
            failures.append(
                self._failure(
                    source,
                    _("legacyid '{}' already belongs to resource {}").format(
                        legacyid, existing_resourceid
                    ),
                )
            )
        return failures

    def _check_existing_cardinality(self, cardinality_keys):
        failures = []
        wanted = []
        for (
            resourceid,
            nodegroupid,
            parenttileid,
        ), tileids in cardinality_keys.items():
            if len(tileids) > 1:
                failures.append(
                    self._failure(
                        None,
                        _(
                            "Cardinality violation: {} tiles for single-value "
                            "nodegroup {} on resource {}"
                        ).format(len(tileids), nodegroupid, resourceid),
                        nodegroupid=nodegroupid,
                    )
                )
            wanted.append((resourceid, nodegroupid, parenttileid))

        if self._overwrite or not wanted:
            return failures

        # One set-based existence check per batch, not one per resource.
        # parenttileid is compared too: cardinality on a child nodegroup is per
        # parent tile, so ignoring it would reject legitimate sibling tiles.
        logger.info(
            "checking cardinality against existing tiles for %s nodegroup(s)",
            len(wanted),
        )
        for batch in self._in_batches(wanted):
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT t.resourceinstanceid, t.nodegroupid, t.parenttileid
                    FROM unnest(%s::uuid[], %s::uuid[], %s::uuid[])
                         AS w(resourceid, nodegroupid, parenttileid)
                    JOIN tiles t
                      ON t.resourceinstanceid = w.resourceid
                     AND t.nodegroupid = w.nodegroupid
                     AND t.parenttileid IS NOT DISTINCT FROM w.parenttileid
                    """,
                    [
                        [r for r, _ng, _p in batch],
                        [ng for _r, ng, _p in batch],
                        [p for _r, _ng, p in batch],
                    ],
                )
                for resourceid, nodegroupid, parenttileid in cursor.fetchall():
                    failures.append(
                        self._failure(
                            None,
                            _(
                                "Cardinality violation: resource {} already has a "
                                "tile for single-value nodegroup {}"
                            ).format(resourceid, nodegroupid),
                            nodegroupid=nodegroupid,
                        )
                    )
        return failures

    # ------------------------------------------------------ failure recording

    def _failure(
        self,
        source,
        error,
        message=None,
        nodeid=None,
        nodegroupid=None,
        datatype=None,
        value=None,
    ):
        return {
            "source": source,
            "error": error,
            "message": message or error,
            "nodeid": nodeid,
            "nodegroupid": nodegroupid,
            "datatype": datatype,
            "value": value,
        }

    # Only failures are staged: __arches_load_staging_report_errors reads
    # "WHERE passes_validation IS NOT true", so the error-report UI works from
    # these rows alone without a second copy of the passing data.
    def _flush_failures(self, failures):
        if not failures:
            return
        self._demote_unknown_references(failures)
        LoadErrors.objects.bulk_create(
            [
                LoadErrors(
                    load_event_id=self.loadid,
                    nodegroup_id=f["nodegroupid"],
                    node_id=f["nodeid"],
                    type="node" if f["nodeid"] else "tile",
                    source=f["source"] or "",
                    error=f["error"],
                    message=f["message"],
                    datatype=f["datatype"],
                    value=(
                        json.dumps(f["value"])[:4000]
                        if f["value"] is not None
                        else None
                    ),
                )
                for f in failures
            ],
            batch_size=settings.BULK_IMPORT_BATCH_SIZE,
        )
        LoadStaging.objects.bulk_create(
            [
                LoadStaging(
                    load_event_id=self.loadid,
                    nodegroup_id=f["nodegroupid"],
                    value={},
                    passes_validation=False,
                    source_description=f["source"],
                    error_message=f["message"],
                    operation="insert",
                )
                for f in failures
            ],
            batch_size=settings.BULK_IMPORT_BATCH_SIZE,
        )

    # load_errors.nodeid and .nodegroupid are real foreign keys and these ids
    # come from the import file, so an unknown one would fail the *error
    # recording* and lose every other error in the batch with it.
    @staticmethod
    def _demote_unknown_references(failures):
        nodegroupids = {f["nodegroupid"] for f in failures if f["nodegroupid"]}
        nodeids = {f["nodeid"] for f in failures if f["nodeid"]}

        known_nodegroups = set()
        known_nodes = set()
        if nodegroupids:
            known_nodegroups = {
                str(pk)
                for pk in NodeGroup.objects.filter(
                    nodegroupid__in=nodegroupids
                ).values_list("nodegroupid", flat=True)
            }
        if nodeids:
            known_nodes = {
                str(pk)
                for pk in Node.objects.filter(nodeid__in=nodeids).values_list(
                    "nodeid", flat=True
                )
            }

        for failure in failures:
            for key, known, label in (
                ("nodegroupid", known_nodegroups, "nodegroup"),
                ("nodeid", known_nodes, "node"),
            ):
                value = failure[key]
                if value and str(value) not in known:
                    failure[key] = None
                    failure["message"] = "{} ({} {} is not in this database)".format(
                        failure["message"], label, value
                    )

    # ---------------------------------------------------------- framework fit

    # Handled in memory during pass 1; the SQL procedure reads load_staging,
    # which this module leaves empty for passing rows.
    def check_tile_cardinality(self, cursor):
        return None

    def validate(self, loadid):
        return {"success": True, "data": self.get_validation_result(loadid)}

    # ---------------------------------------------------------- pass 2: write

    def save_to_tiles(
        self,
        cursor,
        userid,
        loadid,
        multiprocessing=False,
        max_subprocesses=0,
        index=True,
    ):
        options = self._load_options()
        self._overwrite = bool(options.get("overwrite"))
        # run_load_task passes the request's choice; the Celery path cannot, so
        # the one stored by start() counts too.
        index = index and options.get("index", True)
        chunk_size = settings.BULK_IMPORT_BATCH_SIZE
        # edit_log.newvalue duplicates the tile data (~0.9KB/tile; ~4GB on a
        # 4.5M-tile load).  Reversal never reads it -- reverse_edit_log_entries
        # deletes on 'create'/'tile create' and only reads oldvalue on
        # 'tile edit' -- so it is off unless the audit copy is wanted.
        log_tile_values = bool(self.config.get("logTileValues", False))

        if not self._acquire_trigger_lock(cursor):
            contention = _(
                "Another bulk load is already running; only one may hold the "
                "tile triggers at a time."
            )
            LoadEvent.objects.filter(loadid=loadid).update(
                status="failed", load_end_time=timezone.now(), error_message=contention
            )
            return {
                "success": False,
                "data": {
                    "title": _("Another bulk load is running"),
                    "message": _(
                        "Tile triggers are disabled database-wide during a bulk load, "
                        "so only one may run at a time. Try again when it finishes."
                    ),
                },
            }

        try:
            log_event_details(cursor, loadid, "done|Saving the tiles...")
            # The etl-manager badge reads load_event.status alone, and "running"
            # renders as "Validating".
            LoadEvent.objects.filter(loadid=loadid).update(status="validated")
            disable_tile_triggers(cursor, loadid)
            try:
                written = 0
                for chunk in self._iter_resource_chunks(chunk_size):
                    written += self._write_chunk(chunk, loadid, log_tile_values)
                logger.info("arches_json_importer wrote %s resources", written)

                log_event_details(cursor, loadid, "done|Refreshing relationships...")
                self._post_process(loadid)
            finally:
                reenable_tile_triggers(cursor, loadid)
        except Exception as e:
            logger.exception(e)
            # This branch returns a dict rather than raising, so nothing else
            # records the reason and the report reads "no errors found".
            LoadEvent.objects.filter(loadid=loadid).update(
                status="failed", load_end_time=timezone.now(), error_message=str(e)
            )
            return {
                "success": False,
                "data": {"title": _("Failed to complete load"), "message": str(e)},
            }
        finally:
            self._release_trigger_lock(cursor)

        # "completed" is the badge's "Indexing" state; _post_save_edit_log
        # takes it to "indexed" (or "unindexed" if indexing fails).
        LoadEvent.objects.filter(loadid=loadid).update(
            status="completed", load_end_time=timezone.now()
        )
        response = _post_save_edit_log(
            userid, loadid, multiprocessing, max_subprocesses, index=index
        )

        # _post_save_edit_log stamps its finish through raw SQL with a naive
        # datetime, which lands an hour out from the ORM-written start under BST.
        stamped = (
            "indexed_time" if response.get("data") == "indexed" else "load_end_time"
        )
        LoadEvent.objects.filter(loadid=loadid).update(**{stamped: timezone.now()})
        return response

    # Chunks break on resource boundaries: the tile FKs are DEFERRABLE INITIALLY
    # DEFERRED, so a whole resource needs no parent-before-child ordering, but a
    # resource split across two transactions would fail.
    def _iter_resource_chunks(self, chunk_size):
        chunk = []
        for filename in self._source_paths:
            for resource in self._iter_resources(filename):
                chunk.append(resource)
                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []
        if chunk:
            yield chunk

    def _write_chunk(self, chunk, loadid, log_tile_values):
        now = timezone.now()
        resources, tiles, created, edits = [], [], [], []
        resourceids, file_ids = [], []

        for resource in chunk:
            instance = resource["resourceinstance"]
            resourceid = uuid.UUID(str(instance["resourceinstanceid"]))
            graphid = str(instance["graph_id"])
            graph = self._graph_info(graphid)
            resourceids.append(resourceid)

            resources.append(
                ResourceInstance(
                    resourceinstanceid=resourceid,
                    graph_id=graphid,
                    legacyid=instance.get("legacyid"),
                    # staging_to_tile leaves this null; without it
                    # reverse_edit_log_entries raises "Graph Has Different
                    # Publication" and the load cannot be undone.
                    graph_publication_id=graph["publication_id"],
                    resource_instance_lifecycle_state_id=graph["lifecycle_state_id"],
                )
            )
            created.append(
                EditLog(
                    resourceclassid=graphid,
                    resourceinstanceid=str(resourceid),
                    edittype="create",
                    timestamp=now,
                    note="loaded from arches json",
                    transactionid=loadid,
                )
            )

            for tile in resource.get("tiles") or []:
                tileid = uuid.UUID(str(tile["tileid"]))
                data = tile.get("data") or {}
                if self._overwrite:
                    file_ids.extend(self._file_ids(data, graph))
                tiles.append(
                    TileModel(
                        tileid=tileid,
                        resourceinstance_id=resourceid,
                        parenttile_id=(
                            uuid.UUID(str(tile["parenttile_id"]))
                            if tile.get("parenttile_id")
                            else None
                        ),
                        nodegroup_id=tile["nodegroup_id"],
                        sortorder=tile.get("sortorder") or 0,
                        data=data,
                    )
                )
                edits.append(
                    EditLog(
                        resourceclassid=graphid,
                        resourceinstanceid=str(resourceid),
                        nodegroupid=str(tile["nodegroup_id"]),
                        tileinstanceid=str(tileid),
                        edittype="tile create",
                        newvalue=data if log_tile_values else None,
                        timestamp=now,
                        note="loaded from arches json",
                        transactionid=loadid,
                    )
                )

        # One transaction per chunk: the deferred FKs resolve at commit, and the
        # edit_log rows land with the tiles so a crashed load always reverses to
        # exactly what was written.
        with transaction.atomic():
            if self._overwrite:
                existing = {
                    str(pk)
                    for pk in ResourceInstance.objects.filter(
                        resourceinstanceid__in=resourceids
                    ).values_list("resourceinstanceid", flat=True)
                }
                created = [e for e in created if e.resourceinstanceid not in existing]
                self._clear_replaced_tiles(
                    loadid, resourceids, [t.tileid for t in tiles], file_ids
                )
                ResourceInstance.objects.bulk_create(
                    resources,
                    update_conflicts=True,
                    unique_fields=["resourceinstanceid"],
                    update_fields=[
                        "graph",
                        "legacyid",
                        "graph_publication",
                        "resource_instance_lifecycle_state",
                    ],
                )
            else:
                ResourceInstance.objects.bulk_create(resources)
            TileModel.objects.bulk_create(tiles)
            EditLog.objects.bulk_create(created + edits)
        return len(resources)

    @staticmethod
    def _file_ids(data, graph):
        file_ids = []
        for nodeid, value in data.items():
            if graph["nodes"].get(nodeid, {}).get("datatype") != "file-list":
                continue
            for item in value or []:
                if isinstance(item, dict) and item.get("file_id"):
                    file_ids.append(str(item["file_id"]))
        return file_ids

    # Overwrite replaces a resource's tiles, never the resource itself: deleting
    # the resource would cascade away links into it from resources outside the load.
    @staticmethod
    def _clear_replaced_tiles(loadid, resourceids, tileids, file_ids):
        old_tiles = (
            "SELECT tileid FROM tiles WHERE resourceinstanceid = ANY(%s::uuid[])"
        )
        ids = [str(r) for r in resourceids]
        with connection.cursor() as cursor:
            # Only tiles the file no longer has: a kept tile is re-inserted and logged
            # as created, and two rows for one tile in a load would make
            # _post_process, which joins edit_log on the transaction, see it twice.
            cursor.execute(
                """
                INSERT INTO edit_log (resourceclassid, resourceinstanceid, nodegroupid,
                                      tileinstanceid, edittype, timestamp, note,
                                      transactionid)
                SELECT r.graphid::text, t.resourceinstanceid::text, t.nodegroupid::text,
                       t.tileid::text, 'tile delete', now(),
                       'removed by arches json overwrite', %s
                FROM tiles t
                JOIN resource_instances r USING (resourceinstanceid)
                WHERE t.resourceinstanceid = ANY(%s::uuid[])
                  AND t.tileid <> ALL(%s::uuid[])
                """,
                [loadid, ids, [str(t) for t in tileids]],
            )
            # Keeps the row, with its real path and thumbnail, of a file the import
            # uses again; _post_process points it at the new tile.
            cursor.execute(
                f"UPDATE files SET tileid = NULL WHERE tileid IN ({old_tiles}) "
                "AND fileid = ANY(%s::uuid[])",
                [ids, file_ids],
            )
            for table in ("resource_x_resource", "geojson_geometries", "files"):
                cursor.execute(
                    f"DELETE FROM {table} WHERE tileid IN ({old_tiles})", [ids]
                )
            cursor.execute(
                "DELETE FROM tiles WHERE resourceinstanceid = ANY(%s::uuid[])", [ids]
            )

    # ------------------------------------------------- set-based postprocess

    def _post_process(self, loadid):
        with transaction.atomic(), connection.cursor() as cursor:
            # Create any missing File rows and point them at their tile.  This
            # is what FileListDataType.pre_tile_save does one row at a time --
            # and it must run *after* the tiles exist, which is why this module
            # never calls that hook.
            cursor.execute(
                """
                INSERT INTO files (fileid, path, tileid)
                SELECT (f->>'file_id')::uuid,
                       %s || '/' || (f->>'name'),
                       t.tileid
                FROM tiles t
                JOIN edit_log el
                  ON el.tileinstanceid::uuid = t.tileid AND el.transactionid = %s
                JOIN nodes n
                  ON n.nodegroupid = t.nodegroupid AND n.datatype = 'file-list'
                CROSS JOIN LATERAL jsonb_array_elements(t.tiledata -> n.nodeid::text) f
                WHERE jsonb_typeof(t.tiledata -> n.nodeid::text) = 'array'
                  AND f->>'file_id' IS NOT NULL
                ON CONFLICT (fileid) DO UPDATE SET tileid = EXCLUDED.tileid
                """,
                [settings.UPLOADED_FILES_DIR, loadid],
            )
            cursor.execute(
                "SELECT __arches_refresh_transaction_resource_relationships(%s)",
                [loadid],
            )
            # ponytail: one statement over every geojson tile in the load.  If a
            # 300k load makes this the bottleneck, chunk it by resource-id range.
            cursor.execute(
                "SELECT refresh_transaction_geojson_geometries(%s)", [loadid]
            )

    # ------------------------------------------------------------ concurrency

    @staticmethod
    def _acquire_trigger_lock(cursor):
        cursor.execute("SELECT pg_try_advisory_lock(%s)", [TILE_TRIGGER_LOCK_KEY])
        return cursor.fetchone()[0]

    @staticmethod
    def _release_trigger_lock(cursor):
        try:
            cursor.execute("SELECT pg_advisory_unlock(%s)", [TILE_TRIGGER_LOCK_KEY])
        except Exception:
            logger.warning("Could not release the bulk-load advisory lock")

    # ---------------------------------------------------------------- reverse

    # Core undoes a load by deleting what its edit log says it created. An overwrite
    # load also replaced tiles that no longer exist, so undoing it would leave the
    # resources it replaced empty rather than restore them.
    @method_decorator(user_created_transaction_match, name="dispatch")
    def reverse(self, request, **kwargs):
        loadid = self.loadid or request.POST.get("loadid")
        if self._load_options(loadid).get("overwrite"):
            return {
                "success": False,
                "data": {
                    "title": _("Cannot undo this load"),
                    "message": _(
                        "An overwrite load cannot be undone: the tiles it replaced "
                        "no longer exist."
                    ),
                },
            }
        return super().reverse(request, **kwargs)

    # ------------------------------------------------------------------ async

    @load_data_async
    def run_load_task_async(self, request):
        import arches.app.tasks as tasks

        details = json.loads(self.file_details)
        summary = details["result"]["summary"]
        load_task = tasks.load_arches_json.apply_async(
            (
                self.userid,
                summary["files"],
                summary,
                {},
                self.temp_dir,
                self.loadid,
                self.moduleid,
            ),
        )
        LoadEvent.objects.filter(loadid=self.loadid).update(taskid=load_task.task_id)
