import json

from rest_framework.parsers import MultiPartParser, DataAndFiles
from rest_framework.exceptions import ParseError


class MultiPartJSONParser(MultiPartParser):
    """
    Parses multipart/form-data, extracts the 'json' part,
    decodes it into a native dict, and returns that as request.data.
    Uploaded files remain in request.FILES.
    """

    def parse(self, stream, media_type=None, parser_context=None):
        parsed = super().parse(stream, media_type, parser_context)

        data_fields = parsed.data
        file_fields = parsed.files

        raw_json = data_fields.get("json") or file_fields.get("json").read()
        if raw_json is None:
            raise ParseError(detail="Missing 'json' part in multipart payload")

        try:
            decoded = json.loads(raw_json)
        except ValueError as err:
            raise ParseError(detail=f"Invalid JSON in 'json' part: {err}")

        if not isinstance(decoded, dict):
            raise ParseError(detail="'json' part did not decode to a dict")

        return DataAndFiles(decoded, file_fields)
