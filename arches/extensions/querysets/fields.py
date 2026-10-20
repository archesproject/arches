"""Wrapping the Django fields allows registering datatype-specific lookups."""

from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField


class ResourceInstanceField(JSONField):
    pass


class ResourceInstanceListField(JSONField):
    pass


class ConceptListField(JSONField):
    pass


class DomainListField(JSONField):
    pass


class LocalizedStringField(JSONField):
    pass


### Cardinality N
class CardinalityNResourceInstanceField(ArrayField):
    pass


class CardinalityNResourceInstanceListField(ArrayField):
    pass


class CardinalityNConceptListField(ArrayField):
    pass


class CardinalityNLocalizedStringField(ArrayField):
    pass


class CardinalityNTextField(ArrayField):
    pass


class CardinalityNUUIDField(ArrayField):
    pass


class CardinalityNJSONField(ArrayField):
    pass
