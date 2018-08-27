import json
from django.core.urlresolvers import reverse
from arches.app.models import models

class BaseDataType(object):

    def __init__(self, model=None):
        self.datatype_model = model

    def validate(self, value, row_number=None, source=None):
        return []

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        """
        Assigns a given node value to the corresponding key in a document in
        in preparation to index the document
        """
        pass

    def after_update_all(self):
        """
        Refreshes mv_geojson_geoms materialized view after save.
        """
        pass

    def transform_import_values(self, value, nodeid):
        """
        Transforms values from probably string/wkt representation to specified
        datatype in arches
        """
        return value

    def transform_export_values(self, value, *args, **kwargs):
        """
        Transforms values from probably string/wkt representation to specified
        datatype in arches
        """
        return value

    def get_bounds(self, tile, node):
        """
        Gets the bounds of a geometry if the datatype is spatial
        """
        return None

    def get_layer_config(self, node=None):
        """
        Gets the layer config to generate a map layer (use if spatial)
        """
        return None

    def should_cache(self, node=None):
        """
        Tells the system if the tileserver should cache for a given node
        """
        return False

    def should_manage_cache(self, node=None):
        """
        Tells the system if the tileserver should clear cache on edits for a
        given node
        """
        return False

    def get_map_layer(self, node=None):
        """
        Gets the array of map layers to add to the map for a given node
        should be a dictionary including (as in map_layers table):
        nodeid, name, layerdefinitions, isoverlay, icon
        """
        return None

    def clean(self, tile, nodeid):
        """
        Converts '' values to null when saving a tile.
        """
        if tile.data[nodeid] == '':
            tile.data[nodeid] = None

    def get_map_source(self, node=None, preview=False):
        """
        Gets the map source definition to add to the map for a given node
        should be a dictionary including (as in map_sources table):
        name, source (json)
        """
        tileserver_url = reverse('tileserver')
        if node is None:
            return None
        source_config = {
            "type": "vector",
            "tiles": ["%s/%s/{z}/{x}/{y}.pbf" % (tileserver_url, node.nodeid)]
        }
        count = None
        if preview == True:
            count = models.TileModel.objects.filter(data__has_key=str(node.nodeid)).count()
            if count == 0:
                source_config = {
                    "type": "geojson",
                    "data": {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "properties": {
                                    "total": 1
                                },
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [
                                        -122.4810791015625,
                                        37.93553306183642
                                    ]
                                }
                            },
                            {
                                "type": "Feature",
                                "properties": {
                                    "total": 100
                                },
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [
                                        -58.30078125,
                                        -18.075412438417395
                                    ]
                                }
                            },
                            {
                                "type": "Feature",
                                "properties": {
                                    "total": 1
                                },
                                "geometry": {
                                    "type": "LineString",
                                    "coordinates": [
                                        [
                                            -179.82421875,
                                            44.213709909702054
                                        ],
                                        [
                                            -154.16015625,
                                            32.69486597787505
                                        ],
                                        [
                                            -171.5625,
                                            18.812717856407776
                                        ],
                                        [
                                            -145.72265625,
                                            2.986927393334876
                                        ],
                                        [
                                            -158.37890625,
                                            -30.145127183376115
                                        ]
                                    ]
                                }
                            },
                            {
                                "type": "Feature",
                                "properties": {
                                    "total": 1
                                },
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [
                                            [
                                                -50.9765625,
                                                22.59372606392931
                                            ],
                                            [
                                                -23.37890625,
                                                22.59372606392931
                                            ],
                                            [
                                                -23.37890625,
                                                42.94033923363181
                                            ],
                                            [
                                                -50.9765625,
                                                42.94033923363181
                                            ],
                                            [
                                                -50.9765625,
                                                22.59372606392931
                                            ]
                                        ]
                                    ]
                                }
                            },
                            {
                                "type": "Feature",
                                "properties": {
                                    "total": 1
                                },
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [
                                            [
                                                -27.59765625,
                                                -14.434680215297268
                                            ],
                                            [
                                                -24.43359375,
                                                -32.10118973232094
                                            ],
                                            [
                                                0.87890625,
                                                -31.653381399663985
                                            ],
                                            [
                                                2.28515625,
                                                -12.554563528593656
                                            ],
                                            [
                                                -14.23828125,
                                                -0.3515602939922709
                                            ],
                                            [
                                                -27.59765625,
                                                -14.434680215297268
                                            ]
                                        ]
                                    ]
                                }
                            }
                        ]
                    }
                }
        return {
            "nodeid": node.nodeid,
            "name": "resources-%s" % node.nodeid,
            "source": json.dumps(source_config),
            "count": count
        }

    def get_pref_label(self, nodevalue):
        """
        Gets the prefLabel of a concept value
        """
        return None

    def get_display_value(self, tile, node):
        """
        Returns a list of concept values for a given node
        """
        return unicode(tile.data[str(node.nodeid)])

    def get_search_terms(self, nodevalue, nodeid=None):
        """
        Returns a nodevalue if it qualifies as a search term
        """
        return []

    def append_search_filters(self, value, node, query, request):
        """
        Allows for modification of an elasticsearch bool query for use in
        advanced search
        """
        pass

    def handle_request(self, current_tile, request, node):
        """
        Updates files
        """
        pass
