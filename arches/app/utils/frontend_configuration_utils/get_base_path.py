import os

from django.conf import settings
from pathlib import Path


def get_base_path():
    if Path(settings.APP_ROOT).parent == Path(settings.ROOT_DIR):
        return os.path.realpath(settings.ROOT_DIR)
    else:
        return os.path.realpath(settings.APP_ROOT)
