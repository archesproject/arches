import uuid
from arches.app.models.models import Node
from arches.app.models.system_settings import settings
from arches.app.search.elasticsearch_dsl_builder import (
    Bool,
    Terms,
    NestedAgg,
    FiltersAgg,
    GeoHashGridAgg,
    GeoBoundsAgg,
    Nested,
)
from arches.app.search.components.base import BaseSearchFilter
from arches.app.search.components.resource_type_filter import get_permitted_graphids
from arches.app.utils.permission_backend import user_is_resource_reviewer
from arches.app.utils import permission_backend
from django.utils.translation import get_language, gettext as _

details = {
    "searchcomponentid": "",
    "name": "Search Results",
    "icon": "",
    "modulename": "search_results.py",
    "classname": "SearchResultsFilter",
    "type": "search-results-type",
    "componentpath": "views/components/search/search-results",
    "componentname": "search-results",
    "config": {},
}


class SearchResultsFilter(BaseSearchFilter):
    def append_dsl(self, search_query_object, **kwargs):
        permitted_nodegroups = kwargs.get("permitted_nodegroups")
        include_provisional = kwargs.get("include_provisional")
        nested_agg = NestedAgg(path="points", name="geo_aggs")
        nested_agg_filter = FiltersAgg(name="inner")
        geo_agg_filter = Bool()

        try:
            search_query_object["query"].dsl["query"]["bool"]["filter"][0]["terms"][
                "graph_id"
            ]  # check if resource_type filter is already applied
        except (KeyError, IndexError):
            resource_model_filter = Bool()
            permitted_graphids = get_permitted_graphids(permitted_nodegroups)
            terms = Terms(field="graph_id", terms=list(permitted_graphids))
            resource_model_filter.filter(terms)
            search_query_object["query"].add_query(resource_model_filter)

        if include_provisional is True:
            geo_agg_filter.filter(
                Terms(field="points.provisional", terms=["false", "true"])
            )

        else:
            if include_provisional is False:
                geo_agg_filter.filter(
                    Terms(field="points.provisional", terms=["false"])
                )

            elif include_provisional == "only provisional":
                geo_agg_filter.filter(Terms(field="points.provisional", terms=["true"]))

        geo_agg_filter.filter(
            Terms(field="points.nodegroup_id", terms=permitted_nodegroups)
        )
        nested_agg_filter.add_filter(geo_agg_filter)
        nested_agg_filter.add_aggregation(
            GeoHashGridAgg(
                field="points.point", name="grid", precision=settings.HEX_BIN_PRECISION
            )
        )
        nested_agg_filter.add_aggregation(
            GeoBoundsAgg(field="points.point", name="bounds")
        )
        nested_agg.add_aggregation(nested_agg_filter)

        if self.user and self.user.id:
            search_query = Bool()
            subsearch_query = Bool()
            # TODO: call to permissions framework with subsearch_query
            subsearch_query.should(
                Nested(
                    path="permissions",
                    query=Terms(
                        field="permissions.principal_user", terms=[int(self.user.id)]
                    ),
                )
            )
            search_query.must(subsearch_query)
            search_query_object["query"].add_query(search_query)

        search_query_object["query"].add_aggregation(nested_agg)

    def post_search_hook(self, search_query_object, response_object, **kwargs):
        permitted_nodegroups = kwargs.get("permitted_nodegroups")
        user_is_reviewer = user_is_resource_reviewer(self.request.user)

        descriptor_types = ("displaydescription", "displayname")
        active_and_default_language_codes = (get_language(), settings.LANGUAGE_CODE)
        groups = [group.id for group in self.request.user.groups.all()]
        response_object["groups"] = groups

        # only reuturn points and geometries a user is allowed to view
        geojson_nodes = get_nodegroups_by_datatype_and_perm(
            self.request, "geojson-feature-collection", "read_nodegroup"
        )

        for result in response_object["results"]["hits"]["hits"]:
            result.update(
                permission_backend.get_search_ui_permissions(
                    self.request.user, result, groups
                )
            )
            result["_source"]["points"] = select_geoms_for_results(
                result["_source"]["points"], geojson_nodes, user_is_reviewer
            )
            result["_source"]["geometries"] = select_geoms_for_results(
                result["_source"]["geometries"], geojson_nodes, user_is_reviewer
            )
            try:
                permitted_tiles = []
                for tile in result["_source"]["tiles"]:
                    if uuid.UUID(tile["nodegroup_id"]) in permitted_nodegroups:
                        permitted_tiles.append(tile)
                result["_source"]["tiles"] = permitted_tiles
            except KeyError:
                pass

            for descriptor_type in descriptor_types:
                descriptor = get_localized_descriptor(
                    result, descriptor_type, active_and_default_language_codes
                )
                if descriptor:
                    result["_source"][descriptor_type] = descriptor["value"]
                    if descriptor_type == "displayname":
                        result["_source"]["displayname_language"] = descriptor[
                            "language"
                        ]
                else:
                    result["_source"][descriptor_type] = _("Undefined")


def get_nodegroups_by_datatype_and_perm(request, datatype, permission):
    nodes = []
    for node in Node.objects.filter(datatype=datatype).select_related("nodegroup"):
        if request.user.has_perm(permission, node.nodegroup):
            nodes.append(str(node.nodegroup_id))
    return nodes


def select_geoms_for_results(features, geojson_nodes, user_is_reviewer):
    res = []
    for feature in features:
        if "provisional" in feature:
            if feature["provisional"] is False or (
                user_is_reviewer is True and feature["provisional"] is True
            ):
                if feature["nodegroup_id"] in geojson_nodes:
                    res.append(feature)
        else:
            if feature["nodegroup_id"] in geojson_nodes:
                res.append(feature)

    return res


def get_localized_descriptor(resource, descriptor_type, language_codes):
    descriptor = resource["_source"][descriptor_type]
    result = descriptor[0] if len(descriptor) > 0 else None
    for language_code in language_codes:
        for entry in descriptor:
            if entry["language"] == language_code and entry["value"] != "":
                return entry
    return result
