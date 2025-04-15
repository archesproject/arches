import logging

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _

from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.decorators import group_required
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.views.api import APIBase

logger = logging.getLogger(__name__)


class UserPreferenceListCreateView(APIBase):
    """
    Does not take an identifier, and represents response as a list.  Use for GET and POST requests.
    """

    def get(self, request):
        """
        Returns a list of all current User's preferences.
        Depending on permissions, returns a list of all user preferences.
        """

        # check user permission
        administrator_user = False
        if request.user.groups.filter(name="Application Administrator").exists():
            administrator_user = True

        if administrator_user:  # give view to everything
            return JSONResponse(models.UserPreference.objects.all())
        else:
            return JSONResponse(
                models.UserPreference.objects.filter(username=request.user)
            )

    @method_decorator(group_required("Application Administrator", raise_exception=True))
    def post(self, request):
        try:
            user_pref_json = JSONDeserializer().deserialize(request.body)
        except ValueError:
            return JSONErrorResponse(
                _("Invalid JSON data"),
                _("The User Preference API was sent invalid JSON"),
                status=400,
            )

        try:
            if user_pref_json["userpreferenceid"]:
                return JSONErrorResponse(
                    _("Incorrect User Preference json data"),
                    _(
                        "POST REST request should not have a userpreferenceid provided in the JSON data."
                    ),
                    status=400,
                )
        except KeyError:
            pass

        expected_keys = [
            "preferencename",
            "appname",
            "username",
            "config",
        ]
        if missing_keys := set(expected_keys) - set(user_pref_json):
            return JSONErrorResponse(
                _("JSON payload missing fields"),
                _("The JSON payload is missing the fields {0}").format(missing_keys),
                status=400,
            )

        try:
            preference_user = models.User.objects.get(
                username=user_pref_json["username"]
            )
        except ObjectDoesNotExist:
            return JSONErrorResponse(
                _("Invalid username"),
                _("The User Preference API includes an invalid username."),
                status=400,
            )

        try:
            new_user_preference = models.UserPreference()
            new_user_preference.username = preference_user
            new_user_preference.preferencename = user_pref_json["preferencename"]
            new_user_preference.appname = user_pref_json["appname"]
            new_user_preference.config = user_pref_json["config"]
            new_user_preference.full_clean()
            new_user_preference.save()
            return JSONResponse(new_user_preference, status=201)
        except ValidationError as e:
            return JSONErrorResponse(
                _("Validation Error when creating User Preference"),
                e.messages,
                status=400,
            )


class UserPreferenceDetailView(APIBase):
    """
    Takes an identifier.  Use for GET or DELETE requests to a specific userpreferenceid.
    """

    def get(self, request, identifier):
        """
        Returns specific user preference when given uuid
        If no id specified, and depending on user permissions, returns a list of all user preferences
        """

        # check user permission
        administrator_user = False
        if request.user.groups.filter(name="Application Administrator").exists():
            administrator_user = True

        try:
            returned_user_preference = models.UserPreference.objects.get(pk=identifier)
        except:
            return JSONErrorResponse(
                _("User Preference GET request failed"),
                _("No User Preference with this id"),
                status=404,
            )
        if administrator_user or returned_user_preference.username == request.user:
            return JSONResponse(returned_user_preference)
        else:
            return JSONErrorResponse(
                _("User Preference GET request failed"),
                _("You do not have access to view this userpreferenceid"),
                status=403,
            )

    @method_decorator(group_required("Application Administrator", raise_exception=True))
    def delete(self, request, identifier):
        """
        Delete User Preference with given userpreferenceid.
        """
        user_preference = None
        try:
            user_preference = models.UserPreference.objects.get(pk=identifier)
        except ObjectDoesNotExist:
            return JSONErrorResponse(
                _("User Preference delete failed"),
                _("User Preference does not exist"),
                status=404,
            )
        user_preference.delete()
        return JSONResponse(status=204)
