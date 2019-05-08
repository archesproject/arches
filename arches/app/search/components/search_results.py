from arches.app.models.system_settings import settings
from arches.app.search.elasticsearch_dsl_builder import Bool, Terms, NestedAgg, FiltersAgg, GeoHashGridAgg, GeoBoundsAgg
from arches.app.search.components.base import BaseSearchFilter

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
    "enabled": True
}


class SearchResultsFilter(BaseSearchFilter):

    def append_dsl(self, query_dsl, permitted_nodegroups, include_provisional):
        export = self.request.GET.get('export', None)
        mobile_download = self.request.GET.get('mobiledownload', None)
        page = 1 if self.request.GET.get('page') == '' else int(self.request.GET.get('page', 1))

        if export is not None:
            limit = settings.SEARCH_EXPORT_ITEMS_PER_PAGE
        elif mobile_download is not None:
            limit = self.request.GET['resourcecount']
        else:
            limit = settings.SEARCH_ITEMS_PER_PAGE
        limit = int(self.request.GET.get('limit', limit))
        query_dsl.start = limit*int(page-1)
        query_dsl.limit = limit


        nested_agg = NestedAgg(path='points', name='geo_aggs')
        nested_agg_filter = FiltersAgg(name='inner')
        geo_agg_filter = Bool()

        if include_provisional is True:
            geo_agg_filter.filter(Terms(field='points.provisional', terms=['false', 'true']))

        else:
            if include_provisional is False:
                geo_agg_filter.filter(Terms(field='points.provisional', terms=['false']))

            elif include_provisional is 'only provisional':
                geo_agg_filter.filter(Terms(field='points.provisional', terms=['true']))

        geo_agg_filter.filter(Terms(field='points.nodegroup_id', terms=permitted_nodegroups))
        nested_agg_filter.add_filter(geo_agg_filter)
        nested_agg_filter.add_aggregation(GeoHashGridAgg(field='points.point', name='grid', precision=settings.HEX_BIN_PRECISION))
        nested_agg_filter.add_aggregation(GeoBoundsAgg(field='points.point', name='bounds'))
        nested_agg.add_aggregation(nested_agg_filter)
        query_dsl.add_aggregation(nested_agg)
