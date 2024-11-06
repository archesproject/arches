from django.db import models


class UUID4(models.Func):
    function = "uuid_generate_v4"
    arity = 0
    output_field = models.UUIDField()
