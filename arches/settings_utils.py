import json
import os
import site
import sys
from contextlib import contextmanager

import django
from django.apps import apps
from django.conf import global_settings, settings


@contextmanager
def _move_to_end_of_sys_path(*paths, add_cwd=False):
    _orig_sys_path = sys.path[:]
    for path in paths:
        if path in sys.path:
            sys.path.remove(path)
            sys.path.append(path)
    if add_cwd:
        sys.path.append(os.getcwd())
    try:
        yield
    finally:
        sys.path = _orig_sys_path


def list_arches_app_names():
    return [
        config.name
        for config in apps.get_app_configs()
        if getattr(config, "is_arches_application", False)
    ]


def list_arches_app_paths():
    return [
        config.module.__path__[0]
        for config in apps.get_app_configs()
        if getattr(config, "is_arches_application", False)
    ]


def build_staticfiles_dirs(root_dir, app_root=None, additional_directories=None):
    """
    Builds the STATICFILES_DIRS tuple with respect to ordering projects,
    packages, additional directories, before considering Arches
    applications. (Those are handled by inject_arches_applications_directories(),
    called by an arches application's ready() method.)

    Arguments

    root_dir -- string, os-safe absolute path to arches-core root directory
    app_root -- string, os-safe absolute path to application directory
    additional_directories -- list of os-safe absolute paths
    """
    directories = []

    if additional_directories:
        for additional_directory in additional_directories:
            directories.append(additional_directory)

    if app_root:
        directories.append(os.path.join(app_root, "media", "build"))
        directories.append(os.path.join(app_root, "media"))
        directories.append(
            ("node_modules", os.path.join(app_root, "..", "node_modules"))
        )

    directories.append(os.path.join(root_dir, "app", "media", "build"))
    directories.append(os.path.join(root_dir, "app", "media"))
    directories.append(("node_modules", os.path.join(root_dir, "..", "node_modules")))

    return tuple(directories)


def build_templates_config(
    root_dir,
    debug,
    app_root=None,
    additional_directories=None,
    context_processors=None,
):
    """
    Builds a preliminary template config dictionary, before considering Arches
    applications. (Those are handled by inject_arches_applications_directories(),
    called by an arches application's ready() method.)

    Arguments

    root_dir -- string, os-safe absolute path to arches-core root directory
    debug -- boolean representing the DEBUG value derived from settings
    app_root -- string, os-safe absolute path to application directory
    additional_directories -- list of os-safe absolute paths
    context_processors -- list of strings representing desired context processors
    """
    directories = []

    if additional_directories:
        for additional_directory in additional_directories:
            directories.append(additional_directory)

    if app_root:
        directories.append(os.path.join(app_root, "templates"))

    directories.append(os.path.join(root_dir, "app", "templates"))

    return [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": directories,
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": (
                    context_processors
                    if context_processors
                    else [
                        "django.contrib.auth.context_processors.auth",
                        "django.template.context_processors.debug",
                        "django.template.context_processors.i18n",
                        "django.template.context_processors.media",
                        "django.template.context_processors.static",
                        "django.template.context_processors.tz",
                        "django.template.context_processors.request",
                        "django.contrib.messages.context_processors.messages",
                        "arches.app.utils.context_processors.livereload",
                        "arches.app.utils.context_processors.map_info",
                        "arches.app.utils.context_processors.app_settings",
                    ]
                ),
                "debug": debug,
            },
        },
    ]


def inject_arches_applications_directories():
    from django.conf import settings

    arches_app_paths = list_arches_app_paths()

    arches_app_template_dirs = []
    for arches_app_path in arches_app_paths:
        template_path = os.path.join(arches_app_path, "templates")
        if template_path not in settings.TEMPLATES[0]["DIRS"]:
            arches_app_template_dirs.append(template_path)

    settings.TEMPLATES[0]["DIRS"] = (
        *settings.TEMPLATES[0]["DIRS"][:-1],
        *arches_app_template_dirs,
        settings.TEMPLATES[0]["DIRS"][-1],
    )

    arches_app_media_dirs = []
    for arches_app_path in arches_app_paths:
        media_dir = os.path.join(arches_app_path, "media")
        if media_dir not in settings.STATICFILES_DIRS:
            arches_app_media_dirs.append(media_dir)

    settings.STATICFILES_DIRS = (
        *settings.STATICFILES_DIRS[:-3],
        *arches_app_media_dirs,
        *settings.STATICFILES_DIRS[-3:],
    )


def transmit_webpack_django_config(**kwargs):
    is_arches_core = kwargs["APP_NAME"] == "Arches"
    transmitted_project_settings = {k: v for k, v in kwargs.items() if k.isupper()}
    settings.configure(default_settings=global_settings, **transmitted_project_settings)

    # Without this `import celery` might resolve to arches.celery or project.celery
    if is_arches_core:
        with _move_to_end_of_sys_path(os.path.realpath(kwargs["ROOT_DIR"])):
            django.setup()
    else:
        with _move_to_end_of_sys_path(
            os.path.realpath(kwargs["APP_ROOT"]), add_cwd=True
        ):
            django.setup()

    arches_app_names = list_arches_app_names()
    arches_app_paths = list_arches_app_paths()
    path_lookup = dict(zip(arches_app_names, arches_app_paths, strict=True))

    sys.stdout.write(
        json.dumps(
            {
                "APP_ROOT": os.path.realpath(kwargs["APP_ROOT"]),
                "ARCHES_APPLICATIONS": arches_app_names,
                "ARCHES_APPLICATIONS_PATHS": path_lookup,
                "SITE_PACKAGES_DIRECTORY": site.getsitepackages()[0],
                "PUBLIC_SERVER_ADDRESS": kwargs["PUBLIC_SERVER_ADDRESS"],
                "ROOT_DIR": os.path.realpath(kwargs["ROOT_DIR"]),
                "STATIC_URL": kwargs["STATIC_URL"],
                "WEBPACK_DEVELOPMENT_SERVER_PORT": kwargs[
                    "WEBPACK_DEVELOPMENT_SERVER_PORT"
                ],
            }
        )
    )
    sys.stdout.flush()
