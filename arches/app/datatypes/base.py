import json

class BaseDataType(object):

    def __init__(self, model=None):
        self.datatype_model = model

    def validate(self, value, source=None):
        return []

    def append_to_document(self, document, nodevalue):
        """
        Assigns a given node value to the corresponding key in a document in
        in preparation to index the document
        """
        pass

    def transform_import_values(self, value):
        """
        Transforms values from probably string/wkt representation to specified
        datatype in arches
        """
        return value

    def transform_export_values(self, value):
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

    def get_map_layer(self, node=None):
        """
        Gets the array of map layers to add to the map for a given node
        should be a dictionary including (as in map_layers table):
        nodeid, name, layerdefinitions, isoverlay, icon
        """
        return None

    def get_map_source(self, node=None, preview=False):
        """
        Gets the map source definition to add to the map for a given node
        should be a dictionary including (as in map_sources table):
        name, source (json)
        """
        if node is None:
            return None
        source_config = {
            "type": "vector",
            "tiles": ["/tileserver/%s/{z}/{x}/{y}.pbf" % node.nodeid]
        }
        if preview:
            source_config = {
                "type": "geojson",
                "data": {
                    "type": "FeatureCollection",
                    "features": [{
                        "type": "Feature",
                        "properties": {
                            "total": 1
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                  [-121.353637, 40.584978],
                                  [-121.284551, 40.584758],
                                  [-121.275349, 40.541646],
                                  [-121.246768, 40.541017],
                                  [-121.251343, 40.423383],
                                  [-121.326870, 40.423768],
                                  [-121.360619, 40.434790],
                                  [-121.363694, 40.409124],
                                  [-121.439713, 40.409197],
                                  [-121.439711, 40.423791],
                                  [-121.572133, 40.423548],
                                  [-121.577415, 40.550766],
                                  [-121.539486, 40.558107],
                                  [-121.520284, 40.572459],
                                  [-121.487219, 40.550822],
                                  [-121.446951, 40.563190],
                                  [-121.370644, 40.563267],
                                  [-121.353637, 40.584978]
                                ]
                            ]
                        }
                    }, {
                        "type": "Feature",
                        "properties": {
                            "total": 1
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-121.415061, 40.506229]
                        }
                    }, {
                        "type": "Feature",
                        "properties": {
                            "total": 1
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-121.505184, 40.488084]
                        }
                    }, {
                        "type": "Feature",
                        "properties": {
                            "total": 10
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-121.354465, 40.488737]
                        }
                    }]
                }
            }
        return {
            "nodeid": node.nodeid,
            "name": "resources-%s" % node.nodeid,
            "source": json.dumps(source_config)
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
        return None

    def get_search_term(self, nodevalue):
        """
        Returns a nodevalue if it qualifies as a search term
        """
        return None

    def manage_files(self, previously_saved_tile, current_tile, request, node):
        """
        Updates files
        """
        pass
