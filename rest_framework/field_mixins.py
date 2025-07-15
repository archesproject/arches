class NodeValueMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        try:
            value["node_value"]
        except (TypeError, KeyError):
            return super().to_representation(value)
        return value

    def to_internal_value(self, data):
        try:
            node_value = data["node_value"]
        except (TypeError, KeyError):
            node_value = data
        # DRF's DateField doesn't handle None despite a few
        # close-but-no-cigar bug reports like:
        # https://github.com/encode/django-rest-framework/issues/4835
        if node_value is None:
            return None
        return super().to_internal_value(node_value)
