from arches.app.datatypes import datatypes


class StringDataType(datatypes.StringDataType):
    def get_interchange_value(self, value, **kwargs):
        if not value or not isinstance(value, dict):
            return None
        return value
