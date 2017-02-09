from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from arches.app.views.concept import get_preflabel_from_valueid

class BaseConceptDataType(BaseDataType):
    def get_concept_export_value(self, value, concept_export_value_type):
        if concept_export_value_type != None:
            if concept_export_value_type == "label" or concept_export_value_type == "both":
                if concept_export_value_type == "label":
                    value = Value.objects.get(valueid=value).value
                elif concept_export_value_type == "both":
                    value = value + '|' + Value.objects.get(valueid=value).value
        return value

    def append_to_document(self, document, nodevalue):
        try:
            assert isinstance(nodevalue, (list, tuple)) #assert nodevalue is an array
        except AssertionError:
            nodevalue = [nodevalue]
        for concept_valueid in nodevalue:
            value = models.Value.objects.get(pk=concept_valueid)
            document['domains'].append({'label': value.value, 'conceptid': value.concept_id, 'valueid': concept_valueid})

class ConceptDataType(BaseConceptDataType):
    def transform_import_values(self, value):
        return value.strip()

    def transform_export_values(self, value):
        return self.get_concept_export_value(value, concept_export_value_type)

    def get_pref_label(self, nodevalue, lang='en-US'):
        return get_preflabel_from_valueid(nodevalue, lang)['value']

    def get_concept_values(self, tile, node):
        concept_values = models.Value.objects.filter(valueid=uuid.UUID(tile.data[str(node.nodeid)]))
        return concept_values

class ConceptListDataType(BaseConceptDataType):
    def transform_import_values(self, value):
        return [v.strip() for v in value.split(',')]

    def transform_export_values(self, value):
        new_values = []
        for val in value:
            new_val = self.get_concept_export_value(val, concept_export_value_type)
            new_values.append(new_val)
        return ','.join(new_values)
