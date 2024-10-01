import json
import logging
import zipfile
from datetime import datetime
from functools import cache, lru_cache
from pathlib import Path

from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.db import transaction
from django.utils.translation import gettext as _

from arches.app.etl_modules.save import (
    _save_to_tiles,
    disable_tile_triggers,
    reenable_tile_triggers,
    _post_save_edit_log,
)
from arches.app.tasks import load_json_ld
from arches.app.utils.data_management.resources.formats.rdffile import (
    ValueErrorWithNodeInfo,
)
from arches.app.etl_modules.base_import_module import (
    BaseImportModule,
    FileValidationError,
)
from arches.app.etl_modules.decorators import load_data_async
from arches.app.models.models import (
    GraphModel,
    LoadErrors,
    LoadEvent,
    LoadStaging,
    Node,
    ResourceInstance,
)
from arches.app.models.system_settings import settings
from arches.app.utils.file_validator import FileValidator

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_graph_tree_from_slug(slug):
    """Resources are ordered by graph, so use an aggressively low maxsize."""
    graph_id = graph_id_from_slug(slug)
    return BaseImportModule().get_graph_tree(graph_id)


@lru_cache(maxsize=1)
def graph_id_from_slug(slug):
    return GraphModel.objects.get(slug=slug).pk


@cache
def fallback_node():
    """Consider removing this if we make LoadStaging.nodegroup nullable."""
    return Node.objects.filter(nodegroup__isnull=False).first()


class RedirectStdoutToLogger:
    def write(self, msg):
        if msg:
            logger.info(msg)

    def flush(self):
        pass


class RedirectStderrToLogger:
    def write(self, msg):
        if msg:
            logger.error(msg)

    def flush(self):
        pass


