import json
import os
import re

from collections import OrderedDict
from django.conf import settings
from django.urls import get_resolver, URLPattern, URLResolver
from django.urls.resolvers import RegexPattern, RoutePattern, LocalePrefixPattern


def get_base_path():
    return (
        os.path.realpath(settings.ROOT_DIR)
        if settings.APP_NAME == "Arches"
        else os.path.realpath(settings.APP_ROOT)
    )


def generate_frontend_configuration_directory():
    destination_dir = os.path.realpath(
        os.path.join(get_base_path(), "..", "frontend_configuration")
    )

    os.makedirs(destination_dir, exist_ok=True)


def generate_urls_json():
    resolver = get_resolver()
    human_readable_urls = _generate_human_readable_urls(resolver.url_patterns)

    destination_path = os.path.realpath(
        os.path.join(get_base_path(), "..", "frontend_configuration", "urls.json")
    )

    with open(destination_path, "w") as file:
        json.dump(
            {
                url_name: human_readable_urls[url_name]
                for url_name in sorted(human_readable_urls)
            },
            file,
            indent=4,
        )


def _generate_human_readable_urls(patterns, prefix="", namespace="", result={}):
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

            _generate_human_readable_urls(
                pattern.url_patterns, new_prefix, current_namespace, result
            )
    return result
