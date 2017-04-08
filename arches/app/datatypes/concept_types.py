import uuid
from arches.app.models import models
from arches.app.datatypes.base import BaseDataType
from arches.app.models.concept import get_preflabel_from_valueid
from django.core.exceptions import ObjectDoesNotExist


class BaseConceptDataType(BaseDataType):
    def __init__(self, model=None):
        super(BaseConceptDataType, self).__init__(model=model)
        self.value_lookup = {}

    def get_value(self, valueid):
        try:
            return self.value_lookup[valueid]
        except:
            self.value_lookup[valueid] = models.Value.objects.get(pk=valueid)
            return self.value_lookup[valueid]

    def get_concept_export_value(self, valueid, *args, **kwargs):
        concept_export_value_type = None
        if 'concept_export_value_type' in kwargs:
            concept_export_value_type = kwargs.get('concept_export_value_type')
        ret = ''
        if concept_export_value_type != None:
            if concept_export_value_type == "label" or concept_export_value_type == "both":
                if concept_export_value_type == "label":
                    ret = self.get_value(valueid)
                elif concept_export_value_type == "both":
                    ret = valueid + '|' + self.get_value(valueid)
        return ret

    def append_to_document(self, document, nodevalue):
        try:
            assert isinstance(nodevalue, (list, tuple)) #assert nodevalue is an array
        except AssertionError:
            nodevalue = [nodevalue]
        for valueid in nodevalue:
            value = self.get_value(valueid)
            document['domains'].append({'label': value.value, 'conceptid': value.concept_id, 'valueid': valueid})


class ConceptDataType(BaseConceptDataType):

    def validate(self, value, source=''):
        errors = []
        try:
            models.Value.objects.get(pk=value)
        except ObjectDoesNotExist:
            message = "Not a valid domain value"
            errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}'.format(self.datatype_model.datatype, value, source, message)})
        return errors

    def transform_import_values(self, value):
        return value.strip()

    def transform_export_values(self, value, *args, **kwargs):
        if 'concept_export_value_type' in kwargs:
            concept_export_value_type = kwargs.get('concept_export_value_type')
        return self.get_concept_export_value(value, concept_export_value_type)

    def get_pref_label(self, nodevalue, lang='en-US'):
        return get_preflabel_from_valueid(nodevalue, lang)['value']

    def get_display_value(self, tile, node):
        value = None
        return self.get_value(uuid.UUID(tile.data[str(node.nodeid)]))


class ConceptListDataType(BaseConceptDataType):
    def transform_import_values(self, value):
        return [v.strip() for v in value.split(',')]

    def transform_export_values(self, value, concept_export_value_type):
        new_values = []
        for val in value:
            new_val = self.get_concept_export_value(val, concept_export_value_type)
            new_values.append(new_val)
        return ','.join(new_values)
