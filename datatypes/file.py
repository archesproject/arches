from django.utils.translation import get_language

from arches.app.datatypes import datatypes


class FileListDataType(datatypes.FileListDataType):
    localized_metadata_keys = {"altText", "attribution", "description", "title"}

    def transform_value_for_tile(self, value, *, languages, **kwargs):
        if not value:
            return value

        language = get_language()
        stringified_list = ",".join([file_info.get("name") for file_info in value])
        final_value = self.transform_value_for_tile(
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

    def merge_tile_value(self, tile, node_id_str, transformed) -> None:
        """
        Merge a node value with the existing node values. Useful to
        accept incoming data without overwriting all data on the target.
        """
        data = self.get_tile_data(tile)
        if not (existing_tile_value := data.get(node_id_str)):
            tile.data[node_id_str] = transformed
            return
        for file_info in transformed:
            for key, val in file_info.items():
                if key not in self.localized_metadata_keys:
                    continue
                for existing_file_info in existing_tile_value:
                    if existing_file_info.get("file_id") == file_info.get("file_id"):
                        file_info[key] = existing_file_info[key] | val
                    break
        tile.data[node_id_str] = transformed
