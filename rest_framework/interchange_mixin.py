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
        # DRF's DateField doesn't handle None despite a few
        # close-but-no-cigar bug reports like:
        # https://github.com/encode/django-rest-framework/issues/4835
        if interchange_value is None:
            return None
        return super().to_internal_value(interchange_value)
