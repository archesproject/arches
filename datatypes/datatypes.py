import django.db.models

from arches.app.datatypes import datatypes

from arches_querysets.datatypes import *


class DataTypeFactory(datatypes.DataTypeFactory):
    def get_instance(self, datatype):
        """Ensure every datatype has our additional methods."""
        instance = super().get_instance(datatype)

        if not hasattr(instance, "get_details"):
            instance.get_details = lambda value, *args, **kwargs: None
        if not hasattr(instance, "get_display_value_context_in_bulk"):
            instance.get_display_value_context_in_bulk = lambda *args, **kwargs: None
        if not hasattr(instance, "set_display_value_context_in_bulk"):
            instance.set_display_value_context_in_bulk = lambda *args, **kwargs: None

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
