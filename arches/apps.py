import warnings

from django.apps import AppConfig
from django.conf import settings
from django.core.checks import register, Tags, Error, Warning


class ArchesAppConfig(AppConfig):
    name = "arches"
    verbose_name = "Arches"
    is_arches_application = False


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
