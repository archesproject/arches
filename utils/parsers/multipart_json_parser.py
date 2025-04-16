from rest_framework import parsers


class MultiPartJSONParser(parsers.MultiPartParser):
    """https://stackoverflow.com/a/63398121"""

    def parse(self, stream, *args, **kwargs):
        data = super().parse(stream, *args, **kwargs)

        # Any 'File' found having application/json as type will be moved to data
        mutable_data = data.data.copy()
        unmarshaled_blob_names = []
        json_parser = parsers.JSONParser()
        for name, blob in data.files.items():
            if blob.content_type == "application/json" and name not in data.data:
                mutable_data[name] = json_parser.parse(blob)
                unmarshaled_blob_names.append(name)
        for name in unmarshaled_blob_names:
            del data.files[name]
        data.data = mutable_data

        return data
