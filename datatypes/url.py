from arches.app.datatypes import url


class URLDataType(url.URLDataType):
    def to_json(self, tile, node):
        return {"@display_value": super().to_json(tile, node)["url_label"]}
