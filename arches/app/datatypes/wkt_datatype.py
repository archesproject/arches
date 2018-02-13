from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from arches.app.models.system_settings import settings

wkt_widget = models.Widget.objects.get(name='wkt-widget')

details = {
    'datatype': 'wkt-datatype',
    'iconclass': 'fa fa-house-o',
    'modulename': 'datatypes.py',
    'classname': 'WKTDataType',
    'defaultwidget': wkt_widget,
    'defaultconfig': None,
    'configcomponent': None,
    'configname': None,
    'isgeometric': False
    }

class WKTDataType(BaseDataType):

    def validate(self, value, source=None):
        errors = []
        try:
            value.upper()
        except:
            errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}. {4}'.format(self.datatype_model.datatype, value, source, 'this is not a string', 'This data was not imported.')})
        return errors

    def append_to_document(self, document, nodevalue, nodeid, tile):
        document['strings'].append({'string': nodevalue, 'nodegroup_id': tile.nodegroup_id})

    def transform_export_values(self, value, *args, **kwargs):
        if value != None:
            return value.encode('utf8')

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        if nodevalue is not None:
            if settings.WORDS_PER_SEARCH_TERM == None or (len(nodevalue.split(' ')) < settings.WORDS_PER_SEARCH_TERM):
                terms.append(nodevalue)
        return terms

    def append_search_filters(self, value, node, query, request):
        try:
            if value['val'] != '':
                match_type = 'phrase_prefix' if '~' in value['op'] else 'phrase'
                match_query = Match(field='tiles.data.%s' % (str(node.pk)), query=value['val'], type=match_type)
                if '!' in value['op']:
                    query.must_not(match_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(match_query)
        except KeyError, e:
            pass
