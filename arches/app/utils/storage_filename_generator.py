import os
from arches.app.models.system_settings import settings


def generate_filename(instance, filename):
    return os.path.join(settings.UPLOADED_FILES_DIR, filename)
