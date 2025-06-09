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
        except (TypeError, KeyError):
            interchange_value = data
        return super().to_internal_value(interchange_value)


class BooleanField(InterchangeValueMixin, fields.BooleanField): ...


class FloatField(InterchangeValueMixin, fields.FloatField): ...


class CharField(InterchangeValueMixin, fields.CharField): ...


class UUIDField(InterchangeValueMixin, fields.UUIDField): ...


class DateField(InterchangeValueMixin, fields.DateField):
    def to_internal_value(self, data):
        """
        DRF's DateField doesn't handle None despite a few
        close-but-not-cigar-enough bug reports like:
        https://github.com/encode/django-rest-framework/issues/4835
        """
        try:
            interchange_value = data["interchange_value"]
        except (TypeError, KeyError):
            interchange_value = data
        if interchange_value is None:
            return None
        return super().to_internal_value(interchange_value)


class JSONField(InterchangeValueMixin, fields.JSONField): ...
