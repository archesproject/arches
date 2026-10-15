import time
from django.urls import Resolver404, resolve
from django.http import HttpResponse
from django.contrib.auth.models import User, AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.utils.translation import gettext as _
from arches.app.models.system_settings import settings
from arches.app.utils.response import Http401Response
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

HTTP_HEADER_ENCODING = "iso-8859-1"


# Pages where a person approves an OAuth client. They must send visitors who
# aren't signed in to the login page, not approve the client as "anonymous".
OAUTH_APPROVAL_URL_NAMES = {
    "authorize",
    "device",
    "device-confirm",
    "device-grant-status",
}


def is_oauth_approval_page(request):
    try:
        resolved_url = resolve(request.path_info)
    except Resolver404:
        return False
    return (
        resolved_url.namespace == "oauth2"
        and resolved_url.url_name in OAUTH_APPROVAL_URL_NAMES
    )


class SetAnonymousUser(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_anonymous and not is_oauth_approval_page(request):
            try:
                request.user = (
                    User.objects.filter(username="anonymous")
                    .select_related("userprofile")
                    .get()
                )
            except Exception:
                pass


class ModifyAuthorizationHeader(MiddlewareMixin):
    def process_request(self, request):
        # for OAuth authentication to work, we must use the standard
        # HTTP_AUTHORIZATION header. So, if the request has the alternate
        # HTTP_X_AUTHORIZATION header, update the request to use the standard
        if request.META.get("HTTP_X_AUTHORIZATION", None) is not None:
            request.META["HTTP_AUTHORIZATION"] = request.META.get(
                "HTTP_X_AUTHORIZATION"
            )
            del request.META["HTTP_X_AUTHORIZATION"]


class TokenMiddleware(MiddlewareMixin):
    """
    puts the Bearer token found in the request header onto the request object

    pulled from http://www.django-rest-framework.org

    """

    def get_authorization_header(self, request):
        """
        Return request's 'Authorization:' header, as a bytestring.
        Hide some test client ickyness where the header can be unicode.
        """
        auth = request.META.get("HTTP_AUTHORIZATION", b"").replace("Bearer ", "")
        if isinstance(auth, str):
            # Work around django test client oddness
            auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth

    def process_request(self, request):
        token = self.get_authorization_header(request)
        request.token = token


class AuthenticationFailed(Exception):
    pass
