from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime
from datetime import timedelta
import logging
import os
from django.contrib.auth.models import User
from django.core import management
from django.db import connection
from django.http import HttpRequest
from arches.app.models import models
from arches.app.search.search_export import SearchResultsExporter
import arches.app.utils.zip as zip_utils
from django.utils.translation import ugettext as _


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
def sync(self, surveyid=None, userid=None):
    create_user_task_record(self.request.id, self.name, userid)
    management.call_command("mobile", operation="sync_survey", id=surveyid, user=userid)
    response = {"taskid": self.request.id}
    return response


@shared_task(bind=True)
def export_search_results(self, userid, request_values, format):

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

    context = dict(
        greeting="Hello,\nYour request to download a set of search results is now ready.",
        link=exportid,
        button_text="Download Now",
        closing="Thank you",
        email=email,
        name=export_name,
    )
    response = {"taskid": self.request.id, "msg": export_name, "notiftype_name": "Search Export Download Ready", "context": context}

    return response


@shared_task(bind=True)
def refresh_materialized_view(self):
    cursor = connection.cursor()
    sql = """
        REFRESH MATERIALIZED VIEW mv_geojson_geoms;
    """
    cursor.execute(sql)
    response = {"taskid": self.request.id}


@shared_task
def update_user_task_record(arg_dict={}):
    taskid = arg_dict["taskid"]
    msg = arg_dict["msg"]
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
    if msg is None:
        msg = task_obj.status + ": " + task_obj.name
    notify_completion(msg, task_obj.user, notiftype_name, context)


@shared_task
def log_error(request, exc, traceback, msg=None):
    logger = logging.getLogger(__name__)
    logger.warn(exc)
    try:
        task_obj = models.UserXTask.objects.get(taskid=request.id)
        task_obj.status = "FAILED"
        task_obj.date_done = datetime.now()
        task_obj.save()
        if msg is None:
            msg = task_obj.status + ": " + task_obj.name
        notify_completion(msg, task_obj.user)
    except Exception as e:
        print("No such UserXTask record exists. Notification aborted.")


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
