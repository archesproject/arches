import importlib
import os
import logging
import shutil
from celery import shared_task
from datetime import datetime
from datetime import timedelta
from django.contrib.auth.models import User
from django.core import management
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.http import HttpRequest
from django.utils.translation import gettext as _
from arches.app.models import models
from arches.app.utils import import_class_from_string
from arches.app.utils.message_contexts import return_message_context
from tempfile import NamedTemporaryFile


@shared_task
def delete_file():
    from arches.app.models.system_settings import settings

    settings.update_from_db()

    logger = logging.getLogger(__name__)
    file_list = []
    range = datetime.now() - timedelta(seconds=settings.CELERY_SEARCH_EXPORT_EXPIRES)
    exports = models.SearchExportHistory.objects.filter(exporttime__lt=range).exclude(
        downloadfile=""
    )
    for export in exports:
        file_list.append(export.downloadfile.url)
        export.downloadfile.delete()
    deleted_message = _("files_deleted")
    logger.warning(f"{len(file_list)} {deleted_message}")
    return f"{len(file_list)} {deleted_message}"


@shared_task
def message(arg):
    return arg


@shared_task(bind=True)
def export_search_results(self, userid, request_values, format, report_link):
    from arches.app.search.search_export import SearchResultsExporter
    from arches.app.models.system_settings import settings

    logger = logging.getLogger(__name__)
    settings.update_from_db()

    create_user_task_record(self.request.id, self.name, userid)
    _user = User.objects.get(id=userid)
    try:
        email = request_values["email"]
    except KeyError:
        email = None
    try:
        export_name = request_values["exportName"][0]
    except KeyError:
        export_name = None
    new_request = HttpRequest()
    new_request.method = "GET"
    new_request.user = _user
    for k, v in request_values.items():
        new_request.GET.__setitem__(k, v[0])
    new_request.path = request_values["path"]
    if format == "tilexl":
        exporter = SearchResultsExporter(search_request=new_request)
        export_files, export_info = exporter.export(format, report_link)
        wb = export_files[0]["outputfile"]
        try:
            with NamedTemporaryFile(delete=False) as tmp:
                wb.save(tmp.name)
                tmp.seek(0)
                stream = tmp.read()
                export_files[0]["outputfile"] = tmp
                exportid = exporter.write_export_zipfile(
                    export_files, export_info, export_name
                )
        except OSError:
            logger.error("Temp file could not be created.")
            raise
        os.unlink(tmp.name)
    else:
        exporter = SearchResultsExporter(search_request=new_request)
        files, export_info = exporter.export(format, report_link)
        exportid = exporter.write_export_zipfile(files, export_info, export_name)

    search_history_obj = models.SearchExportHistory.objects.get(pk=exportid)

    expiration_date = datetime.now() + timedelta(
        seconds=settings.CELERY_SEARCH_EXPORT_EXPIRES
    )
    formatted_expiration_date = expiration_date.strftime("%A, %d %B %Y")

    context = return_message_context(
        greeting=_(
            "Hello,\nYour request to download a set of search results is now ready. You have until {} to access this download, after which time it'll be deleted.".format(
                formatted_expiration_date
            )
        ),
        closing_text=_("Thank you"),
        email=email,
        additional_context={
            "link": str(exportid),
            "button_text": _("Download Now"),
            "name": export_name,
            "email_link": str(settings.PUBLIC_SERVER_ADDRESS).rstrip("/")
            + "/files/"
            + str(exportid),
            "username": _user.first_name or _user.username,
        },
    )

    return {
        "taskid": self.request.id,
        "msg": _(
            "Your search '{}' is ready for download. You have until {} to access this file, after which we'll automatically remove it.".format(
                export_name, formatted_expiration_date
            )
        ),
        "notiftype_name": "Search Export Download Ready",
        "context": context,
    }


@shared_task(bind=True)
def refresh_geojson_geometries(self):
    with connection.cursor() as cursor:
        sql = """
            SELECT * FROM refresh_geojson_geometries();
        """
        cursor.execute(sql)
    response = {"taskid": self.request.id}


@shared_task(bind=True)
def import_business_data(
    self,
    data_source="",
    overwrite="",
    bulk_load=False,
    create_concepts=False,
    create_collections=False,
    prevent_indexing=False,
):
    management.call_command(
        "packages",
        operation="import_business_data",
        source=data_source,
        bulk_load=bulk_load,
        overwrite=overwrite,
        prevent_indexing=prevent_indexing,
    )


