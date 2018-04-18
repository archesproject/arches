import json
from django.contrib.gis.geos import GEOSGeometry, GeometryCollection
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


class GeoUtils(object):

    def create_geom_collection_from_geojson(self, geojson):
        geoms = []
        for feature in geojson['features']:
            geoms.append(GEOSGeometry(JSONSerializer().serialize(feature['geometry'])))
        return GeometryCollection(geoms)

    def get_bounds_from_geojson(self, geojson):
        """
        Takes a geojson object with polygon(s) and returns the coordinates of
        the extent of the polygons.

        """
        geom_collection = self.create_geom_collection_from_geojson(geojson)
        bounds = geom_collection.extent
        return bounds

    def get_centroid(self, geojson):
        """
        Takes a geojson object with polygon(s) and returns its center point as geojson.

        """
        geom_collection = self.create_geom_collection_from_geojson(geojson)
        centroid = geom_collection.centroid.geojson
        return JSONDeserializer().deserialize(centroid)

    def convert_multipart_to_singlepart(self, geom, format="geojson"):
        result = None
        if geom != None:
            multipart = geom
            fc = {"type": "FeatureCollection", "features": []}
            for coords in multipart['coordinates']:
                geom = { "type": "Feature",
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": coords
                            },
                            "properties": {}
                        };
                fc['features'].append(geom)
            result = fc
        return result
