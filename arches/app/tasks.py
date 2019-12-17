from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime
import logging
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.core import management
from django.db import connection
from django.http import HttpRequest
from arches.app.models import models
from arches.app.search.search_export import SearchResultsExporter
import arches.app.utils.data_management.zip as zip_utils


@shared_task
def delete_file():
    now = datetime.timestamp(datetime.now())
    file_list = []
    counter = 0
    with os.scandir(settings.CELERY_SEARCH_EXPORT_DIR) as current_files:
        for file in current_files:
            file_stat = os.stat(os.path.join(settings.CELERY_SEARCH_EXPORT_DIR, file))
            if file_stat.st_ctime > settings.CELERY_SEARCH_EXPORT_EXPIRES:
                file_list.append(file.name)
    for file in file_list:
        os.remove(os.path.join(settings.CELERY_SEARCH_EXPORT_DIR, file))
        counter += 1
    return f"{counter} files deleted"


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
def export_search_results(self, userid, request_dict, format):
    create_user_task_record(self.request.id, self.name, userid)
    _user = User.objects.get(id=userid)
    email = request_dict["email"]
    new_req = HttpRequest()
    new_req.method = "GET"
    new_req.user = _user
    for k, v in request_dict.items():
        new_req.GET.__setitem__(k, v[0])  # copies k,v pairs from old req to new_req

    exporter = SearchResultsExporter(search_request=new_req)
    # prod instances of arches should exclude the return_relative_url kwarg (default=False)
    msg = zip_utils.write_zip_file(exporter.export(format), return_relative_url=True)
    context = dict(
        greeting="Hello,\nYour request to download a set of search results is now ready.",
        link=msg,
        button_text="Download Now",
        closing="Thank you",
        email=email
    )
    response = {"taskid": self.request.id, "msg": msg, "notiftype_name": "Search Export Download Ready", "context": context}

    return response


@shared_task(bind=True)
def refresh_materialized_view(self):
    # create_user_task_record(self.request.id, self.name, userid) # get user from session?
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
    task_obj = models.UserXTask.objects.get(taskid=request.id)
    task_obj.status = "FAILED"
    task_obj.date_done = datetime.now()
    task_obj.save()
    if msg is None:
        msg = task_obj.status + ": " + task_obj.name
    notify_completion(msg, task_obj.user)


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
