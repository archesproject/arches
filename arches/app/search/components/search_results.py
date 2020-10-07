from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.search.elasticsearch_dsl_builder import Bool, Terms, NestedAgg, FiltersAgg, GeoHashGridAgg, GeoBoundsAgg
from arches.app.search.components.base import BaseSearchFilter
from arches.app.utils.permission_backend import user_is_resource_reviewer

details = {
    "searchcomponentid": "",
    "name": "Search Results",
    "icon": "",
    "modulename": "search_results.py",
    "classname": "SearchResultsFilter",
    "type": "results-list",
    "componentpath": "views/components/search/search-results",
    "componentname": "search-results",
    "sortorder": "0",
    "enabled": True,
}


class SearchResultsFilter(BaseSearchFilter):
    def append_dsl(self, search_results_object, permitted_nodegroups, include_provisional):
        nested_agg = NestedAgg(path="points", name="geo_aggs")
        nested_agg_filter = FiltersAgg(name="inner")
        geo_agg_filter = Bool()

        if include_provisional is True:
            geo_agg_filter.filter(Terms(field="points.provisional", terms=["false", "true"]))

        else:
            if include_provisional is False:
                geo_agg_filter.filter(Terms(field="points.provisional", terms=["false"]))

            elif include_provisional == "only provisional":
                geo_agg_filter.filter(Terms(field="points.provisional", terms=["true"]))

        geo_agg_filter.filter(Terms(field="points.nodegroup_id", terms=permitted_nodegroups))
        nested_agg_filter.add_filter(geo_agg_filter)
        nested_agg_filter.add_aggregation(GeoHashGridAgg(field="points.point", name="grid", precision=settings.HEX_BIN_PRECISION))
        nested_agg_filter.add_aggregation(GeoBoundsAgg(field="points.point", name="bounds"))
        nested_agg.add_aggregation(nested_agg_filter)
        search_results_object["query"].add_aggregation(nested_agg)

    def post_search_hook(self, search_results_object, results, permitted_nodegroups):
        user_is_reviewer = user_is_resource_reviewer(self.request.user)

        # only reuturn points and geometries a user is allowed to view
        geojson_nodes = get_nodegroups_by_datatype_and_perm(self.request, "geojson-feature-collection", "read_nodegroup")

        for result in results["hits"]["hits"]:
            result["_source"]["points"] = select_geoms_for_results(result["_source"]["points"], geojson_nodes, user_is_reviewer)
            result["_source"]["geometries"] = select_geoms_for_results(result["_source"]["geometries"], geojson_nodes, user_is_reviewer)
            try:
                permitted_tiles = []
                for tile in result["_source"]["tiles"]:
                    if tile["nodegroup_id"] in permitted_nodegroups:
                        permitted_tiles.append(tile)
                result["_source"]["tiles"] = permitted_tiles
            except KeyError:
                pass


def get_nodegroups_by_datatype_and_perm(request, datatype, permission):
    nodes = []
    for node in models.Node.objects.filter(datatype=datatype):
        if request.user.has_perm(permission, node.nodegroup):
            nodes.append(str(node.nodegroup_id))
    return nodes


def select_geoms_for_results(features, geojson_nodes, user_is_reviewer):
    res = []
    for feature in features:
        if "provisional" in feature:
            if feature["provisional"] is False or (user_is_reviewer is True and feature["provisional"] is True):
                if feature["nodegroup_id"] in geojson_nodes:
                    res.append(feature)
        else:
            if feature["nodegroup_id"] in geojson_nodes:
                res.append(feature)

    return res
