import re

from django.conf import settings
from django.urls import get_resolver, URLPattern, URLResolver
from django.urls.resolvers import RegexPattern, RoutePattern, LocalePrefixPattern


def _interpolate_route(resolver_pattern):
    if isinstance(resolver_pattern, RoutePattern):
        return re.sub(r"<(?:[^:]+:)?([^>]+)>", r"{\1}", resolver_pattern._route)
    if isinstance(resolver_pattern, RegexPattern):
        regex_string = resolver_pattern._regex
        regex_string = regex_string.strip("^")
        regex_string = regex_string.rstrip("$")
        regex_string = re.sub(r"\(\?P<(\w+)>[^)]+\)", r"{\1}", regex_string)
        regex_string = re.sub(r"\(\?:[^)]+\)", "", regex_string)
        regex_string = re.sub(r"\[[^\]]+\]", "", regex_string)
        regex_string = regex_string.replace("\\", "")
        regex_string = re.sub(r"[\^\$\+\*\?\(\)]", "", regex_string)
        regex_string = re.sub(r"//+", "/", regex_string)
        regex_string = regex_string.strip("/")
        return regex_string
    return ""


def _join_paths(left_path, right_path):
    left_clean = (left_path or "").strip("/")
    right_clean = (right_path or "").strip("/")
    if left_clean and right_clean:
        return left_clean + "/" + right_clean
    if left_clean:
        return left_clean
    return right_clean


def _get_top_level_package_name(module_name):
    if not module_name:
        return ""
    parts = module_name.split(".", 1)
    return parts[0]


def _get_pattern_origin_application_name(url_pattern):
    lookup_string = getattr(url_pattern, "lookup_str", "") or ""
    if lookup_string:
        module_name = lookup_string.rsplit(".", 1)[0]
    else:
        callback_object = getattr(url_pattern, "callback", None)
        module_name = getattr(callback_object, "__module__", "") or ""
    return _get_top_level_package_name(module_name)


def _get_resolver_origin_application_name(url_resolver):
    urlconf_module = getattr(url_resolver, "urlconf_module", None)
    module_name = getattr(urlconf_module, "__name__", "") or ""
    return _get_top_level_package_name(module_name)


def _select_effective_namespace(namespace_stack, origin_application_name):
    for namespace_value, namespace_origin in reversed(namespace_stack):
        if namespace_value and namespace_origin == origin_application_name:
            return namespace_value
    return origin_application_name


def _first_significant_path_segment(path_string):
    segments = [segment for segment in path_string.split("/") if segment]
    if not segments:
        return ""
    if segments[0] == "{language_code}" and len(segments) > 1:
        return segments[1]
    return segments[0]


def _path_has_i18n_prefix(path_string):
    segments = [segment for segment in path_string.split("/") if segment]
    return bool(segments and segments[0] == "{language_code}")


def _walk_url_patterns(
    url_patterns, accumulated_prefix, namespace_stack, collected_entries
):
    for url_object in url_patterns:
        if isinstance(url_object, URLPattern):
            origin_application_name = _get_pattern_origin_application_name(url_object)
            effective_namespace = _select_effective_namespace(
                namespace_stack, origin_application_name
            )

            route_text = _interpolate_route(url_object.pattern)
            joined_path = _join_paths(accumulated_prefix, route_text)
            path_string = "/" + joined_path if joined_path else "/"

            path_parameters = re.findall(r"{([^}]+)}", path_string)
            is_unnamed = not bool(url_object.name)
            is_admin = _first_significant_path_segment(path_string) == "admin"

            if is_admin and is_unnamed:
                if _path_has_i18n_prefix(path_string):
                    collapsed_path = "/{language_code}/admin/{url}"
                    collapsed_params = ["language_code", "url"]
                else:
                    collapsed_path = "/admin/{url}"
                    collapsed_params = ["url"]
                collapsed_key = (collapsed_path, "admin")
                if collapsed_key not in collected_entries:
                    collected_entries[collapsed_key] = {
                        "name": "admin",
                        "url": collapsed_path,
                        "params": collapsed_params,
                    }
                continue

            if url_object.name:
                route_name = (
                    effective_namespace + ":" + url_object.name
                    if effective_namespace
                    else url_object.name
                )
            else:
                base_segment = _first_significant_path_segment(path_string) or "unnamed"
                route_name = (
                    effective_namespace + ":" + base_segment
                    if effective_namespace
                    else base_segment
                )

            force_script_name = ""
            if settings.FORCE_SCRIPT_NAME:
                force_script_name = settings.FORCE_SCRIPT_NAME.rstrip("/")

            normalized_path_key = path_string.rstrip("/") or "/"
            deduplication_key = (normalized_path_key, route_name)
            if deduplication_key not in collected_entries:
                collected_entries[deduplication_key] = {
                    "name": route_name,
                    "url": force_script_name + path_string,
                    "params": path_parameters,
                }

        elif isinstance(url_object, URLResolver):
            next_namespace_stack = list(namespace_stack)
            namespace_value = getattr(url_object, "namespace", "")
            if namespace_value:
                namespace_origin_application = _get_resolver_origin_application_name(
                    url_object
                )
                next_namespace_stack.append(
                    (namespace_value, namespace_origin_application)
                )

            if isinstance(url_object.pattern, LocalePrefixPattern):
                resolver_route_text = "{language_code}"
            else:
                resolver_route_text = _interpolate_route(url_object.pattern)

            next_prefix = _join_paths(accumulated_prefix, resolver_route_text)
            _walk_url_patterns(
                url_object.url_patterns,
                next_prefix,
                next_namespace_stack,
                collected_entries,
            )


def generate_urls_json():
    root_url_resolver = get_resolver()
    collected_entries = {}
    _walk_url_patterns(root_url_resolver.url_patterns, "", [], collected_entries)

    grouped_by_route_name = {}
    for collected_value in collected_entries.values():
        route_name = collected_value["name"]
        route_entry = {
            "url": collected_value["url"],
            "params": collected_value["params"],
        }
        existing_list = grouped_by_route_name.setdefault(route_name, [])
        if route_entry not in existing_list:
            existing_list.append(route_entry)

    root_urlconf_module = getattr(root_url_resolver, "urlconf_module", None)
    root_module_name = getattr(root_urlconf_module, "__name__", "") or ""
    project_namespace = _get_top_level_package_name(root_module_name)

    special_route_entries = {
        project_namespace + ":static_url": settings.STATIC_URL,
        project_namespace + ":media_url": settings.MEDIA_URL,
    }

    for special_route_name, special_url_value in special_route_entries.items():
        special_entry = {"url": special_url_value, "params": []}
        existing_list = grouped_by_route_name.setdefault(special_route_name, [])
        if special_entry not in existing_list:
            existing_list.append(special_entry)

    return {name: grouped_by_route_name[name] for name in sorted(grouped_by_route_name)}
