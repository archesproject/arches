from arches.app.datatypes import url


class URLDataType(url.URLDataType):
    def to_json(self, tile, node):
        try:
            return super().to_json(tile, node)
        except TypeError:
            return {"@display_value": ""}
