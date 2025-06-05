import copy

from django.utils.translation import get_language

from arches.app.datatypes import datatypes
from arches.app.utils.i18n import rank_label


class FileListDataType(datatypes.FileListDataType):
    def transform_value_for_tile(self, value, *, languages, **kwargs):
        if not value:
            return value

        stringified_list = ",".join([file_info.get("name") for file_info in value])
        final_value = self.transform_value_for_tile(
            stringified_list, languages=languages, **kwargs
        )

        for file_info in final_value:
            for key, val in file_info.items():
                if key not in {"altText", "attribution", "description", "title"}:
                    continue
                original_val = val
                if not isinstance(original_val, dict):
                    file_info[key] = {}
                for lang in languages:
                    if lang.code not in file_info[key]:
                        file_info[key][lang.code] = {
                            "value": (
                                original_val if lang.code == get_language() else ""
                            ),
                            "direction": lang.default_direction,
                        }

        return final_value

    def merge_tile_value(self, tile, node_id_str, transformed) -> None:
        if not (existing_tile_value := tile.data.get(node_id_str)):
            tile.data[node_id_str] = transformed
            return
        for file_info in transformed:
            for key, val in file_info.items():
                if key not in {"altText", "attribution", "description", "title"}:
                    continue
                for existing_file_info in existing_tile_value:
                    if existing_file_info.get("file_id") == file_info.get("file_id"):
                        file_info[key] = existing_file_info[key] | val
                    break
        tile.data[node_id_str] = transformed

    def get_display_value(self, tile, node, **kwargs):
        """Resolve localized string metadata to a single language value."""
        value = super().get_display_value(tile, node, **kwargs)
        if not value:
            return value
        final_value = copy.deepcopy(value)
        for file_info in final_value:
            for key, val in file_info.items():
                if not isinstance(val, dict):
                    continue
                lang_val_pairs = [(lang, lang_val) for lang, lang_val in val.items()]
                if not lang_val_pairs:
                    continue
                ranked = sorted(
                    lang_val_pairs,
                    key=lambda pair: rank_label(source_lang=pair[0]),
                    reverse=True,
                )
                file_info[key] = ranked[0][1].get("value")
        return final_value
