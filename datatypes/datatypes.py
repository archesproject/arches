import django.db.models

from arches.app.datatypes.datatypes import (
    BooleanDataType,
    DateDataType,
    DomainListDataType,
    NonLocalizedStringDataType,
    NumberDataType,
)

from arches_querysets.datatypes import *
from arches_querysets.fields import (
    ConceptListField,
    DomainListField,
    LocalizedStringField,
    ResourceInstanceField,
    ResourceInstanceListField,
)


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
            case NumberDataType():
                return django.db.models.FloatField(null=True)
            case DateDataType():
                return django.db.models.DateTimeField(null=True)
            case BooleanDataType():
                return django.db.models.BooleanField(null=True)
            case NonLocalizedStringDataType():
                return django.db.models.TextField(null=True)
            case StringDataType():
                return LocalizedStringField(null=True)
            case ResourceInstanceListDataType():
                # must precede ResourceInstanceDataType
                return ResourceInstanceListField(null=True)
            case ResourceInstanceDataType():
                return ResourceInstanceField(null=True)
            case ConceptListDataType():
                return ConceptListField(null=True)
            case ConceptDataType(), NodeValueDataType():
                return django.db.models.UUIDField(null=True)
            case URLDataType():
                return django.db.models.JSONField(null=True)
            case DomainListDataType():
                return DomainListField(null=True)
            case FileListDataType():
                return django.db.models.JSONField(default=list, null=True)
            case _:
                return django.db.models.TextField(null=True)
