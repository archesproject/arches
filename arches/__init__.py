from __future__ import absolute_import
from arches.version import get_version

try:
    # This will make sure the app is always imported when
    # Django starts so that shared_task will use this app.
    from .celery import app as celery_app

    __all__ = ("celery_app",)
except Exception as e:
    pass

# VERSION[3] options = "alpha", "beta", "rc", or "final"
VERSION = (7, 6, 0, "beta", 0)

__version__ = get_version(VERSION)
