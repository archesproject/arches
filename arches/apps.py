import warnings
from importlib.metadata import PackageNotFoundError, requires
from pathlib import Path

from django.apps import AppConfig, apps
from django.conf import settings
from django.core.checks import register, Tags, Error, Warning
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
        try:
            project_requirements = requires(config.name)
        except PackageNotFoundError:
            # Not installed by pip: read pyproject.toml directly
            toml_path = Path(config.path).parent / "pyproject.toml"
            if not toml_path.exists():  # pragma: no cover
                raise ValueError
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)
                try:
                    project_requirements = data["project"]["dependencies"]
                except KeyError:  # pragma: no cover
                    raise ValueError from None
        try:
            for requirement in project_requirements:
                if requirement.lower().startswith("arches"):
                    parsed_arches_requirement = SimpleSpec(
                        requirement.lower().replace("arches", "").lstrip()
                    )
                    break
            else:
                raise ValueError
        except ValueError:
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
                Error(
                    f"Incompatible arches requirement for Arches version: {arches_version}",
                    obj=config.name,
                    hint=requirement,
                    id="arches.E003",
                )
            )

    return errors
