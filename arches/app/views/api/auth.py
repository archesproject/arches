from http import HTTPStatus

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.debug import sensitive_variables, sensitive_post_parameters
from django_ratelimit.decorators import ratelimit

from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.views.api import APIBase


class Login(LoginView, APIBase):
    """Inherit from LoginView to get @csrf_protect etc. on dispatch()."""

    http_method_names = ["post"]

    @method_decorator(
        (
            sensitive_variables(),
            sensitive_post_parameters(),
            ratelimit(key="post:username", rate=settings.RATE_LIMIT, block=False),
        )
    )
    def post(self, request):
        if getattr(request, "limited", False):
            return JSONErrorResponse(status=HTTPStatus.TOO_MANY_REQUESTS)

        failure_title = _("Login failed")
        failure_msg_invalid = _("Invalid username and/or password.")
        failure_msg_inactive = _("This account is no longer active.")

        data = JSONDeserializer().deserialize(request.body)
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return JSONErrorResponse(
                failure_title, failure_msg_invalid, status=HTTPStatus.UNAUTHORIZED
            )

        user = authenticate(username=username, password=password)
        if user is None:
            return JSONErrorResponse(
                failure_title, failure_msg_invalid, status=HTTPStatus.UNAUTHORIZED
            )
        if not user.is_active:
            # ModelBackend already disallows inactive users, but add some safety
            # and disallow this no matter the backend for now.
            return JSONErrorResponse(
                failure_title, failure_msg_inactive, status=HTTPStatus.FORBIDDEN
            )
        if settings.FORCE_TWO_FACTOR_AUTHENTICATION or (
            settings.ENABLE_TWO_FACTOR_AUTHENTICATION
            and user.userprofile.encrypted_mfa_hash
        ):
            return JSONErrorResponse(
                title=_("Two-factor authentication required."),
                message=_("Use the provided link to log in."),
                status=HTTPStatus.UNAUTHORIZED,
            )

        login(request, user)

        fields = {"first_name", "last_name", "username"}
        return JSONResponse(JSONSerializer().serialize(request.user, fields=fields))


class Logout(LogoutView):
    def post(self, request):
        logout(request)
        return JSONResponse(status=HTTPStatus.NO_CONTENT)
