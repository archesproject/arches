from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase


class TransformEdtfForTile(APIBase):
    def get(self, request):
        try:
            value = request.GET.get("value")
            datatype_factory = DataTypeFactory()
            edtf_datatype = datatype_factory.get_instance("edtf")
            transformed_value = edtf_datatype.transform_value_for_tile(value)
            is_valid = len(edtf_datatype.validate(transformed_value)) == 0
            result = (transformed_value, is_valid)

        except TypeError as e:
            return JSONResponse({"data": (str(e), False)})

        except Exception as e:
            return JSONResponse(str(e), status=500)

        return JSONResponse({"data": result})