@shared_task(bind=True)
def index_resource(self, module, index_name, resource_id, tile_ids):
    from arches.app.models.resource import Resource  # avoids circular import

    resource = Resource.objects.get(pk=resource_id)
    tiles = [models.TileModel.objects.get(pk=tile_id) for tile_id in tile_ids]

    es_index = import_class_from_string(module)(index_name)
    document, document_id = es_index.get_documents_to_index(resource, tiles)

    return es_index.index_document(document=document, id=document_id)


@shared_task
def package_load_complete(*args, **kwargs):
    valid_resource_paths = kwargs.get("valid_resource_paths")

    msg = _("Resources have completed loading.")
    notifytype_name = "Package Load Complete"
    user = User.objects.get(id=1)
    context = return_message_context(
        greeting=_(
            "Hello,\nYour package has successfully loaded into your Arches project."
        ),
        closing_text=_("Thank you"),
        email=user.email,
        additional_context={
            "link": "",
            "loaded_resource": [
                os.path.basename(os.path.normpath(resource_path))
                for resource_path in valid_resource_paths
            ],
            "link_text": _("Log me in"),
        },
    )
    notify_completion(msg, user, notifytype_name, context)


@shared_task
def update_user_task_record(arg_dict={}):
    taskid = arg_dict["taskid"]
    msg = arg_dict.get("msg", None)
    if "notiftype_name" in list(arg_dict.keys()):
        notiftype_name = arg_dict["notiftype_name"]
    else:
        notiftype_name = None
    if "context" in list(arg_dict.keys()):
        context = arg_dict["context"]
    else:
        context = None
    task_obj = models.UserXTask.objects.get(taskid=taskid)
    task_obj.status = "SUCCESS"
    task_obj.datedone = datetime.now()
    task_obj.save()
    if notiftype_name is not None:
        if msg is None:
            msg = task_obj.status + ": " + task_obj.name
        notify_completion(msg, task_obj.user, notiftype_name, context)


@shared_task
def log_error(request, exc, traceback, msg=None):
    logger = logging.getLogger(__name__)
    logger.warning(exc)
    try:
        task_obj = models.UserXTask.objects.get(taskid=request.id)
        task_obj.status = "ERROR"
        task_obj.date_done = datetime.now()
        task_obj.save()
        if msg is None:
            msg = task_obj.status + ": " + task_obj.name
        notify_completion(msg, task_obj.user)
    except ObjectDoesNotExist:
        print("No such UserXTask record exists. Notification aborted.")


@shared_task
def on_chord_error(request, exc, traceback):
    logger = logging.getLogger(__name__)
    logger.warning(exc)
    logger.warning(traceback)
    msg = f"Package Load erred on import_business_data. Exception: {exc}. See logs for details."
    user = User.objects.get(id=1)
    notify_completion(msg, user)


def load_excel_data(
    import_module, importer_name, userid, files, summary, result, temp_dir, loadid
):
    logger = logging.getLogger(__name__)
    try:
        import_module.run_load_task(userid, files, summary, result, temp_dir, loadid)

        load_event = models.LoadEvent.objects.get(loadid=loadid)
        status = _("Completed") if load_event.status == "indexed" else _("Failed")
    except Exception as e:
        logger.error(e)
        load_event = models.LoadEvent.objects.get(loadid=loadid)
        load_event.status = "failed"
        load_event.save()
        status = _("Failed")
    finally:
        msg = _("{}: {} [{}]").format(importer_name, summary["name"], status)
        user = User.objects.get(id=userid)
        notify_completion(msg, user)


@shared_task
def load_branch_excel(userid, files, summary, result, temp_dir, loadid):
    from arches.app.etl_modules import branch_excel_importer

    BranchExcelImporter = branch_excel_importer.BranchExcelImporter(
        request=None, loadid=loadid, temp_dir=temp_dir
    )
    load_excel_data(
        BranchExcelImporter,
        "Branch Excel Import",
        userid,
        files,
        summary,
        result,
        temp_dir,
        loadid,
    )


@shared_task
def load_tile_excel(userid, files, summary, result, temp_dir, loadid):
    from arches.app.etl_modules import tile_excel_importer

    TileExcelImporter = tile_excel_importer.TileExcelImporter(
        request=None, loadid=loadid, temp_dir=temp_dir
    )
    load_excel_data(
        TileExcelImporter,
        "Tile Excel Import",
        userid,
        files,
        summary,
        result,
        temp_dir,
        loadid,
    )


