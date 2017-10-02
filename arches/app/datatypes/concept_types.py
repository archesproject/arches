import uuid
from arches.app.models import models
from arches.app.models import concept
from arches.app.datatypes.base import BaseDataType
from arches.app.models.concept import get_preflabel_from_valueid
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Range, Term, Nested, Exists
from arches.app.utils.date_utils import SortableDate
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

    def get_concept_export_value(self, valueid, concept_export_value_type=None):
        ret = ''
        if concept_export_value_type == None or concept_export_value_type == '' or concept_export_value_type == 'label':
            ret = self.get_value(valueid).value
        elif concept_export_value_type == 'both':
            ret = valueid + '|' + self.get_value(valueid).value
        elif concept_export_value_type == 'id':
            ret = valueid
        return ret

    def get_concept_dates(self, concept):
        result = None
        date_range = {}
        values = models.Value.objects.filter(concept=concept)
        for value in values:
            if value.valuetype.valuetype in ('min_year' 'max_year'):
                date_range[value.valuetype.valuetype] = value.value
        if 'min_year' in date_range and 'max_year' in date_range:
            result = date_range
        return result

    def append_to_document(self, document, nodevalue, nodeid, tile):
        try:
            assert isinstance(nodevalue, (list, tuple)) #assert nodevalue is an array
        except AssertionError:
            nodevalue = [nodevalue]
        for valueid in nodevalue:
            value = self.get_value(valueid)
            date_range = self.get_concept_dates(value.concept)
            if date_range is not None:
                min_date = SortableDate(date_range['min_year']).as_float()
                max_date = SortableDate(date_range['max_year']).as_float()
                if {'gte': min_date, 'lte': max_date} not in document['date_ranges']:
                    document['date_ranges'].append({'date_range': {'gte': min_date, 'lte': max_date}, 'nodegroup_id': tile.nodegroup_id})
            document['domains'].append({'label': value.value, 'conceptid': value.concept_id, 'valueid': valueid, 'nodegroup_id': tile.nodegroup_id})
            document['strings'].append({'string': value.value, 'nodegroup_id': tile.nodegroup_id})


class ConceptDataType(BaseConceptDataType):

    def validate(self, value, source=''):
        errors = []
        try:
            models.Value.objects.get(pk=value)
        except ObjectDoesNotExist:
            message = "Not a valid domain value"
            errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}. {4}'.format(self.datatype_model.datatype, value, source, message, 'This data was not imported.')})
        return errors

    def transform_import_values(self, value, nodeid):
        ret = value.strip()
        return ret

    def transform_export_values(self, value, *args, **kwargs):
        if 'concept_export_value_type' in kwargs:
            concept_export_value_type = kwargs.get('concept_export_value_type')
        return self.get_concept_export_value(value, concept_export_value_type)

    def get_pref_label(self, nodevalue, lang='en-US'):
        return get_preflabel_from_valueid(nodevalue, lang)['value']

    def get_display_value(self, tile, node):
        if tile.data[str(node.nodeid)] is None or tile.data[str(node.nodeid)].strip() == '':
            return ''
        else:
            return self.get_value(uuid.UUID(tile.data[str(node.nodeid)])).value

    def append_search_filters(self, value, node, query, request):
        try:
            if value['val'] != '':
                match_query = Match(field='tiles.data.%s' % (str(node.pk)), type="phrase", query=value['val'], fuzziness=0)
                if '!' in value['op']:
                    query.must_not(match_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(match_query)

        except KeyError, e:
            pass


class ConceptListDataType(BaseConceptDataType):
    def validate(self, value, source=''):
        errors = []
        for v in value:
            val = v.strip()
            try:
                models.Value.objects.get(pk=val)
            except ObjectDoesNotExist:
                message = "Not a valid domain value"
                errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}. {4}'.format(self.datatype_model.datatype, val, source, message, 'This data was not imported.')})
        return errors

    def transform_import_values(self, value, nodeid):
        ret = []
        concept = ConceptDataType()
        for val in [v.strip() for v in value.split(',')]:
            ret.append(concept.transform_import_values(val, nodeid))
        return ret

    def transform_export_values(self, value, *args, **kwargs):
        new_values = []
        for val in value:
            new_val = self.get_concept_export_value(val, kwargs['concept_export_value_type'])
            new_values.append(new_val)
        return ','.join(new_values)

    def get_display_value(self, tile, node):
        new_values = []
        for val in tile.data[str(node.nodeid)]:
            new_val = self.get_value(uuid.UUID(val))
            new_values.append(new_val.value)
        return ','.join(new_values)

    def append_search_filters(self, value, node, query, request):
        try:
            if value['val'] != '':
                match_query = Match(field='tiles.data.%s' % (str(node.pk)), type="phrase", query=value['val'], fuzziness=0)
                if '!' in value['op']:
                    query.must_not(match_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(match_query)

        except KeyError, e:
            pass
