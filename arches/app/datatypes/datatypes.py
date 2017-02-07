import uuid
from arches.app.datatypes.base import BaseDataType
from arches.app.models import models

class StringDataType(BaseDataType):
    def append_to_document(self, document, nodevalue):
        document['strings'].append(nodevalue)

class NumberDataType(BaseDataType):
    def append_to_document(self, document, nodevalue):
        document['numbers'].append(nodevalue)

class DateDataType(BaseDataType):
    def append_to_document(self, document, nodevalue):
        document['dates'].append(nodevalue)

class GeojsonFeatureCollectionDataType(BaseDataType):
    def append_to_document(self, document, nodevalue):
        document['geometries'].append(nodevalue)

class ConceptDataType(BaseDataType):
    def append_to_document(self, document, nodevalue):
        nodevalue = [nodevalue]
        for concept_valueid in nodevalue:
            value = models.Value.objects.get(pk=concept_valueid)
            document['domains'].append({'label': value.value, 'conceptid': value.concept_id, 'valueid': concept_valueid})

class ConceptListDataType(BaseDataType):
    def append_to_document(self, document, nodevalue):
        for concept_valueid in nodevalue:
            value = models.Value.objects.get(pk=concept_valueid)
            document['domains'].append({'label': value.value, 'conceptid': value.concept_id, 'valueid': concept_valueid})
