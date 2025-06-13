from arches.app.datatypes import url


class URLDataType(url.URLDataType):
    def to_json(self, tile, node):
        try:
            result = super().to_json(tile, node)
        except TypeError:
            result = {"url_label": ""}
        return {"@display_value": result["url_label"]}
