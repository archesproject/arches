from __future__ import absolute_import, unicode_literals
import os
import celery
from celery import Celery

import platform

if platform.system().lower() == "windows":
    os.environ.setdefault("FORKED_BY_MULTIPROCESSING", "1")

# Only takes effect if nothing has set DJANGO_SETTINGS_MODULE yet, which is the
# case when this module is celery's own -A app (running arches core standalone).
# In a downstream project, the project's own celery.py / manage.py sets this
# first, so this is a no-op there and their settings module is left alone.
# ARCHES_PROJECT_PACKAGE (falling back to ARCHES_PROJECT, as in
# .runtime/test_settings.py) names that project's package when running as one;
# unset in a bare core checkout, so it defaults to "arches".
_project_package = (
    os.environ.get("ARCHES_PROJECT_PACKAGE")
    or os.environ.get("ARCHES_PROJECT", "").replace("-", "_")
    or "arches"
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{_project_package}.settings")
app = Celery("arches")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
