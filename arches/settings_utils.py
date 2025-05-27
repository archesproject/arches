import os
import sys

from django.apps import apps
from django.contrib.staticfiles.finders import AppDirectoriesFinder


class StaticFilesFinderBuildDirectory(AppDirectoriesFinder):
    source_dir = os.path.join("app", "media", "build")


class StaticFilesFinderMediaRoot(AppDirectoriesFinder):
    source_dir = os.path.join("app", "media")


class StaticFilesFinderNodeModules(AppDirectoriesFinder):
    source_dir = os.path.normpath(os.path.join("..", "node_modules"))


def list_arches_app_names():
    return [
        config.name
        for config in apps.get_app_configs()
        if getattr(config, "is_arches_application", False)
    ]


def list_arches_app_paths():
    return [
        os.path.realpath(config.module.__path__[0])
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
        sys.stderr.write(str(e))
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
        # allows for manual additions to template overrides
        if additional_directories:
            for additional_directory in additional_directories:
                directories.append(additional_directory)

        # allows for application-level overrides of generic Django templates
        if app_root:
            directories.append(os.path.join(app_root, "templates"))

        # forces Arches-level overrides of generic Django templates
        # directories.append(
        #     os.path.join(Path(__file__).resolve().parent, "app", "templates")
        # )

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
        sys.stderr.write(str(e))
        raise e
