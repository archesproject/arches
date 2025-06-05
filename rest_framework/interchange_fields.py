from rest_framework import fields


class InterchangeValueMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        try:
            value["interchange_value"]
        except (TypeError, KeyError):
            return super().to_representation(value)
        return value

    def to_internal_value(self, data):
        try:
            interchange_value = data["interchange_value"]
        except:
            interchange_value = data
        return super().to_internal_value(interchange_value)


class BooleanField(InterchangeValueMixin, fields.BooleanField): ...


class FloatField(InterchangeValueMixin, fields.FloatField): ...


class CharField(InterchangeValueMixin, fields.CharField): ...


class UUIDField(InterchangeValueMixin, fields.UUIDField): ...


class DateField(InterchangeValueMixin, fields.DateField): ...


class JSONField(InterchangeValueMixin, fields.JSONField): ...
