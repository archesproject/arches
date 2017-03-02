from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from django.core.exceptions import ValidationError

text_widget = models.Widget.objects.get(name='text-widget')

details = {
    'datatype': 'sample',
    'iconclass': 'fa fa-file-code-o',
    'modulename': 'datatypes.py',
    'classname': 'SampleDataType',
    'defaultwidget': text_widget,
    'defaultconfig': None,
    'configcomponent': None,
    'configname': None,
    'isgeometric': False
    }

class SampleDataType(BaseDataType):
    def validate(self, value, source=None):
        """
        Confirm your datatype meets validation criteria

        """
        errors = []
        try:
            value.upper()
        except:
            errors.append({'source': source, 'value': value, 'message': 'this is not a string', 'datatype': self.datatype_model.datatype})
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
