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
def update_user_task_record(taskid):
    task_obj = models.UserXTask.objects.get(taskid=taskid)
    task_obj.status = "SUCCESS"
    task_obj.date_done = datetime.datetime.now()
    task_obj.save()


@shared_task
def log_error(request, exc, traceback):
    logger = logging.getLogger(__name__)
    logger.warn(exc)
    task_obj = models.UserXTask.objects.get(taskid=request.id)
    task_obj.status = "FAILED"
    task_obj.date_done = datetime.datetime.now()
    task_obj.save()


def create_user_task_record(taskid, taskname, userid):
    try:
        new_task_record = models.UserXTask.objects.create(user_id=userid, taskid=taskid, date_start=datetime.datetime.now(), name=taskname)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warn(e)
