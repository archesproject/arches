import json
import uuid
from arcgis2geojson import arcgis2geojson
from django.contrib.gis.geos import GEOSGeometry, GeometryCollection, WKTWriter
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


class GeoUtils(object):
    def set_precision(self, coordinates, precision):
        """
        returns the passed in coordinates with the specified precision

        """

        result = []
        try:
            return round(coordinates, int(precision))
        except TypeError:
            for coordinate in coordinates:
                result.append(self.set_precision(coordinate, precision))
        return result

    def create_geom_collection_from_geojson(self, geojson):
        geoms = []
        for feature in geojson["features"]:
            geoms.append(GEOSGeometry(JSONSerializer().serialize(feature["geometry"])))
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
        if geom is not None:
            multipart = geom
            fc = {"type": "FeatureCollection", "features": []}
            geom_type = multipart["type"].replace("Multi", "")
            for coords in multipart["coordinates"]:
                geom = {
                    "type": "Feature",
                    "geometry": {"type": geom_type, "coordinates": coords},
                    "properties": {},
                }
                fc["features"].append(geom)
            result = fc
        return result

    def arcgisjson_to_geojson(self, geom):
        """
        Takes a list of arcgisjson geometries and converts them to a GeoJSON feature collection. Example below:
        '{"x":-0.11515950499995142,"y":51.534958948000053,"spatialReference":{"wkid":4326,"latestWkid":4326}},
         {"x":-0.11337002699997356,"y":51.536050094000075,"spatialReference":{"wkid":4326,"latestWkid":4326}}'
        """
        payload = json.loads('{"geometries": [' + geom + "]}")
        features = []
        for geometry in payload["geometries"]:
            features.append(
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": arcgis2geojson(geometry),
                }
            )
        feature_collection = {"type": "FeatureCollection", "features": features}
        return feature_collection

    def convert_geos_geom_collection_to_feature_collection(self, geometry):
        arches_geojson = {}
        arches_geojson["type"] = "FeatureCollection"
        arches_geojson["features"] = []
        for geom in geometry:
            arches_json_geometry = {}
            arches_json_geometry["geometry"] = JSONDeserializer().deserialize(
                GEOSGeometry(geom, srid=4326).json
            )
            arches_json_geometry["type"] = "Feature"
            arches_json_geometry["id"] = str(uuid.uuid4())
            arches_json_geometry["properties"] = {}
            arches_geojson["features"].append(arches_json_geometry)
        return arches_geojson
