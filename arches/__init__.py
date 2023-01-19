from __future__ import absolute_import
from arches.setup import get_version

try:
    # This will make sure the app is always imported when
    # Django starts so that shared_task will use this app.
    from .celery import app as celery_app

    __all__ = ("celery_app",)
except Exception as e:
    pass

VERSION = (7, 3, 0, "final", 0)  # VERSION[3] options = "alpha", "beta", "rc", or "final"

__version__ = get_version(VERSION)

