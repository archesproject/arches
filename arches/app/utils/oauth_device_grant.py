"""
Works around django-oauth-toolkit issues in the device authorization grant.

1. DeviceGrant.is_expired compares an aware "now" with the grant's expiry, which
Django stores naive when USE_TZ is False, as it is in Arches. The comparison
raises TypeError, so the page where a user enters their device code fails.
Comparing with django.utils.timezone.now(), which follows USE_TZ, fixes it.

2. oauthlib 4.0.1 adds a `scope` key to the device authorization response, which
DeviceAuthorizationView passes to DeviceCodeResponse(**response), and calls a new
RequestValidator.validate_device_code hook that OAuth2Validator lacks
(https://github.com/django-oauth/django-oauth-toolkit/issues/1950).

Remove this once a django-oauth-toolkit release with the fixes is pinned.
"""

from django.utils import timezone
from oauth2_provider.models import get_device_grant_model
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.views import DeviceAuthorizationView
from oauthlib.oauth2.rfc8628.grant_types.device_code import DeviceCodeGrant


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


class ArchesDeviceAuthorizationView(DeviceAuthorizationView):
    def create_device_authorization_response(self, request):
        headers, response, status = super().create_device_authorization_response(
            request
        )
        if status == 200 and isinstance(response, dict):
            response.pop("scope", None)
        return headers, response, status


class ArchesOAuth2Validator(OAuth2Validator):
    def validate_device_code(self, client_id, code, request, *args, **kwargs):
        device_grant = (
            get_device_grant_model()
            .objects.filter(device_code=code, client_id=client_id)
            .first()
        )
        if device_grant is None:
            return None
        if device_grant.is_expired():
            return DeviceCodeGrant.DEVICE_CODE_EXPIRED
        if device_grant.status == device_grant.AUTHORIZED:
            request.user = device_grant.user
            request.scopes = device_grant.scope.split() if device_grant.scope else []
            return DeviceCodeGrant.DEVICE_CODE_AUTHORIZED
        if device_grant.status == device_grant.DENIED:
            return DeviceCodeGrant.DEVICE_CODE_DENIED
        if device_grant.status == device_grant.AUTHORIZATION_PENDING:
            return DeviceCodeGrant.DEVICE_CODE_PENDING
        return None
