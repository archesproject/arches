import json
import os
import site
import sys
from contextlib import contextmanager

import django
from django.apps import apps
from django.conf import global_settings, settings
from django.contrib.staticfiles.finders import AppDirectoriesFinder


class ArchesApplicationsStaticFilesFinder(AppDirectoriesFinder):
    source_dir = "media"


class CoreArchesStaticFilesFinderBuildDirectory(AppDirectoriesFinder):
    source_dir = os.path.join("app", "media", "build")


class CoreArchesStaticFilesFinderMediaRoot(AppDirectoriesFinder):
    source_dir = os.path.join("app", "media")


class CoreArchesStaticFilesFinderNodeModules(AppDirectoriesFinder):
    source_dir = os.path.normpath(os.path.join("..", "node_modules"))


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


def build_staticfiles_dirs(*, app_root=None, additional_directories=None):
    """
    Builds a STATICFILES_DIRS tuple for this project (additional_directories,
    then app_root) that Django will proritize before falling back to
    INSTALLED_APPS (Arches applications and Arches core).

    Arguments

    app_root -- string, os-safe absolute path to application directory
    additional_directories -- list of os-safe absolute paths
    """
    directories = []
    try:
        if additional_directories:
            for additional_directory in additional_directories:
                directories.append(additional_directory)

        if app_root:
            directories.append(os.path.join(app_root, "media", "build"))
            directories.append(os.path.join(app_root, "media"))
            directories.append(
                (
                    "node_modules",
                    os.path.normpath(os.path.join(app_root, "..", "node_modules")),
                )
            )

        return tuple(directories)
    except Exception as e:
        # Ensures error message is shown if error encountered in webpack build
        sys.stdout.write(str(e))
        raise e


def build_templates_config(
    *,
    debug,
    app_root=None,
    additional_directories=None,
    context_processors=None,
):
    """
    Builds a preliminary template config dictionary for this project
    (additional_directories, then app_root) that Django will proritize
    before falling back to INSTALLED_APPS (Arches applications and Arches core).

    Arguments

    debug -- boolean representing the DEBUG value derived from settings
    app_root -- string, os-safe absolute path to application directory
    additional_directories -- list of os-safe absolute paths
    context_processors -- list of strings representing desired context processors
    """
    directories = []
    try:
        if additional_directories:
            for additional_directory in additional_directories:
                directories.append(additional_directory)

        if app_root:
            directories.append(os.path.join(app_root, "templates"))

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
    except Exception as e:
        # Ensures error message is shown if error encountered in webpack build
        sys.stdout.write(str(e))
        raise e


def generate_frontend_configuration(djangoSettings):
    try:
        app_root = os.path.realpath(djangoSettings.APP_ROOT)

        arches_app_names = list_arches_app_names()
        arches_app_paths = list_arches_app_paths()
        path_lookup = dict(zip(arches_app_names, arches_app_paths, strict=True))

        frontend_configuration_settings_data = {
            "_comment": "This is a generated file. Do not edit directly.",
            "APP_ROOT": app_root,
            "ARCHES_APPLICATIONS": arches_app_names,
            "ARCHES_APPLICATIONS_PATHS": path_lookup,
            "SITE_PACKAGES_DIRECTORY": site.getsitepackages()[0],
            "PUBLIC_SERVER_ADDRESS": djangoSettings.PUBLIC_SERVER_ADDRESS,
            "ROOT_DIR": os.path.realpath(djangoSettings.ROOT_DIR),
            "STATIC_URL": djangoSettings.STATIC_URL,
            "WEBPACK_DEVELOPMENT_SERVER_PORT": djangoSettings.WEBPACK_DEVELOPMENT_SERVER_PORT,
        }

        with open(
            os.path.join(app_root, "..", ".frontend-configuration-settings.json"), "w"
        ) as file:
            json.dump(frontend_configuration_settings_data, file, indent=4)

        tsconfig_paths_data = {
            "_comment": "This is a generated file. Do not edit directly.",
            "compilerOptions": {
                "paths": {
                    "@/arches/*": [
                        os.path.join(
                            os.path.relpath(
                                os.path.realpath(
                                    os.path.realpath(djangoSettings.ROOT_DIR)
                                ),
                                os.path.join(app_root, ".."),
                            ),
                            "app",
                            "src",
                            "arches",
                            "*",
                        )
                    ],
                    **{
                        os.path.join("@", path_name, "*"): [
                            os.path.join(
                                os.path.relpath(path, app_root), "src", path_name, "*"
                            )
                        ]
                        for path_name, path in path_lookup.items()
                    },
                }
            },
        }

        with open(os.path.join(app_root, "..", ".tsconfig-paths.json"), "w") as file:
            json.dump(tsconfig_paths_data, file, indent=4)

    except Exception as e:
        # Ensures error message is shown if error encountered
        sys.stderr.write(str(e))
        raise e
