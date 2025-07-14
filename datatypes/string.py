import ast
import json
import re

from arches.app.datatypes import datatypes
from arches.app.models import models
from django.utils.translation import get_language


class StringDataType(datatypes.StringDataType):
    def transform_value_for_tile(self, value, *, languages=None, **kwargs):
        """
        Override to:
        1. avoid refetching languages already present in kwargs.
        2. get the direction from the database when falling back to get_language().
        """
        language = get_language()
        try:
            regex = re.compile(r"(.+)\|([A-Za-z-]+)$", flags=re.DOTALL | re.MULTILINE)
            match = regex.match(value)
            if match is not None:
                language = match.groups()[1]
                value = match.groups()[0]
        except Exception as e:
            pass

        try:
            parsed_value = json.loads(value)
        except Exception:
            try:
                parsed_value = ast.literal_eval(value)
            except Exception:
                parsed_value = value

        try:
            parsed_value.keys()
            return parsed_value
        except AttributeError:
            if languages:
                for language_object in languages:
                    if language_object.code == language:
                        break
                else:
                    language_object = None
            else:
                language_object = models.Language.objects.filter(code=language).first()
            if language_object is not None:
                return {
                    language: {
                        "value": value,
                        "direction": language_object.default_direction,
                    }
                }

            return {language: {"value": value, "direction": "ltr"}}
