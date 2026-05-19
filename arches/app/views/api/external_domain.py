from arches.app.datatypes.core.external_domain import BaseExternalDomainDataType
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.views.api import APIBase


class ExternalDomainOptions(APIBase):
    """Return ``[{id, text}]`` option pairs for any external-domain datatype.

    Only datatypes that subclass ``BaseExternalDomainDataType`` are supported.
    """

    def get(self, request, datatype):
        factory = DataTypeFactory()
        try:
            instance = factory.get_instance(datatype)
        except Exception as e:
            raise JSONErrorResponse(status=500, reason=e)

        if not isinstance(instance, BaseExternalDomainDataType):
            raise JSONErrorResponse(status=400, reason=f"{datatype} not supported")

        options = [
            {
                "id": instance.get_option_id(record),
                "text": instance.get_option_display(record),
            }
            for record in instance.get_options_queryset()
        ]
        return JSONResponse({"options": options})
