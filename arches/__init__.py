from __future__ import absolute_import
from arches.setup import get_version

try:
    # This will make sure the app is always imported when
    # Django starts so that shared_task will use this app.
    from .celery import app as celery_app

    __all__ = ("celery_app",)
except Exception as e:
    pass

<<<<<<< HEAD
VERSION = (7, 5, 0, "alpha", 0)  # VERSION[3] options = "alpha", "beta", "rc", or "final"
=======
VERSION = (7, 4, 2, "beta", 0)  # VERSION[3] options = "alpha", "beta", "rc", or "final"
>>>>>>> b040c63d5f4b8d0d979190f722135b8d7c90b2e0

__version__ = get_version(VERSION)

