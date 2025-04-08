from django.contrib.postgres.fields import ArrayField
from django.db.models.fields.json import JSONField


class Cardinality1Field(JSONField):
    pass


class CardinalityNField(ArrayField):
    pass
