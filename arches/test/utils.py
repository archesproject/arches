from contextlib import contextmanager

from arches.app.models.system_settings import settings


@contextmanager
def sync_overridden_test_settings_to_arches():
    """Django's @override_settings test util acts on django.conf.settings,
    which is not enough for us, because we use SystemSettings at runtime.

    This context manager swaps in the overridden django.conf.settings for SystemSettings.
    """
    from django.conf import settings as patched_settings

    original_settings_wrapped = settings._wrapped
    try:
        settings._wrapped = patched_settings._wrapped
        yield
    finally:
        settings._wrapped = original_settings_wrapped
