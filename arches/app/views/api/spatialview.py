import logging

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _

from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.decorators import group_required
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.views.api import APIBase

logger = logging.getLogger(__name__)


class SpatialView(APIBase):
    def get(self, request, identifier=None):
        """
        Returns a permitted spatial view given an id
        otherwise returns a list of permitted spatial views
        """
        spatialview_id = None

        # ensure specific spatial view exists before proceeding
        if identifier:
            spatialview_id = identifier
            if not models.SpatialView.objects.filter(pk=identifier).exists():
                return JSONErrorResponse(
                    _("No Spatial View Exists with this id"), status=404
                )

        permitted_nodegroupids = get_nodegroups_by_perm(
            request.user, "models.read_nodegroup"
        )

        permitted_spatialviews = models.SpatialView.objects.filter(
            geometrynode__nodegroup_id__in=permitted_nodegroupids
        )

        if identifier:
            permitted_spatialviews = permitted_spatialviews.filter(pk=spatialview_id)
            if not len(permitted_spatialviews):
                return JSONErrorResponse(
                    _("Request Failed"), _("Permission Denied"), status=403
                )

        response_data = [
            spatialview.to_json() for spatialview in permitted_spatialviews
        ]

        # when using identifier, return a single object instead of a list
        if len(response_data) == 1 and identifier:
            response_data = response_data[0]

        return JSONResponse(response_data)

    def transform_json_data_for_spatialview(self, json_data):
        """
        Transforms the JSON data object to be used in the spatialview model
        """

        json_data["geometrynode_id"] = json_data.pop("geometrynodeid")
        json_data["language_id"] = json_data.pop("language")

        return json_data

    def create_spatialview_from_json_data(self, json_data):
        """
        Returns a SpatialView object from the JSON data. Should only be used if the JSON data has been validated.
        """

        json_data = self.transform_json_data_for_spatialview(json_data)

        try:
            spatialview = models.SpatialView.objects.get(pk=json_data["spatialviewid"])
        except KeyError:
            # if no spatialviewid is provided then is from POST so create a new spatialview object
            spatialview = models.SpatialView(**json_data)
            return spatialview
        except ObjectDoesNotExist:
            return JSONErrorResponse(
                _("Spatialview not found"),
                _("No Spatialview exists for the provided spatialviewid"),
                status=404,
            )

        # update the spatialview object with the new data
        for key, value in json_data.items():
            setattr(spatialview, key, value)

        return spatialview

    def validate_json_data_content(
        self, json_data, spatialviewid_identifier=None, is_post=False
    ):
        """
        Validates the JSON data passed in the request body where not handled by model validation.

        returns a JSONErrorResponse if validation fails or SpatialView if validation passes
        """

        if is_post and "spatialviewid" in json_data.keys():
            return JSONErrorResponse(
                _("Incorrect Spatialview json data"),
                _(
                    "POST REST request should not have a spatialviewid provided in the JSON data."
                ),
                status=400,
            )

        # Check if spatialviewid_identifier matches the spatialviewid in the json_data
        if spatialviewid_identifier:
            if "spatialviewid" in json_data:
                if spatialviewid_identifier != json_data["spatialviewid"]:
                    return JSONErrorResponse(
                        _("Incorrect Spatialview json data"),
                        _(
                            "Spatialviewid in the URL does not match the spatialviewid in the JSON data."
                        ),
                        status=400,
                    )
            else:
                return JSONErrorResponse(
                    _("Incorrect Spatialview json data"),
                    _("No spatialviewid provided in the JSON data."),
                    status=400,
                )

        # Check if geometrynodeid exists in the database before transforming the json data
        try:
            if not models.Node.objects.filter(pk=json_data["geometrynodeid"]).exists():
                return JSONErrorResponse(
                    _("Incorrect Spatialview json data"),
                    _("No geometrynode exists with the provided geometrynodeid."),
                    status=400,
                )

            # Check if language exists in the database before transforming the json data
            if not models.Language.objects.filter(code=json_data["language"]).exists():
                return JSONErrorResponse(
                    _("Incorrect Spatialview json data"),
                    _("No language exists with the provided language code."),
                    status=400,
                )
        except KeyError:
            return JSONErrorResponse(
                _("Incorrect Spatialview json data"),
                _("The JSON data provided is missing required fields."),
                status=400,
            )

        return self.create_spatialview_from_json_data(json_data)

    @method_decorator(group_required("Application Administrator", raise_exception=True))
    def post(self, request, identifier=None):

        # if identifier is not None then the user is trying to update a spatialview so an error should be returned with a message
        if identifier:
            return JSONErrorResponse(
                _("Spatialview creation failed"),
                _("POST request should not have a spatialviewid provided in the URL"),
                status=400,
            )

        try:
            json_data = JSONDeserializer().deserialize(request.body)
        except ValueError:
            return JSONErrorResponse(
                _("Invalid JSON data"),
                _("The Spatialview API was sent invalid JSON"),
                status=400,
            )

        if json_data is not None:

            validate_json_data_content_result = self.validate_json_data_content(
                json_data, is_post=True
            )
            if isinstance(validate_json_data_content_result, JSONErrorResponse):
                return validate_json_data_content_result

            spatialview = validate_json_data_content_result

            try:
                spatialview.full_clean()
                spatialview.save()
            except ValidationError as e:
                return JSONErrorResponse(
                    _("Validation Error when creating Spatialview"),
                    e.messages,
                    status=400,
                )

            return JSONResponse(spatialview.to_json(), status=201)
        return JSONErrorResponse(_("No json request payload"), status=400)

    @method_decorator(group_required("Application Administrator", raise_exception=True))
    def put(self, request, identifier=None):

        if not identifier:
            return JSONErrorResponse(
                _("Spatialview update failed"),
                _(
                    "PUT REST request requires a spatialviewid to be provided in the URL"
                ),
                status=400,
            )

        try:
            json_data = JSONDeserializer().deserialize(request.body)
        except ValueError:
            return JSONErrorResponse(
                _("Invalid JSON data"),
                _("The Spatialview API was sent invalid JSON"),
                status=400,
            )

        if json_data is not None:

            validate_json_data_content_result = self.validate_json_data_content(
                json_data, identifier
            )
            if isinstance(validate_json_data_content_result, JSONErrorResponse):
                return validate_json_data_content_result

            spatialview = validate_json_data_content_result

            try:
                spatialview.full_clean()
                spatialview.save()
            except ValidationError as e:
                return JSONErrorResponse(
                    _("Validation Error when updating Spatialview"),
                    e.messages,
                    status=400,
                )

            return JSONResponse(spatialview.to_json(), status=200)
        return JSONErrorResponse(
            _("Spatialview update failed"), _("No json request payload"), status=400
        )

    @method_decorator(group_required("Application Administrator", raise_exception=True))
    def delete(self, request, identifier=None):
        if identifier:
            spatialview = None
            try:
                spatialview = models.SpatialView.objects.get(pk=identifier)
            except ObjectDoesNotExist:
                return JSONErrorResponse(
                    _("Spatialview delete failed"),
                    _("Spatialview does not exist"),
                    status=404,
                )

            try:
                spatialview.delete()
            except Exception as e:
                logger.error(e)
                return JSONErrorResponse(
                    _("Spatialview delete failed"),
                    _("An error occurred when trying to delete the spatialview"),
                    status=500,
                )

        else:
            return JSONErrorResponse(
                _("Spatialview delete failed"),
                _(
                    "DELETE REST request requires a spatialviewid to be provided in the URL"
                ),
                status=400,
            )
        return JSONResponse(status=204)
