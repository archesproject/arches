from django.db.models.expressions import Func


class JsonbArrayElements(Func):
    arity = 1
    contains_subquery = True  # TODO(Django 5.2) change -> set_returning = True
    function = "JSONB_ARRAY_ELEMENTS"
