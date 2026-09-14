from django.apps import AppConfig
from django.core.checks import Error, Warning, Tags, register

_CACHE_SETTINGS = [
    ("ARCHES_QUERYSETS_CONCEPT_CACHE", "concept cache"),
    ("ARCHES_QUERYSETS_RESOURCE_INSTANCE_CACHE", "resource instance cache"),
]


class ArchesQuerySetsConfig(AppConfig):
    name = "arches_querysets"
    verbose_name = "Arches QuerySets"
    is_arches_application = True


@register(Tags.caches)
def check_cache_configuration(app_configs, **kwargs):
    from django.conf import settings

    errors = []
    configured_caches = getattr(settings, "CACHES", {})

    for setting_name, label in _CACHE_SETTINGS:
        alias = getattr(settings, setting_name, None)
        if alias is not None and alias not in configured_caches:
            errors.append(
                Error(
                    f"{setting_name}={alias!r} is not defined in settings.CACHES.",
                    hint=f"Add a '{alias}' entry to CACHES or correct {setting_name}.",
                    obj="arches_querysets",
                    id="arches_querysets.E001",
                )
            )
        elif alias is None:
            errors.append(
                Warning(
                    f"{label.capitalize()} is not configured, falling back to the 'default' cache.",
                    hint=f"Set {setting_name} to a dedicated cache alias for better performance.",
                    obj="arches_querysets",
                    id="arches_querysets.W001",
                )
            )

    return errors
