from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from arches.app.models.resource import Resource
from arches.app.models.tile import Tile as TileProxyModel, TileValidationError
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase


@method_decorator(csrf_exempt, name="dispatch")
class Validator(APIBase):
    """
    Class for validating existing objects in the system using GET (resource instances, tiles, etc...)
    or for validating new objects using POST.

    arches-json format is assumed when posting a new resource instance for validation

    Querystring parameters:
    indent -- set to an integer value to format the json to be indented that number of characters
    verbose -- (default is False), set to True to return more information about the validation result
    strict -- (default is True), set to True to force the datatype to perform a more complete check
            (eg: check for the existance of a referenced resoure on the resource-instance datatype)
    """

    def validate_resource(self, resource, verbose, strict):
        errors = resource.validate(verbose=verbose, strict=strict)
        ret = {}

        ret["valid"] = len(errors) == 0
        if verbose:
            ret["errors"] = errors
        return ret

    def validate_tile(self, tile, verbose, strict):
        errors = []
        ret = {}

        try:
            tile.validate(raise_early=(not verbose), strict=strict)
        except TileValidationError as err:
            errors += err.message if isinstance(err.message, list) else [err.message]
        except BaseException as err:
            errors += [str(err)]

        ret["valid"] = len(errors) == 0
        if verbose:
            ret["errors"] = errors
        return ret

    def get(self, request, itemtype=None, itemid=None):
        valid_item_types = ["resource", "tile"]
        if itemtype not in valid_item_types:
            return JSONResponse(
                {
                    "message": f"items to validate can only be of the following types: {valid_item_types} -- eg: .../item_type/item_id"
                },
                status=400,
            )

        indent = request.GET.get("indent", None)
        # default is False
        verbose = False if request.GET.get("verbose", "false").startswith("f") else True
        # default is True
        strict = True if request.GET.get("strict", "true").startswith("t") else False

        if itemtype == "resource":
            try:
                resource = Resource.objects.get(pk=itemid)
            except:
                return JSONResponse(status=404)

            return JSONResponse(
                self.validate_resource(resource, verbose, strict), indent=indent
            )

        if itemtype == "tile":
            try:
                tile = TileProxyModel.objects.get(pk=itemid)
            except:
                return JSONResponse(status=404)

            return JSONResponse(
                self.validate_tile(tile, verbose, strict), indent=indent
            )

        return JSONResponse(status=400)

    def post(self, request, itemtype=None):
        valid_item_types = ["resource", "tile"]
        if itemtype not in valid_item_types:
            return JSONResponse(
                {
                    "message": f"items to validate can only be of the following types: {valid_item_types} -- eg: .../item_type/item_id"
                },
                status=400,
            )

        indent = request.GET.get("indent", None)
        # default is False
        verbose = False if request.GET.get("verbose", "false").startswith("f") else True
        # default is True
        strict = True if request.GET.get("strict", "true").startswith("t") else False
        data = JSONDeserializer().deserialize(request.body)

        if itemtype == "resource":
            resource = Resource()
            for tiledata in data["tiles"]:
                resource.tiles.append(TileProxyModel(tiledata))

            return JSONResponse(
                self.validate_resource(resource, verbose, strict), indent=indent
            )

        if itemtype == "tile":
            tile = TileProxyModel(data)
            return JSONResponse(
                self.validate_tile(tile, verbose, strict), indent=indent
            )

        return JSONResponse(status=400)
