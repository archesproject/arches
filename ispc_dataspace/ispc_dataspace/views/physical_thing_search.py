from arches.app.views.search import get_provisional_type
from django.views.generic import View
from arches.app.search.search_engine_factory import SearchEngineFactory
from django.http import HttpResponseNotFound
from django.utils.translation import ugettext as _
from django.shortcuts import render
from datetime import datetime
from arches.app.search.components.base import SearchFilterFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Terms, MaxAgg, Aggregation, Nested
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.utils.response import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.views.base import BaseManagerView
from arches.app.models import models
from arches.app.models.system_settings import settings


class PhysicalThingSearchView(View):
    def get(self, request):
        return self.search_results(request)

    def search_results(self, request):
        has_filters = True if len(list(request.GET.items())) > 1 is not None else False
        request.GET = request.GET.copy()

        se = SearchEngineFactory().create()
        search_results_object = {"query": Query(se)}

        include_provisional = get_provisional_type(request)
        permitted_nodegroups = self.get_permitted_nodegroups(request.user)

        # get a list of resourceIds of type Person et al that meet
        # the search query then use those ids to search for Person instances related to Physical Thing instances
        request.GET["resource-type-filter"] = '[{"graphid":"f71f7b9c-b25b-11e9-901e-a4d18cec433a","name":"Person","inverted":false}]'

        search_filter_factory = SearchFilterFactory(request)
        try:
            for filter_type, querystring in list(request.GET.items()) + [("search-results", "")]:
                search_filter = search_filter_factory.get_filter(filter_type)
                if search_filter:
                    search_filter.append_dsl(search_results_object, permitted_nodegroups, include_provisional)
        except Exception as err:
            return JSONResponse(err.message, status=500)

        dsl = search_results_object.pop("query", None)
        dsl.exclude("*")
        results = dsl.search(index="resources", limit=1000)
        resourceIds = [hit["_id"] for hit in results["hits"]["hits"]]

        search_results_object = {"query": Query(se)}

        request.GET[
            "resource-type-filter"
        ] = '[{"graphid":"9519cb4f-b25b-11e9-8c7b-a4d18cec433a","name":"Physical Thing","inverted":false}]'
        search_filter_factory = SearchFilterFactory(request)
        try:
            for filter_type, querystring in list(request.GET.items()) + [("search-results", "")]:
                search_filter = search_filter_factory.get_filter(filter_type)
                if search_filter:
                    search_filter.append_dsl(search_results_object, permitted_nodegroups, include_provisional)
        except Exception as err:
            return JSONResponse(err.message, status=500)

        # only search for realted instance references when a filter is applied (aside from the paging filter)
        if has_filters:
            # the resource id query can only return resources of type Physical Thing; this is to handle for the scenario
            # where a Person (or other relatable model added to filter) is related to something other than a Person
            resource_id_query = Bool()
            resource_id_query.must(Nested(path="ids", query=Terms(field="ids.id", terms=resourceIds)))
            resource_id_query.must(Terms(field="graph_id", terms="9519cb4f-b25b-11e9-8c7b-a4d18cec433a"))

            # we need to wrap the existing query (search_results_object['query']) in a Bool query along with
            # the resource id query above
            outer_query = Bool()
            outer_query.should(resource_id_query)

            dsl = search_results_object.pop("query", None)
            outer_query.should(dsl.dsl.pop("query", None))
            dsl.dsl["query"] = {}
            search_results_object["query"] = dsl

            search_results_object["query"].add_query(outer_query)

        dsl = search_results_object.pop("query", None)
        dsl.include("graph_id")
        dsl.include("root_ontology_class")
        dsl.include("resourceinstanceid")
        dsl.include("points")
        dsl.include("geometries")
        dsl.include("displayname")
        dsl.include("displaydescription")
        dsl.include("map_popup")
        dsl.include("provisional_resource")
        dsl.include("domains")
        # if request.GET.get('tiles', None) is not None:
        #     dsl.include('tiles')

        dsl.include("tiles")
        results = dsl.search(index="resources")
        # print JSONSerializer().serialize(dsl.dsl)

        if results is not None:
            # allow filters to modify the results
            for filter_type, querystring in list(request.GET.items()) + [("search-results", "")]:
                search_filter = search_filter_factory.get_filter(filter_type)
                if search_filter:
                    search_filter.post_search_hook(search_results_object, results, permitted_nodegroups)

            ret = {}
            ret["results"] = results

            for key, value in list(search_results_object.items()):
                ret[key] = value

            ret["reviewer"] = request.user.groups.filter(name="Resource Reviewer").exists()
            ret["timestamp"] = datetime.now()
            ret["total_results"] = dsl.count(index="resources")

            return JSONResponse(ret)
        else:
            return HttpResponseNotFound(_("There was an error retrieving the search results"))

    def get_permitted_nodegroups(self, user):
        return [str(nodegroup.pk) for nodegroup in get_nodegroups_by_perm(user, "models.read_nodegroup")]
