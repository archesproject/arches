import json
import zipfile
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.utils.translation import gettext as _

from arches.app.etl_modules.base_import_module import BaseImportModule, FileValidationError
from arches.app.etl_modules.decorators import load_data_async
from arches.app.models.models import GraphModel, LoadErrors, LoadEvent, LoadStaging
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.file_validator import FileValidator


@lru_cache(maxsize=1)
def get_graph_tree_from_slug(graph_id):
    """Resources are ordered by graph, so use an aggressively low maxsize."""
    return BaseImportModule().get_graph_tree(graph_id)


@lru_cache(maxsize=1)
def graph_id_from_slug(slug):
    return GraphModel.objects.get(slug=slug).pk


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
        if validator.validate_file_type(content):
            return {
                "status": 400,
                "success": False,
                "title": _("Invalid Uploaded File"),
                "message": _("Upload a valid zip file"),
            }

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
                result["summary"]["files"][file.filename] = {"size": (self.filesize_format(file.file_size))}
                result["summary"]["cumulative_files_size"] = self.cumulative_files_size
                with zip_ref.open(file) as opened_file:
                    self.validate_uploaded_file(opened_file)
                    f = File(opened_file)

                    # Discard outermost part ("e.g. myzip/")
                    destination = Path(self.temp_dir)
                    for part in Path(file.filename).parts[1:]:
                        destination = destination / part

                    default_storage.save(destination, f)

        if not result["summary"]["files"]:
            title = _("Invalid Uploaded File")
            message = _("This file has missing information or invalid formatting. Make sure the file is complete and in the expected format.")
            return {"success": False, "data": {"title": title, "message": message}}

        return {"success": True, "data": result}

    def validate_uploaded_file(self, file):
        path = Path(file.name)
        slug = path.parts[1]
        try:
            graph_id_from_slug(slug)
        except GraphModel.ObjectDoesNotExist:
            raise FileValidationError(
                code=404,
                message=_('The model "{0}" does not exist.').format(slug)
            )

    def stage_files(self, files, summary, cursor):
        for file in files:
            path = Path(file)
            unused, graph_slug, block, resource_id_with_suffix = path.parts
            resource_id = resource_id_with_suffix.split(".json")[0]

            self.handle_block(graph_slug, block)

            summary["files"][file]["resources"].append(resource_id)

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
            LoadErrors(
                load_event_id=self.loadid,
                type="graph",
                source="/".join((graph_slug, block)),
                error=_("Load JSON-LD command error"),
                message=e.args[0],
            ).save()
            # Prevent IntegrityError: https://code.djangoproject.com/ticket/35425
            LoadEvent.objects.filter(loadid=self.loadid).update(
                user_id=self.userid,
                successful=False,
                status="failed",
                load_description="/".join((graph_slug, block)),
                etl_module_id=self.moduleid,
                error_message=_("Load JSON-LD command error"),
                load_end_time=datetime.now(),
            )
            raise

        nodegroup_info, node_info = get_graph_tree_from_slug(graph_slug)
        self.populate_staging_table(resources, nodegroup_info, node_info)

    def populate_staging_table(self, resources, nodegroup_info, node_info):
        load_staging_instances = []
        for resource in resources:
            for tile in resource.get_flattened_tiles():
                load_staging_instances.append(
                    self.load_staging_instance_from_tile(tile, resource, nodegroup_info, node_info)
                )

        tile_batch_size = settings.BULK_IMPORT_BATCH_SIZE * 10  # assume 10 tiles/resource
        LoadStaging.objects.bulk_create(load_staging_instances, batch_size=tile_batch_size)
        # todo(jtw): edit log?

    def load_staging_instance_from_tile(self, tile, resource, nodegroup_info, node_info):
        tile_value = {}
        for nodeid, source_value in tile.data.entries():
            datatype = node_info[nodeid]["datatype"]
            config = node_info[nodeid]["config"]
            value, validation_errors = self.prepare_data_for_loading(
                datatype,
                source_value,
                config,
            )
            self.save_validation_errors(validation_errors, tile, source_value, datatype, nodeid)

            tile_value[nodeid] = {
                "value": value,
                "valid": len(validation_errors) == 0,
                "source": source_value,
                "notes": ",".join(validation_errors),
                "datatype": datatype,
            }

            return LoadStaging(
                nodegroup_id=tile.nodegroup_id,
                load_event_id=self.loadid,
                value=JSONSerializer().serialize(tile_value),
                legacyid=resource.legacyid,
                resourceid=resource.pk,
                tileid=tile.pk,
                parenttileid=tile.parenttile_id,
                passes_validation=True,
                nodegroup_depth=nodegroup_info[tile.nodegroup_id].depth,
                source_description=None,
                error_message=None,
                operation="insert",
            )

    def save_validation_errors(self, validation_errors, tile, source_value, datatype, nodeid):
        for error in validation_errors:
            LoadErrors(
                load_event_id=self.loadid,
                nodegroup_id=tile.nodegroup_id,
                node_id=nodeid,
                datatype=datatype.pk,
                type="node",
                value=source_value,
                source="",
                error=error["title"],
                message=error["message"],
            ).save()

    @load_data_async
    def run_load_task_async(self, request):
        raise NotImplementedError
