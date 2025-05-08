"""Wrapping the Django fields allows registering lookups per datatype."""

from django.db.models import DateTimeField, TextField
from django.db.models.fields.json import JSONField
from django.contrib.postgres.fields import ArrayField


class CardinalityNField(ArrayField):
    """Takes a base_field argument."""

    pass


class Cardinality1DateTimeField(DateTimeField):
    pass


class Cardinality1JSONField(JSONField):
    pass


class ResourceInstanceField(JSONField):
    pass


class ResourceInstanceListField(JSONField):
    pass


class Cardinality1ResourceInstanceField(ResourceInstanceField):
    pass


class Cardinality1ResourceInstanceListField(ResourceInstanceListField):
    pass


class Cardinality1TextField(TextField):
    pass
