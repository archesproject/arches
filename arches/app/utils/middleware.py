from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin


class SetAnonymousUser(MiddlewareMixin):
    def process_request(self, request):
        # for OAuth authentication to work, we can't automatically assign
        # the anonymous user to the request, otherwise the anonymous user is
        # used for all OAuth resourse requests
        if request.path != reverse("oauth2:authorize") and request.user.is_anonymous:
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
