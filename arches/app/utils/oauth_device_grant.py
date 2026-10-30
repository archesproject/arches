"""
Works around a django-oauth-toolkit bug in the device authorization grant.

DeviceGrant.is_expired compares an aware "now" with the grant's expiry, which
Django stores naive when USE_TZ is False, as it is in Arches. The comparison
raises TypeError, so the page where a user enters their device code fails.
Comparing with django.utils.timezone.now(), which follows USE_TZ, fixes it.

Remove this once a django-oauth-toolkit release with the fix is pinned.
"""

from django.utils import timezone
from oauth2_provider.models import get_device_grant_model


def is_expired(device_grant):
    if device_grant.status == device_grant.EXPIRED:
        return True
    if timezone.now() >= device_grant.expires:
        device_grant.status = device_grant.EXPIRED
        device_grant.save(update_fields=["status"])
        return True
    return False


def patch_device_grant_expiry():
    get_device_grant_model().is_expired = is_expired
