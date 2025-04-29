import os

from arches.app.models.system_settings import settings
from arches.app.utils import import_class_from_string


def get_filename(instance, filename):
    return import_class_from_string(settings.FILENAME_GENERATOR)(instance, filename)


def generate_filename(instance, filename):
    return os.path.join(settings.UPLOADED_FILES_DIR, filename)
