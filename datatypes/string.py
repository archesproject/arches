from arches.app.datatypes import datatypes


class StringDataType(datatypes.StringDataType):
    def merge_tile_value(self, tile, node_id_str, transformed) -> None:
        """
        Merge a node value with the existing node values. Useful to
        accept incoming data without overwriting all data on the target.
        """
        data = self.get_tile_data(tile)
        tile.data[node_id_str] = (data.get(node_id_str) or {}) | transformed

    def get_interchange_value(self, value, **kwargs):
        if not value or not isinstance(value, dict):
            return None
        return value
