from __future__ import absolute_import, unicode_literals
import os
import celery
from celery import Celery

import platform

if platform.system().lower() == "windows":
    os.environ.setdefault("FORKED_BY_MULTIPROCESSING", "1")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
app = Celery("arches")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
