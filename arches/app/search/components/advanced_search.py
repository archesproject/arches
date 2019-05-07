from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Bool, Nested
from arches.app.search.components.base import BaseSearchFilter

details = {
    "searchcomponentid": "",
    "name": "Advanced",
    "icon": "fa fa-check-circle-o",
    "modulename": "advanced_search.py",
    "classname": "AdvancedSearch",
    "type": "filter",
    "componentpath": "views/components/search/advanced-search",
    "componentname": "advanced-search",
    "config": {},
    "sortorder": "0",
    "enabled": True
}


class AdvancedSearch(BaseSearchFilter):

    def append_dsl(self, query_dsl, permitted_nodegroups, include_provisional):
        querysting_params = self.request.GET.get(details['componentname'], '')
        advanced_filters = JSONDeserializer().deserialize(querysting_params)
        datatype_factory = DataTypeFactory()
        search_query = Bool()
        advanced_query = Bool()
        grouped_query = Bool()
        grouped_queries = [grouped_query]
        for index, advanced_filter in enumerate(advanced_filters):
            tile_query = Bool()
            for key, val in advanced_filter.iteritems():
                if key != 'op':
                    node = models.Node.objects.get(pk=key)
                    if self.request.user.has_perm('read_nodegroup', node.nodegroup):
                        datatype = datatype_factory.get_instance(node.datatype)
                        datatype.append_search_filters(val, node, tile_query, self.request)
            nested_query = Nested(path='tiles', query=tile_query)
            if advanced_filter['op'] == 'or' and index != 0:
                grouped_query = Bool()
                grouped_queries.append(grouped_query)
            grouped_query.must(nested_query)
        for grouped_query in grouped_queries:
            advanced_query.should(grouped_query)
        search_query.must(advanced_query)

    def view_data(self):
        ret = {}
        resource_graphs = models.GraphModel.objects.exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).exclude(isresource=False).exclude(isactive=False)
        searchable_datatypes = [d.pk for d in models.DDataType.objects.filter(issearchable=True)]
        searchable_nodes = models.Node.objects.filter(graph__isresource=True, graph__isactive=True, datatype__in=searchable_datatypes, issearchable=True)
        resource_cards = models.CardModel.objects.filter(graph__isresource=True, graph__isactive=True)
        datatypes = models.DDataType.objects.all()

        ret['graphs'] = resource_graphs
        ret['datatypes'] = datatypes
        ret['nodes'] = searchable_nodes
        ret['cards'] = resource_cards

        return ret
