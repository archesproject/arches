from arches.app.datatypes import url


class URLDataType(url.URLDataType):
    def pre_structure_tile_data(self, tile, nodeid, **kwargs):
        if tile.data[nodeid] is None:
            tile.data[nodeid] = {"url": "", "url_label": ""}
            return
        return super().pre_structure_tile_data(tile, nodeid, **kwargs)
