from __future__ import absolute_import
import importlib.metadata

try:
    # This will make sure the app is always imported when
    # Django starts so that shared_task will use this app.
    from .celery import app as celery_app

    __all__ = ("celery_app",)
except Exception as e:
    pass

__version__ = importlib.metadata.version(__package__)

# Keep pre-8.2 module paths for the applications now under arches.extensions
# resolvable. Installed here rather than in AppConfig.ready() because project
# settings reference those paths before the app registry is populated.
from arches.extensions import compat as _extensions_compat

_extensions_compat.install()
