from __future__ import absolute_import
import importlib.metadata
from packaging.version import Version

try:
    # This will make sure the app is always imported when
    # Django starts so that shared_task will use this app.
    from .celery import app as celery_app

    __all__ = ("celery_app",)
except Exception as e:
    pass

__version__ = importlib.metadata.version(__package__)

version = Version(__version__)
major, minor, micro = version.major, version.minor, version.micro

if version.pre:
    pre_type_mapping = {"a": "alpha", "b": "beta", "rc": "rc"}
    pre_type = pre_type_mapping.get(version.pre[0], version.pre[0])
    pre_num = version.pre[1]
else:
    pre_type = "final"
    pre_num = 0

VERSION = (major, minor, micro, pre_type, pre_num)
