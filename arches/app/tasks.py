from __future__ import absolute_import, unicode_literals
import os
import logging
from celery import shared_task
from datetime import datetime
from datetime import timedelta
from django.contrib.auth.models import User
from django.core import management
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.http import HttpRequest
from django.utils.translation import ugettext as _
from arches.app.models import models


@shared_task
def delete_file():
    from arches.app.models.system_settings import settings

    settings.update_from_db()

    logger = logging.getLogger(__name__)
    now = datetime.timestamp(datetime.now())
    file_list = []
    range = datetime.now() - timedelta(seconds=settings.CELERY_SEARCH_EXPORT_EXPIRES)
    exports = models.SearchExportHistory.objects.filter(exporttime__lt=range).exclude(downloadfile="")
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
def sync(self, surveyid=None, userid=None, synclogid=None):
    from arches.app.models.mobile_survey import MobileSurvey

    create_user_task_record(self.request.id, self.name, userid)
    survey = MobileSurvey.objects.get(id=surveyid)
    survey._sync(synclogid, userid)
    response = {"taskid": self.request.id}
    return response


@shared_task(bind=True)
def export_search_results(self, userid, request_values, format):
    from arches.app.search.search_export import SearchResultsExporter
    from arches.app.models.system_settings import settings

    settings.update_from_db()

    create_user_task_record(self.request.id, self.name, userid)
    _user = User.objects.get(id=userid)
    email = request_values["email"]
    export_name = request_values["exportName"][0]
    new_request = HttpRequest()
    new_request.method = "GET"
    new_request.user = _user
    for k, v in request_values.items():
        new_request.GET.__setitem__(k, v[0])
    new_request.path = request_values["path"]
    exporter = SearchResultsExporter(search_request=new_request)
    files, export_info = exporter.export(format)
    exportid = exporter.write_export_zipfile(files, export_info)
    search_history_obj = models.SearchExportHistory.objects.get(pk=exportid)

    return {
        "taskid": self.request.id,
        "msg": _(
            "Your search {} is ready for download. You have 24 hours to access this file, after which we'll automatically remove it."
        ).format(export_name),
        "notiftype_name": "Search Export Download Ready",
        "context": dict(
            greeting=_("Hello,\nYour request to download a set of search results is now ready."),
            link=exportid,
            button_text=_("Download Now"),
            closing=_("Thank you"),
            email=email,
            name=export_name,
            email_link=str(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT).rstrip("/") + "/files/" + str(search_history_obj.downloadfile),
        ),
    }


@shared_task(bind=True)
def refresh_materialized_view(self):
    with connection.cursor() as cursor:
        sql = """
            REFRESH MATERIALIZED VIEW mv_geojson_geoms;
        """
        cursor.execute(sql)
    response = {"taskid": self.request.id}


@shared_task(bind=True)
def import_business_data(
    self, data_source="", overwrite="", bulk_load=False, create_concepts=False, create_collections=False, prevent_indexing=False
):
    management.call_command(
        "packages", operation="import_business_data", source=data_source, overwrite=True, prevent_indexing=prevent_indexing
    )


@shared_task
def package_load_complete(*args, **kwargs):
    valid_resource_paths = kwargs.get("valid_resource_paths")

    msg = _("Resources have completed loading.")
    notifytype_name = "Package Load Complete"
    user = User.objects.get(id=1)
    context = dict(
        greeting=_("Hello,\nYour package has successfully loaded into your Arches project."),
        loaded_resources=[os.path.basename(os.path.normpath(resource_path)) for resource_path in valid_resource_paths],
        link="",
        link_text=_("Log me in"),
        closing=_("Thank you"),
        email="",
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
    logger.warn(exc)
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
    logger.warn(exc)
    logger.warn(traceback)
    msg = f"Package Load erred on import_business_data. Exception: {exc}. See logs for details."
    user = User.objects.get(id=1)
    notify_completion(msg, user)


def create_user_task_record(taskid, taskname, userid):
    try:
        user = User.objects.get(id=userid)
        new_task_record = models.UserXTask.objects.create(user=user, taskid=taskid, datestart=datetime.now(), name=taskname)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warn(e)


def notify_completion(msg, user, notiftype_name=None, context=None):
    if notiftype_name is not None:
        notif_type = models.NotificationType.objects.get(name=notiftype_name)
    else:
        notif_type = None
    notif = models.Notification.objects.create(notiftype=notif_type, message=msg, context=context)
    models.UserXNotification.objects.create(notif=notif, recipient=user)
