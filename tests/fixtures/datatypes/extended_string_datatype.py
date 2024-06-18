from arches.app.datatypes.datatypes import StringDataType
from arches.app.models import models

string_widget = models.Widget.objects.get(name="text-widget")

details = {
    "datatype": "extended-string-datatype",
    "iconclass": "fa fa-file-code-o",
    "modulename": "extended_string_datatype.py",
    "classname": "ExtendedStringDataType",
    "defaultwidget": string_widget,
    "defaultconfig": {"pgDatatype": "jsonb"},
    "configcomponent": "views/components/datatypes/string",
    "configname": "string-datatype-config",
    "isgeometric": False,
    "issearchable": True,
}


class ExtendedStringDataType(StringDataType):
    def validate(
        self,
        value,
        row_number=None,
        source=None,
        node=None,
        nodeid=None,
        strict=False,
        **kwargs,
    ):
        errors = super(ExtendedStringDataType, self).validate(
            value, row_number, source, node, nodeid, strict, **kwargs
        )
        return errors

    def clean(self, tile, nodeid):
        super(ExtendedStringDataType, self).clean(tile, nodeid)
