import json
import os
import re
import sys
import sysconfig

from django.conf import settings
from django.urls import get_resolver, URLPattern, URLResolver
from django.urls.resolvers import RegexPattern, RoutePattern, LocalePrefixPattern
from pathlib import Path

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
    def join_paths(*parts):
        first, *middle, last = parts
        segments = [first.rstrip("/")]
        segments += [part.strip("/") for part in middle]
        segments.append(last.lstrip("/"))
        return "/".join(segment for segment in segments if segment)

    def interpolate_route(pattern):
        if isinstance(pattern, RoutePattern):
            return re.sub(r"<(?:[^:]+:)?([^>]+)>", r"{\1}", pattern._route)
        elif isinstance(pattern, RegexPattern):
            regex = pattern._regex.strip("^").rstrip("$")
            regex = re.sub(r"\(\?P<(\w+)>[^)]+\)", r"{\1}", regex)
            regex = re.sub(r"\(\?:[^\)]+\)", "", regex)
            regex = re.sub(r"\[[^\]]+\]", "", regex)
            regex = regex.replace("\\", "")
            regex = re.sub(r"[\^\$\+\*\?\(\)]", "", regex)
            return regex
        return ""

    def build_urls(patterns, prefix="", namespace="", collected_urls=None):
        if collected_urls is None:
            collected_urls = {}

        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                full_name = f"{namespace}{pattern.name}" if pattern.name else None
                path = "/" + join_paths(prefix, interpolate_route(pattern.pattern))
                params = re.findall(r"{([^}]+)}", path)
                key = path.rstrip("/")
                if key not in collected_urls:
                    collected_urls[key] = {
                        "name": full_name,
                        "url": path,
                        "params": params,
                    }

            elif isinstance(pattern, URLResolver):
                next_namespace = (
                    f"{namespace}{pattern.namespace}:"
                    if pattern.namespace
                    else namespace
                )
                if isinstance(pattern.pattern, LocalePrefixPattern):
                    next_prefix = join_paths(prefix, "{language_code}")
                else:
                    next_prefix = join_paths(prefix, interpolate_route(pattern.pattern))
                build_urls(
                    pattern.url_patterns, next_prefix, next_namespace, collected_urls
                )

        return collected_urls

    resolver = get_resolver()
    collected_urls = build_urls(resolver.url_patterns)

    urls_grouped_by_name = {}
    for entry in collected_urls.values():
        name = entry["name"]
        if not name:
            segments = [
                substring
                for substring in entry["url"].split("/")
                if substring and substring != "{language_code}"
            ]
            name = segments[0] if segments else "unnamed"
        urls_grouped_by_name.setdefault(name, []).append(
            {"url": entry["url"], "params": entry["params"]}
        )

    special_urls = {"static_url": settings.STATIC_URL, "media_url": settings.MEDIA_URL}

    for key, url in special_urls.items():
        entry = {"url": url, "params": []}
        urls_grouped_by_name.setdefault(key, [])
        if entry not in urls_grouped_by_name[key]:
            urls_grouped_by_name[key].append(entry)

    sorted_urls = {
        name: urls_grouped_by_name[name] for name in sorted(urls_grouped_by_name)
    }

    destination_path = os.path.realpath(
        os.path.join(_get_base_path(), "..", "frontend_configuration", "urls.json")
    )

    with open(destination_path, "w", encoding="utf-8") as file:
        json.dump(
            {
                "_comment": "This file is auto-generated. Do not edit manually.",
                **sorted_urls,
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

    with open(destination_path, "w", encoding="utf-8") as file:
        json.dump(
            {
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
                        "..",
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
                            "..",
                            os.path.relpath(path, os.path.join(base_path, "..")),
                            "src",
                            path_name,
                            "*",
                        )
                    ]
                    for path_name, path in path_lookup.items()
                },
                "*": ["../node_modules/*"],
            }
        },
    }

    destination_path = os.path.realpath(
        os.path.join(base_path, "..", "frontend_configuration", "tsconfig-paths.json")
    )

    with open(destination_path, "w", encoding="utf-8") as file:
        json.dump(tsconfig_paths_data, file, indent=4)


def _get_base_path():
    return (
        os.path.realpath(settings.ROOT_DIR)
        if Path(settings.APP_ROOT).parent == Path(settings.ROOT_DIR)
        else os.path.realpath(settings.APP_ROOT)
    )