@shared_task
def export_excel_data(
    import_module,
    user_id,
    load_id,
    graph_id,
    graph_name,
    resource_ids,
    export_concepts_as=None,
    filename=None,
):
    logger = logging.getLogger(__name__)

    status = _("Failed")
    try:
        import_module.run_export_task(
            load_id,
            graph_id,
            graph_name,
            resource_ids,
            export_concepts_as=export_concepts_as,
            filename=filename,
        )

        load_event = models.LoadEvent.objects.get(loadid=load_id)
        status = _("Completed") if load_event.status == "indexed" else _("Failed")
    except Exception as e:
        logger.error(e)
        load_event = models.LoadEvent.objects.get(loadid=load_id)
        load_event.status = "failed"
        load_event.save()
    finally:
        msg = _("Excel Export: {}").format(status)
        user = User.objects.get(id=user_id)
        notify_completion(msg, user)


@shared_task
def export_branch_excel(
    userid, load_id, graph_id, graph_name, resource_ids, filename=None
):
    from arches.app.etl_modules import branch_excel_exporter

    BranchExcelExporter = branch_excel_exporter.BranchExcelExporter(
        request=None, loadid=load_id
    )
    export_excel_data(
        BranchExcelExporter,
        userid,
        load_id,
        graph_id,
        graph_name,
        resource_ids,
        filename,
    )


@shared_task
def export_tile_excel(
    userid,
    load_id,
    graph_id,
    graph_name,
    resource_ids,
    export_concepts_as,
    filename=None,
):
    from arches.app.etl_modules import tile_excel_exporter

    TileExcelExporter = tile_excel_exporter.TileExcelExporter(
        request=None, loadid=load_id
    )
    export_excel_data(
        TileExcelExporter,
        userid,
        load_id,
        graph_id,
        graph_name,
        resource_ids,
        export_concepts_as,
        filename,
    )


@shared_task
def load_single_csv(
    userid,
    loadid,
    graphid,
    has_headers,
    fieldnames,
    csv_mapping,
    csv_file_name,
    id_label,
):
    from arches.app.etl_modules import import_single_csv

    logger = logging.getLogger(__name__)

    try:
        ImportSingleCsv = import_single_csv.ImportSingleCsv(loadid=loadid)
        ImportSingleCsv.run_load_task(
            userid,
            loadid,
            graphid,
            has_headers,
            fieldnames,
            csv_mapping,
            csv_file_name,
            id_label,
        )

        load_event = models.LoadEvent.objects.get(loadid=loadid)
        status = _("Completed") if load_event.status == "indexed" else _("Failed")
    except Exception as e:
        logger.error(e)
        load_event = models.LoadEvent.objects.get(loadid=loadid)
        load_event.status = "failed"
        load_event.save()
        status = _("Failed")
    finally:
        msg = _("Single CSV Import: {} [{}]").format(csv_file_name, status)
        user = User.objects.get(id=userid)
        notify_completion(msg, user)


@shared_task
def load_json_ld(userid, files, summary, result, temp_dir, loadid, moduleid):
    from arches.app.etl_modules import jsonld_importer

    logger = logging.getLogger(__name__)

    try:
        importer = jsonld_importer.JSONLDImporter(
            loadid=loadid,
            userid=userid,
            moduleid=moduleid,
        )
        importer.temp_dir = temp_dir
        importer.run_load_task(userid, files, summary, result, temp_dir, loadid)

        load_event = models.LoadEvent.objects.get(loadid=loadid)
        status = _("Completed") if load_event.status == "indexed" else _("Failed")
    except Exception as e:
        logger.error(e)
        load_event = models.LoadEvent.objects.filter(loadid=loadid).update(
            status="failed"
        )
        status = _("Failed")
    finally:
        msg = _("JSON-LD Import: {} [{}]").format(summary["name"], status)
        user = User.objects.get(id=userid)
        notify_completion(msg, user)


@shared_task
def edit_bulk_string_data(
    userid,
    load_id,
    module_id,
    graph_id,
    node_id,
    operation,
    language_code,
    old_text,
    new_text,
    resourceids,
):
    from arches.app.etl_modules import base_data_editor

    logger = logging.getLogger(__name__)

    try:
        BulkStringEditor = base_data_editor.BulkStringEditor(loadid=load_id)
        BulkStringEditor.run_load_task(
            userid,
            load_id,
            module_id,
            graph_id,
            node_id,
            operation,
            language_code,
            old_text,
            new_text,
            resourceids,
        )

        load_event = models.LoadEvent.objects.get(loadid=load_id)
        status = _("Completed") if load_event.status == "indexed" else _("Failed")
    except Exception as e:
        logger.error(e)
        load_event = models.LoadEvent.objects.get(loadid=load_id)
        load_event.status = "failed"
        load_event.save()
        status = _("Failed")
    finally:
        msg = _("Bulk Data Edit: {} [{}]").format(operation, status)
        user = User.objects.get(id=userid)
        notify_completion(msg, user)


