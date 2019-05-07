from django.contrib.gis.geos import GEOSGeometry
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Bool, Nested, Terms, GeoShape
from arches.app.search.components.base import BaseSearchFilter

details = {
    "searchcomponentid": "",
    "name": "Map Filter",
    "icon": "fa fa-map-marker",
    "modulename": "map_filter.py",
    "classname": "MapFilter",
    "type": "filter",
    "componentpath": "views/components/search/map-filter",
    "componentname": "map-filter",
    "sortorder": "0",
    "enabled": True
}


class MapFilter(BaseSearchFilter):

    def append_dsl(self, query_dsl, permitted_nodegroups, include_provisional):
        search_query = Bool()
        querysting_params = self.request.GET.get(details['componentname'], '')
        spatial_filter = JSONDeserializer().deserialize(querysting_params)
        if 'features' in spatial_filter:
            if len(spatial_filter['features']) > 0:
                feature_geom = spatial_filter['features'][0]['geometry']
                feature_properties = {}
                if 'properties' in spatial_filter['features'][0]:
                    feature_properties = spatial_filter['features'][0]['properties']
                buffer = {'width': 0, 'unit': 'ft'}
                if 'buffer' in feature_properties:
                    buffer = feature_properties['buffer']
                search_buffer = _buffer(feature_geom, buffer['width'], buffer['unit'])
                feature_geom = JSONDeserializer().deserialize(search_buffer.json)
                geoshape = GeoShape(field='geometries.geom.features.geometry', type=feature_geom['type'], coordinates=feature_geom['coordinates'])

                invert_spatial_search = False
                if 'inverted' in feature_properties:
                    invert_spatial_search = feature_properties['inverted']

                spatial_query = Bool()
                if invert_spatial_search is True:
                    spatial_query.must_not(geoshape)
                else:
                    spatial_query.filter(geoshape)

                # get the nodegroup_ids that the user has permission to search
                spatial_query.filter(Terms(field='geometries.nodegroup_id', terms=permitted_nodegroups))

                if include_provisional is False:
                    spatial_query.filter(Terms(field='geometries.provisional', terms=['false']))

                elif include_provisional == 'only provisional':
                    spatial_query.filter(Terms(field='geometries.provisional', terms=['true']))

                search_query.filter(Nested(path='geometries', query=spatial_query))

        query_dsl.add_query(search_query)

        return {'search_buffer': search_buffer.geojson}


def _buffer(geojson, width=0, unit='ft'):
    geojson = JSONSerializer().serialize(geojson)
    geom = GEOSGeometry(geojson, srid=4326)

    try:
        width = float(width)
    except:
        width = 0

    if width > 0:
        if unit == 'ft':
            width = width/3.28084

        geom.transform(settings.ANALYSIS_COORDINATE_SYSTEM_SRID)
        geom = geom.buffer(width)
        geom.transform(4326)

    return geom
