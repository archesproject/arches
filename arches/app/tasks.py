from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core import management
import datetime
import logging
from arches.app.models import models


@shared_task(bind=True)
def sync(self, surveyid=None, userid=None):
    create_user_task_record(self.request.id, self.name, userid)
    management.call_command("mobile", operation="sync_survey", id=surveyid, user=userid)
    return self.request.id


@shared_task
def update_user_task_record(taskid, **kwargs):
    task_obj = models.UserXTask.objects.get(taskid=taskid)
    task_obj.status = "SUCCESS"
    task_obj.date_done = datetime.datetime.now()
    task_obj.save()
    if "notif" in kwargs.keys():
        notif = kwargs["notif"]
    else:
        notif = task_obj.status + ": " + task_obj.name
    notify_completion(notif, task_obj.user)


@shared_task
def log_error(request, exc, traceback, **kwargs):
    logger = logging.getLogger(__name__)
    logger.warn(exc)
    task_obj = models.UserXTask.objects.get(taskid=request.id)
    task_obj.status = "FAILED"
    task_obj.date_done = datetime.datetime.now()
    task_obj.save()
    if "notif" in kwargs.keys():
        notif = kwargs["notif"]
    else:
        notif = task_obj.status + ": " + task_obj.name
    notify_completion(notif, task_obj.user)


def create_user_task_record(taskid, taskname, userid):
    try:
        new_task_record = models.UserXTask.objects.create(user_id=userid, taskid=taskid, date_start=datetime.datetime.now(), name=taskname)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warn(e)

def notify_completion(notif, user):
    models.Notification.objects.create(message=notif, recipient_id=user)
