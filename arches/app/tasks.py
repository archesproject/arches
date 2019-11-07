# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core import management

@shared_task
def sync(surveyid, userid):
    management.call_command('mobile', operation='sync_survey', id=surveyid, user=userid)
    return 'sync complete'
