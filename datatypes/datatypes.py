import django.db.models

from arches import VERSION as arches_version
from arches.app.datatypes import datatypes

from arches_querysets.datatypes import *


class DataTypeFactory(datatypes.DataTypeFactory):
    def get_instance(self, datatype):
        instance = super().get_instance(datatype)

        if arches_version < (8, 0) and not hasattr(instance, "get_interchange_value"):
            instance.get_interchange_value = lambda value, **kwargs: value

        return instance

    @staticmethod
    def get_model_field(instance):
        if model_field := getattr(instance, "model_field", None):
            return model_field
        match instance:
            case datatypes.NumberDataType():
                return django.db.models.FloatField(null=True)
            case datatypes.DateDataType():
                return django.db.models.DateField(null=True)
            case datatypes.BooleanDataType():
                return django.db.models.BooleanField(null=True)
            case datatypes.NonLocalizedStringDataType():
                return django.db.models.CharField(null=True)
            case _:
                return django.db.models.JSONField(null=True)
