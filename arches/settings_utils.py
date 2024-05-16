import importlib
import json
import os
import site
import sys

from pathlib import Path


def build_staticfiles_dirs(root_dir, app_root=None, arches_applications=None, additional_directories=None):
    """
    Builds the STATICFILES_DIRS tuple with respect to ordering projects,
    packages, additional directories.

    Arguements

    root_dir -- string, os-safe absolute path to arches-core root directory
    app_root -- string, os-safe absolute path to application directory
    arches_applications -- tuple of installed arches_app names
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
            ('node_modules', os.path.join(app_root, "..", "node_modules"))
        )

    if arches_applications:
        for arches_application in arches_applications:
            importlib.import_module(arches_application)  # need to import module to find path
            application_origin = os.path.split(sys.modules[arches_application].__spec__.origin)[0]
            directories.append(os.path.join(application_origin, 'media'))

    directories.append(os.path.join(root_dir, "app", "media", "build"))
    directories.append(os.path.join(root_dir, "app", "media"))
    directories.append(
        ('node_modules', os.path.join(root_dir, "..", "node_modules"))
    )

    return tuple(directories)


def build_templates_config(root_dir, debug, app_root=None, arches_applications=None, additional_directories=None, context_processors=None):
    """
    Builds a template config dictionary

    Arguements

    root_dir -- string, os-safe absolute path to arches-core root directory
    debug -- boolean representing the DEBUG value derived from settings
    app_root -- string, os-safe absolute path to application directory
    arches_applications -- tuple of installed arches_app names
    additional_directories -- list of os-safe absolute paths
    context_processors -- list of strings representing desired context processors
    """
    directories = []

    if additional_directories:
        for additional_directory in additional_directories:
            directories.append(additional_directory)

    if app_root:
        directories.append(os.path.join(app_root, "templates"))

    if arches_applications:
        for arches_application in arches_applications:
            importlib.import_module(arches_application)  # need to import module to find path
            application_origin = os.path.split(sys.modules[arches_application].__spec__.origin)[0]
            directories.append(os.path.join(application_origin, 'templates'))

    directories.append(os.path.join(root_dir, "app", "templates"))

    return [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": directories,
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": context_processors
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
                ],
                "debug": debug,
            },
        },
    ]


def transmit_webpack_django_config(
    root_dir, app_root, static_url, public_server_address, webpack_development_server_port, arches_applications=None
):
    arches_applications_paths = {}

    if arches_applications:
        for arches_application in arches_applications:
            importlib.import_module(arches_application)  # need to import module to find path
            arches_applications_paths[arches_application] = os.path.split(sys.modules[arches_application].__spec__.origin)[0]

    sys.stdout.write(
        json.dumps(
            {
                "APP_ROOT": os.path.realpath(app_root),
                "ARCHES_APPLICATIONS": list(arches_applications) if arches_applications else [],
                "ARCHES_APPLICATIONS_PATHS": arches_applications_paths,
                "SITE_PACKAGES_DIRECTORY": site.getsitepackages()[0],
                "PUBLIC_SERVER_ADDRESS": public_server_address,
                "ROOT_DIR": os.path.realpath(root_dir),
                "STATIC_URL": static_url,
                "WEBPACK_DEVELOPMENT_SERVER_PORT": webpack_development_server_port,
            }
        )
    )
    sys.stdout.flush()
