from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from django.core.exceptions import ValidationError

wkt_point_widget = models.Widget.objects.get(name='wkt-point-widget')

details = {
    'datatype': 'wkt-point',
    'iconclass': 'fa fa-file-code-o',
    'modulename': 'datatypes.py',
    'classname': 'WKTPointDataType',
    'defaultwidget': wkt_point_widget,
    'defaultconfig': None,
    'configcomponent': None,
    'configname': None,
    'isgeometric': False
    }

class WKTPointDataType(BaseDataType):
    def validate(self, value, source=None):
        """
        Confirm your datatype meets validation criteria

        """
        errors = []
        try:
            value.upper()
        except:
            errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}'.format(self.datatype_model.datatype, value, source, 'this is not a string')})
        return errors

    def append_to_document(self, document, nodevalue):
        """
        Appends a value to a given elastic search document property

        """
        document['strings'].append(nodevalue)

    def transform_export_values(self, value):
        """
        Transform a value for export

        """
        return value.encode('utf8')
