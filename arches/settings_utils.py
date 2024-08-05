import json
import os
import site
import sys

from contextlib import contextmanager
from importlib import import_module

from django.apps import apps
from django.conf import settings
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


def get_app_configs_from_module(module_name):
    module = import_module(module_name)
    app_configs = []
    for app_name in getattr(module, "INSTALLED_APPS", []):
        app_config = apps.get_app_config(app_name.split(".")[-1])
        if getattr(app_config, "is_arches_application", False):
            app_configs.append(app_config)
    return app_configs


def list_arches_app_names(application_name=None):
    module_name = (
        f"{application_name if application_name else settings.APP_NAME}.settings"
    ).lower()
    app_configs = get_app_configs_from_module(module_name=module_name)

    return [config.name for config in app_configs]


def list_arches_app_paths(application_name=None):
    module_name = (
        f"{application_name if application_name else settings.APP_NAME}.settings"
    ).lower()
    app_configs = get_app_configs_from_module(module_name=module_name)

    return [config.module.__path__[0] for config in app_configs]


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


def generate_frontend_configuration(app_config):
    try:
        app_root_path = app_config.path
        root_dir_path = os.path.realpath(settings.ROOT_DIR)

        if app_config.name == "arches":
            app_root_path = os.path.join(app_config.path, "app")
            base_path = root_dir_path
        else:
            base_path = app_root_path

        arches_app_names = list_arches_app_names(application_name=app_config.name)
        arches_app_paths = list_arches_app_paths(application_name=app_config.name)
        path_lookup = dict(zip(arches_app_names, arches_app_paths, strict=True))

        frontend_configuration_settings_data = {
            "_comment": "This is a generated file. Do not edit directly.",
            "APP_ROOT": app_root_path,
            "ARCHES_APPLICATIONS": arches_app_names,
            "ARCHES_APPLICATIONS_PATHS": path_lookup,
            "SITE_PACKAGES_DIRECTORY": site.getsitepackages()[0],
            "PUBLIC_SERVER_ADDRESS": settings.PUBLIC_SERVER_ADDRESS,
            "ROOT_DIR": root_dir_path,
            "STATIC_URL": settings.STATIC_URL,
            "WEBPACK_DEVELOPMENT_SERVER_PORT": settings.WEBPACK_DEVELOPMENT_SERVER_PORT,
        }

        frontend_configuration_settings_path = os.path.realpath(
            os.path.join(base_path, "..", ".frontend-configuration-settings.json")
        )

        with open(
            frontend_configuration_settings_path,
            "w",
        ) as file:
            json.dump(frontend_configuration_settings_data, file, indent=4)

        tsconfig_paths_data = {
            "_comment": "This is a generated file. Do not edit directly.",
            "compilerOptions": {
                "paths": {
                    "@/arches/*": [
                        os.path.join(
                            ".",
                            os.path.relpath(
                                root_dir_path,
                                os.path.join(base_path, ".."),
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
                                ".",
                                os.path.relpath(path, os.path.join(base_path, "..")),
                                "src",
                                path_name,
                                "*",
                            )
                        ]
                        for path_name, path in path_lookup.items()
                    },
                }
            },
        }

        tsconfig_path = os.path.realpath(
            os.path.join(base_path, "..", ".tsconfig-paths.json")
        )

        with open(tsconfig_path, "w") as file:
            json.dump(tsconfig_paths_data, file, indent=4)

    except Exception as e:
        # Ensures error message is shown if error encountered
        sys.stderr.write(str(e))
        raise e
