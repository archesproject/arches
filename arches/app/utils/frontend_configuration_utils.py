import json
import os
import re
import site
import sys

from django.conf import settings
from django.urls import get_resolver, URLPattern, URLResolver
from django.urls.resolvers import RegexPattern, RoutePattern, LocalePrefixPattern

from arches.settings_utils import list_arches_app_names, list_arches_app_paths


def generate_frontend_configuration():
    try:
        _generate_frontend_configuration_directory()
        _generate_urls_json()
        _generate_webpack_configuration()
        _generate_tsconfig_paths()
    except Exception as e:
        # Ensures error message is shown if error encountered
        sys.stderr.write(str(e))
        raise e


def _generate_frontend_configuration_directory():
    destination_dir = os.path.realpath(
        os.path.join(_get_base_path(), "..", "frontend_configuration")
    )

    os.makedirs(destination_dir, exist_ok=True)


def _generate_urls_json():
    def generate_human_readable_urls(patterns, prefix="", namespace="", result={}):
        def join_paths(*args):
            return "/".join(filter(None, (arg.strip("/") for arg in args)))

        def interpolate_route(pattern):
            if isinstance(pattern, RoutePattern):
                return re.sub(r"<(?:[^:]+:)?([^>]+)>", r"{\1}", pattern._route)
            elif isinstance(pattern, RegexPattern):
                regex = pattern._regex.lstrip("^").rstrip("$")

                # Replace named capture groups (e.g., (?P<param>)) with {param}
                regex = re.sub(r"\(\?P<(\w+)>[^)]+\)", r"{\1}", regex)

                # Remove non-capturing groups (e.g., (?:...))
                regex = re.sub(r"\(\?:[^\)]+\)", "", regex)

                # Remove character sets (e.g., [0-9])
                regex = re.sub(r"\[[^\]]+\]", "", regex)

                # Remove backslashes (used to escape special characters in regex)
                regex = regex.replace("\\", "")

                # Remove regex-specific special characters (^, $, +, *, ?, (), etc.)
                regex = re.sub(r"[\^\$\+\*\?\(\)]", "", regex)

                return regex.strip("/")

        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                if pattern.name:
                    result[f"{namespace}{pattern.name}"] = "/" + join_paths(
                        prefix, interpolate_route(pattern.pattern)
                    )
            elif isinstance(pattern, URLResolver):
                current_namespace = namespace + (
                    f":{pattern.namespace}:" if pattern.namespace else ""
                )

                if isinstance(
                    pattern.pattern, LocalePrefixPattern
                ):  # handles i18n_patterns
                    new_prefix = join_paths(prefix, "{language_code}")
                else:
                    new_prefix = join_paths(prefix, interpolate_route(pattern.pattern))

                generate_human_readable_urls(
                    pattern.url_patterns, new_prefix, current_namespace, result
                )
        return result

    resolver = get_resolver()
    human_readable_urls = generate_human_readable_urls(resolver.url_patterns)

    # manual additions
    human_readable_urls["static_url"] = settings.STATIC_URL
    human_readable_urls["media_url"] = settings.MEDIA_URL

    destination_path = os.path.realpath(
        os.path.join(_get_base_path(), "..", "frontend_configuration", "urls.json")
    )

    with open(destination_path, "w") as file:
        json.dump(
            {
                "_comment": "This is a generated file. Do not edit directly.",
                **{
                    url_name: human_readable_urls[url_name]
                    for url_name in sorted(human_readable_urls)
                },
            },
            file,
            indent=4,
        )


def _generate_webpack_configuration():
    app_root_path = os.path.realpath(settings.APP_ROOT)
    root_dir_path = os.path.realpath(settings.ROOT_DIR)

    arches_app_names = list_arches_app_names()
    arches_app_paths = list_arches_app_paths()

    destination_path = os.path.realpath(
        os.path.join(
            _get_base_path(), "..", "frontend_configuration", "webpack-metadata.json"
        )
    )

    with open(destination_path, "w") as file:
        json.dump(
            {
                "_comment": "This is a generated file. Do not edit directly.",
                "APP_ROOT": app_root_path,
                "ARCHES_APPLICATIONS": arches_app_names,
                "ARCHES_APPLICATIONS_PATHS": dict(
                    zip(arches_app_names, arches_app_paths, strict=True)
                ),
                "SITE_PACKAGES_DIRECTORY": site.getsitepackages()[0],
                "PUBLIC_SERVER_ADDRESS": settings.PUBLIC_SERVER_ADDRESS,
                "ROOT_DIR": root_dir_path,
                "STATIC_URL": settings.STATIC_URL,
                "WEBPACK_DEVELOPMENT_SERVER_PORT": settings.WEBPACK_DEVELOPMENT_SERVER_PORT,
            },
            file,
            indent=4,
        )


def _generate_tsconfig_paths():
    base_path = _get_base_path()
    root_dir_path = os.path.realpath(settings.ROOT_DIR)

    path_lookup = dict(
        zip(list_arches_app_names(), list_arches_app_paths(), strict=True)
    )

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
                "*": ["./node_modules/*"],
            }
        },
    }

    destination_path = os.path.realpath(
        os.path.join(base_path, "..", "frontend_configuration", "tsconfig-paths.json")
    )

    with open(destination_path, "w") as file:
        json.dump(tsconfig_paths_data, file, indent=4)


def _get_base_path():
    return (
        os.path.realpath(settings.ROOT_DIR)
        if settings.APP_NAME == "Arches"
        else os.path.realpath(settings.APP_ROOT)
    )
