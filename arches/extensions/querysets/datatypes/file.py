from django.utils.translation import get_language

from arches import __version__ as _arches_version_str
from packaging.version import Version

arches_version = Version(_arches_version_str)
from arches.app.datatypes import datatypes
from arches.app.models import models
from arches.app.models.models import File


class FileListDataType(datatypes.FileListDataType):
    localized_metadata_keys = {"altText", "attribution", "description", "title"}

    def post_tile_save(self, tile, nodeid, request):
        # Can't rely on core's db requery for the old value here, it's
        # already been overwritten by the time bulk save calls this.
        previously_saved_data = getattr(tile, "_existing_data", None) or {}
        previous_file_ids = {
            file_info["file_id"]
            for file_info in previously_saved_data.get(nodeid) or []
            if file_info.get("file_id")
        }
        current_file_ids = {
            file_info["file_id"]
            for file_info in tile.data.get(nodeid) or []
            if file_info.get("file_id")
        }
        removed_file_ids = previous_file_ids - current_file_ids
        if removed_file_ids:
            File.objects.filter(fileid__in=removed_file_ids).delete()

        super().post_tile_save(tile, nodeid, request)

    def get_display_value(self, tile, node, **kwargs):
        data = self.get_tile_data(tile)
        files = data[str(node.nodeid)]
        file_urls = ""
        if files is not None:
            file_urls = " | ".join(
                [file["url"] or "" for file in files if "url" in file]
            )

        return file_urls

    def transform_value_for_tile(self, value, *, languages=None, **kwargs):
        if not value:
            return value
        if not languages:  # pragma: no cover
            languages = models.Language.objects.all()
        language = get_language()
        original_value = value
        reset_fabricated_ids = "bulk_import" not in kwargs
        # Entries to undo the phantom file/file_id fabricated below for
        # genuinely new entries (no file_id in the original payload), so
        # post_tile_save can link the real upload.
        fabricated_file_dicts = []
        file_ids_to_delete = []

        # arches == 9.0.0 - remove the stringifieid_list in favor of the 8.1.0 logic
        if arches_version < Version("8.1"):
            if isinstance(value, str):
                stringified_list = value
            elif isinstance(value, list) and all(
                isinstance(file_info, dict) for file_info in value
            ):
                stringified_list = ",".join(
                    [file_info.get("name") for file_info in value]
                )
            else:
                raise TypeError(value)
            value = super().transform_value_for_tile(
                stringified_list, languages=languages, **kwargs
            )
            new_value = []
            for file in value:
                if isinstance(original_value, str):
                    new_value.append(file)
                    continue

                matching_file_info = next(
                    (
                        file_dict
                        for file_dict in original_value
                        if file_dict.get("name") == file.get("name")
                    ),
                    None,
                )
                if not matching_file_info:
                    continue

                if matching_file_info.get("file_id"):
                    merged_file_info = {**file, **matching_file_info}
                    phantom_file_id = file.get("file_id")

                    if (
                        reset_fabricated_ids
                        and phantom_file_id
                        and phantom_file_id != matching_file_info["file_id"]
                    ):
                        file_ids_to_delete.append(phantom_file_id)
                else:
                    merged_file_info = {**matching_file_info, **file}

                    if reset_fabricated_ids:
                        fabricated_file_dicts.append(merged_file_info)
                new_value.append(merged_file_info)
        else:
            new_value = super().transform_value_for_tile(
                value, languages=languages, **kwargs
            )

            # If lengths ever diverge we can't align by position; skip the
            # reset rather than risk deleting the wrong File row.
            if (
                reset_fabricated_ids
                and isinstance(original_value, list)
                and len(original_value) == len(new_value)
            ):
                fabricated_file_dicts = [
                    file_dict
                    for original_entry, file_dict in zip(original_value, new_value)
                    if not (
                        isinstance(original_entry, dict)
                        and original_entry.get("file_id")
                    )
                ]

        file_ids_to_delete.extend(
            file_dict["file_id"] for file_dict in fabricated_file_dicts
        )
        if file_ids_to_delete:
            File.objects.filter(fileid__in=file_ids_to_delete).delete()

        for file_dict in fabricated_file_dicts:
            file_dict["file_id"] = None
            file_dict["url"] = None

        for file_info in new_value:
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

        return new_value
