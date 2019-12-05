from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core import management
from django.contrib.auth.models import User
import datetime
import logging
from arches.app.models import models
from arches.app.search.search_export import SearchResultsExporter
import arches.app.utils.data_management.zip as zip_utils
from django.http import HttpRequest


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
    new_req = HttpRequest()
    new_req.method = "GET"
    new_req.user = _user
    for k, v in request_dict.items():
        new_req.GET.__setitem__(k, v[0])

    exporter = SearchResultsExporter(search_request=new_req)
    url = zip_utils.write_zip_file(exporter.export(format), return_relative_url=True)
    msg = f"<a download href='{url}'><button class='btn btn-notifs-download btn-labeled btn-sm fa fa-download'>Download File</button></a>"
    response = {"taskid": self.request.id, "msg": msg}

    return response


@shared_task
def update_user_task_record(arg_dict={}):
    taskid = arg_dict["taskid"]
    msg = arg_dict["msg"]
    task_obj = models.UserXTask.objects.get(taskid=taskid)
    task_obj.status = "SUCCESS"
    task_obj.datedone = datetime.datetime.now()
    task_obj.save()
    if msg is None:
        msg = task_obj.status + ": " + task_obj.name
    notify_completion(msg, task_obj.user)


@shared_task
def log_error(request, exc, traceback, msg=None):
    logger = logging.getLogger(__name__)
    logger.warn(exc)
    print("in log_error task")
    print(exc)
    task_obj = models.UserXTask.objects.get(taskid=request.id)
    task_obj.status = "FAILED"
    task_obj.date_done = datetime.datetime.now()
    task_obj.save()
    if msg is None:
        msg = task_obj.status + ": " + task_obj.name
    notify_completion(msg, task_obj.user)


def create_user_task_record(taskid, taskname, userid):
    try:
        user = User.objects.get(id=userid)
        new_task_record = models.UserXTask.objects.create(user=user, taskid=taskid, datestart=datetime.datetime.now(), name=taskname)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warn(e)


def notify_completion(msg, user):
    notif_type = models.NotificationType.objects.get(name="test_email_notification")
    notif = models.Notification.objects.create(notiftype=notif_type, message=msg)
    models.UserXNotification.objects.create(notif=notif, recipient=user)
