from django.utils.translation import gettext as _

from arches.app.datatypes import datatypes
from arches.app.utils.i18n import rank_label


class StringDataType(datatypes.StringDataType):
    def merge_tile_value(self, tile, node_id_str, transformed) -> None:
        """
        Merge a node value with the existing node values. Useful to
        accept incoming data without overwriting all data on the target.
        """
        data = self.get_tile_data(tile)
        tile.data[node_id_str] = (data.get(node_id_str) or {}) | transformed

    def to_json(self, tile, node):
        data = self.get_tile_data(tile)
        if data.get(str(node.nodeid)):
            return self.compile_json(tile, node)
        return {"@display_value": _("(Empty)")}

    def resolve(self, value: dict):
        """Resolve localized values to a single one."""
        lang_val_pairs = [(lang, obj["value"]) for lang, obj in value.items()]
        if not lang_val_pairs:
            return
        ranked = sorted(
            lang_val_pairs,
            key=lambda pair: rank_label(source_lang=pair[0]),
            reverse=True,
        )
        return ranked[0][1]

    def get_interchange_value(self, value, **kwargs):
        if not value or not isinstance(value, dict):
            return None
        return value
