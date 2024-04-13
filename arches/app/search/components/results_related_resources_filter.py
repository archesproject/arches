from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Query, Ids
from arches.app.search.components.base import BaseSearchFilter
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.models.models import Node, ResourceXResource
from arches.app.utils.permission_backend import get_resource_types_by_perm
from django.db.models import Q
import json


details = {
    "searchcomponentid": "166c011c-503b-499d-bc20-bedbe027f30e",
    "name": "Results Related Resources Filter",
    "icon": "",
    "modulename": "results_related_resources_filter.py",
    "classname": "ResultsRelatedResourcesFilter",
    "type": "inline-filter",
    "componentpath": "views/components/search/results-related-resources-filter",
    "componentname": "results-related-resources-filter",
    "sortorder": 6,
    "enabled": True,
}


def get_permitted_graphids(permitted_nodegroups):
    permitted_graphids = set()
    for node in Node.objects.filter(nodegroup__in=permitted_nodegroups):
        permitted_graphids.add(str(node.graph_id))
    return permitted_graphids


class ResultsRelatedResourcesFilter(BaseSearchFilter):

    def post_search_hook(self, search_results_object, results, permitted_nodegroups):
        select_related_resources_graphids = self.request.GET.get("results-related-resources-filter", None)
        if select_related_resources_graphids:
            try:
                select_related_resources_graphids = json.loads(select_related_resources_graphids)
                select_related_resources_graphids = [g['graphid'] for g in select_related_resources_graphids]
            except TypeError:
                return
        else:
            return

        all_ids = [hit["_id"] for hit in results["hits"]["hits"]]
        if not len(all_ids):
            return
        from_query = Q(resourceinstanceidfrom_id__in=all_ids, resourceinstanceto_graphid_id__in=select_related_resources_graphids)
        to_query = Q(resourceinstanceidto_id__in=all_ids, resourceinstancefrom_graphid_id__in=select_related_resources_graphids)
        final_query = (from_query | to_query)

        related_resources = []
        related_resources_query = ResourceXResource.objects.filter(final_query)
        related_resources.extend([str(rid) for rid in related_resources_query.values_list('resourceinstanceidto_id', flat=True)])
        related_resources.extend([str(rid) for rid in related_resources_query.values_list('resourceinstanceidfrom_id', flat=True)])

        se = SearchEngineFactory().create()
        new_search_results_object = {"query": Query(se)}
        new_dsl = new_search_results_object.pop("query", None)
        new_dsl.add_query(Ids(ids=related_resources))
        new_dsl.include("graph_id")
        new_dsl.include("root_ontology_class")
        new_dsl.include("resourceinstanceid")
        new_dsl.include("points")
        new_dsl.include("permissions.users_without_read_perm")
        new_dsl.include("permissions.users_without_edit_perm")
        new_dsl.include("permissions.users_without_delete_perm")
        new_dsl.include("permissions.users_with_no_access")
        new_dsl.include("geometries")
        new_dsl.include("displayname")
        new_dsl.include("displaydescription")
        new_dsl.include("map_popup")
        new_dsl.include("provisional_resource")
        new_results = new_dsl.search(index=RESOURCES_INDEX, limit=10000, scroll="1m")
        new_scroll_id = new_results["_scroll_id"]
        scroll_size = new_results["hits"]["total"]["value"]

        while scroll_size > 0:
            page = new_dsl.se.es.scroll(scroll_id=new_scroll_id, scroll="3m")
            scroll_size = len(page["hits"]["hits"])
            new_results["hits"]["hits"] += page["hits"]["hits"]
        
        for hit in new_results["hits"]["hits"]:
            hit["related"] = True
        
        results["hits"]["hits"] += new_results["hits"]["hits"]
        results["hits"]["total"]["value"] += new_results["hits"]["total"]["value"]

    def view_data(self):
        return {"resources": get_resource_types_by_perm(self.request.user, "read_nodegroup")}
