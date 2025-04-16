from arches.app.search.elasticsearch_dsl_builder import Bool, Ids
from arches.app.search.components.base import BaseSearchFilter
from arches.app.utils.betterJSONSerializer import JSONDeserializer

details = {
    "searchcomponentid": "f1856bfb-c3c4-4d67-8f23-0aa3eef3a160",
    "name": "ResourceIds Filter",
    "icon": "",
    "modulename": "ids.py",
    "classname": "ResourceIdsFilter",
    "type": "ids-filter-type",
    "componentpath": "",
    "componentname": "ids",
    "config": {},
}


class ResourceIdsFilter(BaseSearchFilter):

    def append_dsl(self, search_query_object, **kwargs):
        ids = kwargs.get("querystring", None)
        try:
            ids = JSONDeserializer().deserialize(ids)
        except:
            pass
        if isinstance(ids, list) and len(ids):
            ids_query = Bool()
            ids_query.must(Ids(ids=ids))
            search_query_object["query"].add_query(ids_query)
