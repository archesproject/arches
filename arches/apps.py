from django.conf import settings
from django.core.checks import register, Tags, Error


@register(Tags.security)
def check_cache_backend_for_production(app_configs, **kwargs):
    errors = []
    your_cache = settings.CACHES["default"]["BACKEND"]
    if not settings.DEBUG and your_cache == "django.core.cache.backends.dummy.DummyCache":
        errors.append(
            Error(
                "Using dummy cache in production",
                id="arches.E001",
            )
        )
    return errors
