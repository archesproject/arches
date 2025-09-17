import os
import sysconfig

from django.conf import settings

from arches.settings_utils import list_arches_app_names, list_arches_app_paths


def generate_webpack_configuration():
    app_root_path = os.path.realpath(settings.APP_ROOT)
    root_dir_path = os.path.realpath(settings.ROOT_DIR)

    arches_app_names = list_arches_app_names()
    arches_app_paths = list_arches_app_paths()

    return {
        "_comment": "This is a generated file. Do not edit directly.",
        "APP_RELATIVE_PATH": os.path.relpath(app_root_path),
        "APP_ROOT": app_root_path,
        "ARCHES_APPLICATIONS": arches_app_names,
        "ARCHES_APPLICATIONS_PATHS": dict(
            zip(arches_app_names, arches_app_paths, strict=True)
        ),
        "SITE_PACKAGES_DIRECTORY": sysconfig.get_path("purelib"),
        "ROOT_DIR": root_dir_path,
        "STATIC_URL": settings.STATIC_URL,
        "WEBPACK_DEVELOPMENT_SERVER_PORT": settings.WEBPACK_DEVELOPMENT_SERVER_PORT,
    }
