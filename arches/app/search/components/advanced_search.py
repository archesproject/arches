from arches.app.models.models import (
    Node,
    DDataType,
    GraphModel,
    CardModel,
    CardXNodeXWidget,
)
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
    "type": "advanced-search-type",
    "componentpath": "views/components/search/advanced-search",
    "componentname": "advanced-search",
    "config": {},
}


class AdvancedSearch(BaseSearchFilter):
    def append_dsl(self, search_query_object, **kwargs):
        querystring_params = kwargs.get("querystring", "[]")
        advanced_filters = JSONDeserializer().deserialize(querystring_params)
        datatype_factory = DataTypeFactory()
        search_query = Bool()
        advanced_query = Bool()
        grouped_query = Bool()
        grouped_queries = [grouped_query]
        for index, advanced_filter in enumerate(advanced_filters):
            tile_query = Bool()
            null_query = Bool()
            for key, val in advanced_filter.items():
                if key != "op":
                    node = Node.objects.get(pk=key)
                    if self.request.user.has_perm("read_nodegroup", node.nodegroup):
                        datatype = datatype_factory.get_instance(node.datatype)
                        try:
                            val["val"] = "" if val["val"] == None else val["val"]
                        except:
                            pass

                        if (
                            "op" in val
                            and (val["op"] == "null" or val["op"] == "not_null")
                        ) or (
                            "val" in val
                            and (val["val"] == "null" or val["val"] == "not_null")
                        ):
                            # don't use a nested query with the null/not null search
                            datatype.append_search_filters(
                                val, node, null_query, self.request
                            )
                        else:
                            datatype.append_search_filters(
                                val, node, tile_query, self.request
                            )
            nested_query = Nested(path="tiles", query=tile_query)
            if advanced_filter["op"] == "or" and index != 0:
                grouped_query = Bool()
                grouped_queries.append(grouped_query)
            grouped_query.must(nested_query)
            grouped_query.must(null_query)
        for grouped_query in grouped_queries:
            advanced_query.should(grouped_query)
        search_query.must(advanced_query)
        search_query_object["query"].add_query(search_query)

    def view_data(self):
        ret = {}
        resource_graphs = (
            GraphModel.objects.exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(isresource=False)
            .exclude(is_active=False)
            .exclude(source_identifier__isnull=False)
        )
        searchable_datatypes = [
            d.pk for d in DDataType.objects.filter(issearchable=True)
        ]
        searchable_nodes = Node.objects.filter(
            graph__isresource=True,
            graph__is_active=True,
            datatype__in=searchable_datatypes,
            issearchable=True,
        )

        resource_cards = CardModel.objects.filter(
            graph__isresource=True, graph__is_active=True
        ).select_related("nodegroup")
        cardwidgets = CardXNodeXWidget.objects.filter(node__in=searchable_nodes)
        datatypes = DDataType.objects.all()

        # only allow cards that the user has permission to read
        searchable_cards = []
        for card in resource_cards:
            if self.request.user.has_perm("read_nodegroup", card.nodegroup):
                searchable_cards.append(card)

        ret["graphs"] = resource_graphs
        ret["datatypes"] = datatypes
        ret["nodes"] = searchable_nodes
        ret["cards"] = searchable_cards
        ret["cardwidgets"] = cardwidgets

        return ret
