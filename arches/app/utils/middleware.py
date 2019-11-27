import time
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User, AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.utils.six import text_type
from django.utils.translation import ugettext as _
from arches.app.models.system_settings import settings
from arches.app.utils.response import Http401Response
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

HTTP_HEADER_ENCODING = "iso-8859-1"


class SetAnonymousUser(MiddlewareMixin):
    def process_request(self, request):
        # for OAuth authentication to work, we can't automatically assign
        # the anonymous user to the request, otherwise the anonymous user is
        # used for all OAuth resourse requests
        if request.path != reverse("oauth2:authorize") and request.user.is_anonymous:
            try:
                request.user = User.objects.get(username="anonymous")
            except Exception:
                pass


class ModifyAuthorizationHeader(MiddlewareMixin):
    def process_request(self, request):
        # for OAuth authentication to work, we must use the standard
        # HTTP_AUTHORIZATION header. So, if the request has the alternate
        # HTTP_X_AUTHORIZATION header, update the request to use the standard
        if request.META.get("HTTP_X_AUTHORIZATION", None) is not None:
            request.META["HTTP_AUTHORIZATION"] = request.META.get("HTTP_X_AUTHORIZATION")
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
        if isinstance(auth, text_type):
            # Work around django test client oddness
            auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth

    def process_request(self, request):
        token = self.get_authorization_header(request)
        request.token = token


class AuthenticationFailed(Exception):
    pass
