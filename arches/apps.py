import re
import warnings
from importlib.metadata import PackageNotFoundError, requires
from pathlib import Path

from django.apps import AppConfig, apps
from django.conf import settings
from django.core.checks import register, CheckMessage, Error, Tags, Warning
from django.core.checks.messages import ERROR, WARNING
from semantic_version import SimpleSpec, Version

from arches import __version__
from arches.settings_utils import generate_frontend_configuration

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    # Python 3.10 depends on tomli instead
    import tomli as tomllib


class ArchesAppConfig(AppConfig):
    name = "arches"
    verbose_name = "Arches"
    is_arches_application = False

    def ready(self):
        if settings.APP_NAME.lower() == self.name:
            generate_frontend_configuration()


### GLOBAL DEPRECATIONS ###
FILE_TYPE_CHECKING_MSG = (
    "Providing boolean values to FILE_TYPE_CHECKING is deprecated. "
    "Starting with Arches 8.0, the only allowed options will be "
    "None, 'lenient', and 'strict'."
)
if settings.FILE_TYPE_CHECKING in (True, False):
    warnings.warn(FILE_TYPE_CHECKING_MSG, DeprecationWarning)


### SYSTEM CHECKS ###
@register(Tags.security)
def check_cache_backend_for_production(app_configs, **kwargs):
    errors = []
    your_cache = settings.CACHES["default"]["BACKEND"]
    if (
        not settings.DEBUG
        and your_cache == "django.core.cache.backends.dummy.DummyCache"
    ):
        errors.append(
            Error(
                "Using dummy cache in production",
                id="arches.E001",
            )
        )
    return errors


@register(Tags.security)
def check_cache_backend(app_configs, **kwargs):
    errors = []
    supported_by_django_ratelimit = (
        "django.core.cache.backends.memcached.PyLibMCCache",
        "django.core.cache.backends.memcached.PyMemcacheCache",
        "django.core.cache.backends.redis.RedisCache",
    )
    your_cache = settings.CACHES["default"]["BACKEND"]
    if your_cache not in supported_by_django_ratelimit:
        errors.append(
            Warning(
                "Cache backend does not support rate-limiting",
                hint=f"Your cache: {your_cache}\n\tSupported caches: {supported_by_django_ratelimit}",
                id="arches.W001",
            )
        )
    return errors


@register(Tags.compatibility)
def check_arches_compatibility(app_configs, **kwargs):
    def read_project_requirements_from_toml_file(config: AppConfig):
        with open(Path(config.path).parent / "pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        try:
            project_requirements = data["project"]["dependencies"]
        except KeyError:  # pragma: no cover
            raise ValueError from None
        return project_requirements

    try:
        arches_version = Version(__version__)
    except ValueError:
        arches_version = Version.coerce(__version__)

    if app_configs is None:
        app_configs = apps.get_app_configs()

    errors = []
    for config in app_configs:
        if not getattr(config, "is_arches_application", False):
            continue
        project_requirements = ["No project requirements found."]

        try:
            project_requirements = requires(config.name)
        except PackageNotFoundError:
            # Not installed by pip: read pyproject.toml directly
            project_requirements = read_project_requirements_from_toml_file(config)

        for requirement in project_requirements:
            to_parse = requirement.lower()
            # Normalize "arches" [requires() output] to "arches " [raw toml file]
            # So we can split on a consistent separator (space)
            to_parse = to_parse.replace("arches", "arches ")
            if to_parse.split()[0] == "arches":
                to_parse = requirement.lower().replace("arches", "").lstrip()
            else:
                continue
            # Some arches tags didn't use hyphens, so provide them.
            to_parse = re.sub(r"0(a|b|rc)", r"0-\1", to_parse)
            try:
                parsed_arches_requirement = SimpleSpec(to_parse)
            except ValueError:
                # might have been arches-for-x==3 -> for-x==3, not valid; keep searching.
                continue
            break
        else:
            errors.append(
                Error(
                    f"Invalid or missing arches requirement",
                    obj=config.name,
                    hint=project_requirements,
                    id="arches.E002",
                )
            )
            continue

        if arches_version not in parsed_arches_requirement:
            errors.append(
                CheckMessage(
                    level=WARNING if settings.DEBUG else ERROR,
                    msg=f"Incompatible arches requirement for Arches version: {arches_version}",
                    obj=config.name,
                    hint=requirement,
                    id="arches.E003",
                )
            )

    return errors


@register(Tags.compatibility)
def warn_old_compatibility_settings(app_configs, **kwargs):
    errors = []

    if getattr(settings, "MIN_ARCHES_VERSION", None) or getattr(
        settings, "MAX_ARCHES_VERSION", None
    ):
        errors.append(
            Warning(
                msg=f"MIN_ARCHES_VERSION and MAX_ARCHES_VERSION have no effect.",
                hint="Migrate your version range to pyproject.toml.",
                id="arches.W002",
            )
        )
    return errors
