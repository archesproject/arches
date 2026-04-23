from django.http import Http404

from arches.app.datatypes.core.external_domain import BaseExternalDomainDataType
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase


class DatatypeOptions(APIBase):
    """Return ``[{id, text}]`` option pairs for any external-domain datatype.

    Only datatypes that subclass ``BaseExternalDomainDataType`` are supported;
    all others return 404.
    """

    def get(self, request, datatype):
        factory = DataTypeFactory()
        try:
            instance = factory.get_instance(datatype)
        except Exception:
            raise Http404

        if not isinstance(instance, BaseExternalDomainDataType):
            raise Http404

        options = [
            {
                "id": instance.get_option_id(record),
                "text": instance.get_option_display(record),
            }
            for record in instance.get_options_queryset()
        ]
        return JSONResponse({"options": options})
