import os
import sysconfig

from django.conf import settings

from arches.settings_utils import (
    list_arches_app_labels,
    list_arches_app_labels_and_paths,
    list_arches_app_paths,
)


def generate_webpack_configuration():
    app_root_path = os.path.realpath(settings.APP_ROOT)
    root_dir_path = os.path.realpath(settings.ROOT_DIR)

    arches_app_names = list_arches_app_labels()
    arches_app_paths = list_arches_app_paths()

    return {
        "_comment": "This is a generated file. Do not edit directly.",
        "APP_RELATIVE_PATH": os.path.relpath(app_root_path),
        "APP_ROOT": app_root_path,
        "ARCHES_APPLICATIONS": arches_app_names,
        "ARCHES_APPLICATIONS_PATHS": dict(
            zip(arches_app_names, arches_app_paths, strict=True)
        ),
        # Every Arches application whose source is resolvable, including bundled
        # ones a project has not enabled. Used for module aliasing -- tsconfig
        # paths and vitest -- not for entry points, templates or static files,
        # which must come from installed applications alone.
        "RESOLVABLE_APPLICATION_PATHS": list_arches_app_labels_and_paths(),
        "SITE_PACKAGES_DIRECTORY": sysconfig.get_path("purelib"),
        "ROOT_DIR": root_dir_path,
        "STATIC_URL": settings.STATIC_URL,
        "WEBPACK_DEVELOPMENT_SERVER_PORT": settings.WEBPACK_DEVELOPMENT_SERVER_PORT,
    }