class JSONLDImporter(BaseImportModule):
    def read(self, request):
        self.prepare_temp_dir(request)
        self.cumulative_files_size = 0
        content = request.FILES["file"]

        result = {
            "summary": {
                "name": content.name,
                "size": self.filesize_format(content.size),
                "files": {},
            }
        }
        validator = FileValidator()
        if file_type_errors := validator.validate_file_type(content):
            return {
                "success": False,
                "data": FileValidationError(
                    message=", ".join(file_type_errors),
                    code=400,
                ),
            }

        file_validation_error = None
        try:
            self.read_zip_file(content, result)
        except zipfile.BadZipFile as e1:
            file_validation_error = FileValidationError(message=e1.args[0], code=400)
        except FileValidationError as e2:
            file_validation_error = e2
        if file_validation_error:
            return {"success": False, "data": file_validation_error}

        if not result["summary"]["files"]:
            title = _("Invalid Uploaded File")
            message = _(
                "This file has missing information or invalid formatting. Make sure the file is complete and in the expected format."
            )
            return {"success": False, "data": {"title": title, "message": message}}

        return {"success": True, "data": result}

    def read_zip_file(self, content, result):
        with zipfile.ZipFile(content, "r") as zip_ref:
            files = zip_ref.infolist()
            for file in files:
                if file.filename.split(".")[-1] != "json":
                    continue
                if file.filename.startswith("__MACOSX"):
                    continue
                if file.is_dir():
                    continue
                self.cumulative_files_size += file.file_size
                result["summary"]["files"][file.filename] = {
                    "size": (self.filesize_format(file.file_size))
                }
                result["summary"]["cumulative_files_size"] = self.cumulative_files_size
                with zip_ref.open(file) as opened_file:
                    self.validate_uploaded_file(opened_file)
                    f = File(opened_file)

                    # Discard outermost part ("e.g. myzip/")
                    destination = Path(self.temp_dir)
                    for part in Path(file.filename).parts[1:]:
                        destination = destination / part

                    default_storage.save(destination, f)

    def validate_uploaded_file(self, file):
        path = Path(file.name)
        slug = path.parts[1]
        try:
            graph_id_from_slug(slug)
        except GraphModel.DoesNotExist:
            raise FileValidationError(
                code=404, message=_('The model "{0}" does not exist.').format(slug)
            )

    def stage_files(self, files, summary, cursor):
        for file in files:
            path = Path(file)
            unused, graph_slug, block, resource_id_with_suffix = path.parts
            resource_id = resource_id_with_suffix.split(".json")[0]

            self.handle_block(graph_slug, block)

            summary["files"][file]["resources"] = [resource_id]

        cursor.execute(
            """UPDATE load_event SET load_details = %s WHERE loadid = %s""",
            (json.dumps(summary), self.loadid),
        )

        # Clear cache in case the user edits the last graph and re-runs.
        get_graph_tree_from_slug.cache_clear()
        graph_id_from_slug.cache_clear()

    def handle_block(self, graph_slug, block):
        try:
            resources = call_command(
                "load_jsonld",
                stdout=RedirectStdoutToLogger(),
                stderr=RedirectStderrToLogger(),
                model=graph_slug,
                block=block,
                force="overwrite",
                source=self.temp_dir,
                quiet=True,
                fast=True,
                use_storage=True,
                dry_run=True,  # don't save the resources
            )
        except Exception as e:
            self.handle_early_failure(e, graph_slug=graph_slug, block=block)
            return

        nodegroup_info, _nodes = get_graph_tree_from_slug(graph_slug)
        self.populate_staging_table(resources, nodegroup_info)

    def populate_staging_table(self, resources, nodegroup_info):
        load_staging_instances = []
        for resource in resources:
            for tile in resource.get_flattened_tiles():
                load_staging_instances.append(
                    self.load_staging_instance_from_tile(tile, resource, nodegroup_info)
                )

        tile_batch_size = (
            settings.BULK_IMPORT_BATCH_SIZE * 10
        )  # assume 10 tiles/resource
        LoadStaging.objects.bulk_create(
            load_staging_instances, batch_size=tile_batch_size
        )

    def handle_early_failure(self, exception, graph_slug, block):
        """The CLI might have failed well before creating resources and tiles,
        but still with some useful information we can surface."""

        has_info = isinstance(exception, ValueErrorWithNodeInfo)
        early_failure = _("Load JSON-LD command failed before fully parsing a block.")
        exception_message = exception.args[0]

        if hasattr(exception, "__notes__"):
            source = exception.__notes__[0]
        else:
            source = "/".join((graph_slug, block))

        le = LoadErrors(
            load_event_id=self.loadid,
            type="JSON-LD block",
            source=source,
            error=early_failure,
            message=exception_message,
            value=str(exception.value) if has_info else None,
            datatype=exception.datatype if has_info else None,
            node_id=exception.node_id if has_info else fallback_node().nodeid,
            nodegroup_id=(
                exception.nodegroup_id if has_info else fallback_node().nodegroup_id
            ),
        )
        le.clean_fields()
        le.save()

        # Avoid save() to prevent IntegrityError: https://code.djangoproject.com/ticket/35425
        LoadEvent.objects.filter(loadid=self.loadid).update(
            user_id=self.userid,
            successful=False,
            status="failed",
            load_description=source,
            etl_module_id=self.moduleid,
            error_message=early_failure,
            load_end_time=datetime.now(),
        )

        dummy_tile_info = {
            str(le.node_id or fallback_node().nodeid): {
                "value": {},
                "valid": False,
                "source": early_failure,
                "notes": exception_message,
                "datatype": "",
            }
        }

        ls = LoadStaging(
            load_event_id=self.loadid,
            nodegroup_id=(
                exception.nodegroup_id if has_info else fallback_node().nodegroup_id
            ),
            value=dummy_tile_info,
            passes_validation=False,
            source_description=early_failure,
            error_message=exception_message,
            operation="insert",
        )
        ls.clean_fields()
        ls.save()

    def load_staging_instance_from_tile(self, tile, resource, nodegroup_info):
        tile_info = {}
        for nodeid, source_value in tile.data.items():
            datatype = nodegroup_info[nodeid]["datatype"]
            datatype_instance = self.datatype_factory.get_instance(datatype)
            config = nodegroup_info[nodeid]["config"]
            config["path"] = self.temp_dir
            config["loadid"] = self.loadid
            value, validation_errors = self.prepare_data_for_loading(
                datatype_instance,
                source_value,
                config,
            )
            passes_validation = len(validation_errors) == 0
            self.save_validation_errors(
                validation_errors, tile, source_value, datatype_instance, nodeid
            )

            tile_info[nodeid] = {
                "value": value,
                "valid": passes_validation,
                "source": source_value,
                "notes": "|".join(validation_errors),
                "datatype": datatype,
            }

        ls = LoadStaging(
            nodegroup_id=tile.nodegroup_id,
            load_event_id=self.loadid,
            value=tile_info,
            legacyid=resource.legacyid,
            resourceid=resource.pk,
            tileid=tile.pk,
            parenttileid=tile.parenttile_id,
            passes_validation=passes_validation,
            nodegroup_depth=nodegroup_info[nodeid]["depth"],
            source_description=None,
            error_message=None,
            operation="insert",
        )
        ls.clean_fields()
        return ls

    def save_validation_errors(
        self, validation_errors, tile, source_value, datatype, nodeid
    ):
        for error in validation_errors:
            le = LoadErrors(
                load_event_id=self.loadid,
                nodegroup_id=tile.nodegroup_id,
                node_id=nodeid,
                datatype=datatype.pk,
                type="node",
                value=source_value,
                source="",
                error=error["title"],
                message=error["message"],
            )
            le.clean_fields()
            le.save()

    def check_tile_cardinality(self, cursor):
        # Do this later, after any prior resources have been deleted.
        return None

    def save_to_tiles(self, cursor, userid, loadid, multiprocessing=False):
        error_saving_tiles = None

        # Disable the tile triggers early, because below we wrap resource
        # deletion in a transaction. Avoids "pending trigger events..." error.
        disable_tile_triggers(cursor, loadid)

        try:
            with transaction.atomic():
                # Prepare for possible resource overwriting
                ResourceInstance.objects.filter(
                    pk__in=LoadStaging.objects.filter(load_event_id=self.loadid).values(
                        "resourceid"
                    )
                ).delete()

                # Now we can check tile cardinality.
                super().check_tile_cardinality(cursor)

                error_saving_tiles = _save_to_tiles(cursor, loadid)
                if error_saving_tiles:
                    # Revert transaction.
                    raise RuntimeError
        except:
            return error_saving_tiles
        finally:
            reenable_tile_triggers(cursor, loadid)

        return _post_save_edit_log(cursor, userid, loadid)

    @load_data_async
    def run_load_task_async(self, request):
        details = json.loads(self.file_details)
        summary = details["result"]["summary"]
        files = details["result"]["summary"]["files"]
        result = {}

        load_task = load_json_ld.apply_async(
            (
                self.userid,
                files,
                summary,
                result,
                self.temp_dir,
                self.loadid,
                self.moduleid,
            ),
        )
        LoadEvent.objects.filter(loadid=self.loadid).update(taskid=load_task.task_id)
