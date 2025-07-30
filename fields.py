"""Wrapping the Django fields allows registering lookups per datatype."""

from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField


class ResourceInstanceField(JSONField):
    pass


class ResourceInstanceListField(JSONField):
    pass


class LocalizedStringField(JSONField):
    pass


### Cardinality N
class CardinalityNResourceInstanceField(ArrayField):
    pass


class CardinalityNResourceInstanceListField(ArrayField):
    pass


class CardinalityNLocalizedStringField(ArrayField):
    pass


class CardinalityNTextField(ArrayField):
    pass
