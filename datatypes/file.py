from django.utils.translation import get_language

from arches.app.datatypes import datatypes
from arches.app.models import models


class FileListDataType(datatypes.FileListDataType):
    localized_metadata_keys = {"altText", "attribution", "description", "title"}

    def transform_value_for_tile(self, value, *, languages=None, **kwargs):
        if not value:
            return value
        if not languages:  # pragma: no cover
            languages = models.Language.objects.all()

        language = get_language()
        stringified_list = ",".join([file_info.get("name") for file_info in value])
        final_value = super().transform_value_for_tile(
            stringified_list, languages=languages, **kwargs
        )

        for file_info in final_value:
            for key, val in file_info.items():
                if key not in self.localized_metadata_keys:
                    continue
                original_val = val
                if not isinstance(original_val, dict):
                    file_info[key] = {}
                for lang in languages:
                    if lang.code not in file_info[key]:
                        file_info[key][lang.code] = {
                            "value": original_val if lang.code == language else "",
                            "direction": lang.default_direction,
                        }

        return final_value