@shared_task
def edit_bulk_concept_data(
    userid,
    load_id,
    module_id,
    graph_id,
    node_id,
    resource_ids,
    unselected_tiles,
    oldid,
    newid,
):
    from arches.app.etl_modules import bulk_edit_concept

    logger = logging.getLogger(__name__)
    try:
        BulkConceptEditor = bulk_edit_concept.BulkConceptEditor(loadid=load_id)
        BulkConceptEditor.run_load_task(
            userid,
            load_id,
            module_id,
            graph_id,
            node_id,
            resource_ids,
            unselected_tiles,
            oldid,
            newid,
        )
        load_event = models.LoadEvent.objects.get(loadid=load_id)
        status = _("Completed") if load_event.status == "indexed" else _("Failed")
    except Exception as e:
        logger.error(e)
        load_event = models.LoadEvent.objects.get(loadid=load_id)
        load_event.status = "failed"
        load_event.save()
        status = _("Failed")
    finally:
        msg = _("Bulk Concept Editor: [{}]").format(status)
        user = User.objects.get(id=userid)
        notify_completion(msg, user)


@shared_task
def bulk_data_deletion(userid, load_id, graph_id, nodegroup_id, resourceids):
    from arches.app.etl_modules import bulk_data_deletion

    logger = logging.getLogger(__name__)

    try:
        BulkDataDeletion = bulk_data_deletion.BulkDataDeletion(loadid=load_id)
        BulkDataDeletion.run_bulk_task(
            userid, load_id, graph_id, nodegroup_id, resourceids
        )

        load_event = models.LoadEvent.objects.get(loadid=load_id)
        status = _("Completed") if load_event.status == "indexed" else _("Failed")
    except Exception as e:
        logger.error(e)
        load_event = models.LoadEvent.objects.get(loadid=load_id)
        load_event.status = "failed"
        load_event.save()
        status = _("Failed")
    finally:
        msg = _("Bulk Data Deletion: [{}]").format(status)
        user = User.objects.get(id=userid)
        notify_completion(msg, user)


@shared_task
def run_task(module_name=None, class_name=None, method_to_run=None, **kwargs):
    """
    this allows the user to run any method as a celery task
    module_name, class_name, and method_to_run are required
    pass any additional arguments to the method via the kwargs parameter
    """

    theClass = getattr(importlib.import_module(module_name), class_name)
    theMethod = getattr(theClass(), method_to_run)
    theMethod(**kwargs)


@shared_task
def run_etl_task(**kwargs):
    """
    this allows the user to run the custom etl module
    import_module, import_class, loadid, userid are the required string parameter
    importer_name can be added (not required) for messaging purpose
    """

    logger = logging.getLogger(__name__)

    import_module = kwargs.pop("import_module")
    import_class = kwargs.pop("import_class")
    importer_name = kwargs.pop("importer_name", import_class)
    loadid = kwargs.get("loadid")
    userid = kwargs.get("userid")

    try:
        run_task(
            module_name=import_module,
            class_name=import_class,
            method_to_run="run_load_task",
            **kwargs,
        )

        load_event = models.LoadEvent.objects.get(loadid=loadid)
        status = _("Completed") if load_event.status == "indexed" else _("Failed")
    except Exception as e:
        logger.error(e)
        load_event = models.LoadEvent.objects.get(loadid=loadid)
        load_event.status = "failed"
        load_event.save()
        status = _("Failed")
    finally:
        msg = _("{}: {}").format(importer_name, status)
        user = User.objects.get(id=userid)
        notify_completion(msg, user)


@shared_task
def reverse_etl_load(loadid):
    from arches.app.etl_modules import base_import_module

    module = base_import_module.BaseImportModule()
    module.reverse_load(loadid)


def create_user_task_record(taskid, taskname, userid):
    try:
        user = User.objects.get(id=userid)
        new_task_record = models.UserXTask.objects.create(
            user=user, taskid=taskid, datestart=datetime.now(), name=taskname
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(e)


def notify_completion(msg, user, notiftype_name=None, context=None):
    if notiftype_name is not None:
        notif_type = models.NotificationType.objects.get(name=notiftype_name)
    else:
        notif_type = None
    notif = models.Notification.objects.create(
        notiftype=notif_type, message=msg, context=context
    )
    models.UserXNotification.objects.create(notif=notif, recipient=user)
