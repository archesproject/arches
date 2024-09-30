import json
import uuid
from arcgis2geojson import arcgis2geojson
from django.contrib.gis.geos import (
    GEOSGeometry,
    GeometryCollection,
    MultiPoint,
    MultiLineString,
    MultiPolygon,
)
from django.db import connection
from arches.app.models.system_settings import settings
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

    def get_resource_instances_within_feature_collection(self, feature_collection):
        """
        Takes a FeatureCollection object and returns a dictionary of resource instances
        that intersect the geometries of it, grouped by graph.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                WITH combined_geom AS (
                    SELECT ST_Union(
                        ST_Transform(
                            ST_SetSRID(ST_GeomFromGeoJSON(feature->>'geometry'), 4326), 
                            3857
                        )
                    ) AS geom
                    FROM jsonb_array_elements(%s::jsonb->'features') AS feature
                )
                SELECT resource_instances.graphid, 
                    array_agg(geojson_geometries.resourceinstanceid) AS resourceinstanceids
                FROM geojson_geometries 
                JOIN resource_instances 
                ON geojson_geometries.resourceinstanceid = resource_instances.resourceinstanceid
                WHERE ST_Intersects(
                        geojson_geometries.geom, 
                        (SELECT geom FROM combined_geom)
                    )
                AND resource_instances.graphid != %s
                GROUP BY resource_instances.graphid;
                """,
                [
                    json.dumps(feature_collection),
                    settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID,
                ],
            )

            results = cursor.fetchall()

        return dict(results)

    def buffer_feature_collection(self, feature_collection, buffer_distance):
        """
        Takes a FeatureCollection object and a value for the buffer distance in meters,
        and returns a FeatureCollection of the original features with the buffer distance added.

        """

        buffered_features = []

        for feature in feature_collection["features"]:
            geom = GEOSGeometry(json.dumps(feature["geometry"]))

            geom.transform(settings.ANALYSIS_COORDINATE_SYSTEM_SRID)
            buffered_geom = geom.buffer(buffer_distance)
            buffered_geom.transform(4326)

            buffered_feature = {
                "type": "Feature",
                "id": str(uuid.uuid4()),
                "properties": feature.get("properties", {}),
                "geometry": json.loads(buffered_geom.geojson),
            }
            buffered_features.append(buffered_feature)

        return {
            "type": "FeatureCollection",
            "features": buffered_features,
        }

    def get_intersection_and_difference_of_feature_collections(
        self, feature_collection_1, feature_collection_2
    ):
        def _build_feature_collection(geometries):
            features = []

            if geometries is None or geometries.empty:
                return {"type": "FeatureCollection", "features": []}

            if geometries.geom_type in [
                "GeometryCollection",
                "MultiPolygon",
                "MultiLineString",
                "MultiPoint",
            ]:
                for geometry in geometries:
                    if not geometry.empty:
                        features.append(
                            {
                                "type": "Feature",
                                "id": str(uuid.uuid4()),
                                "properties": {},
                                "geometry": json.loads(geometry.geojson),
                            }
                        )
            else:
                features.append(
                    {
                        "type": "Feature",
                        "id": str(uuid.uuid4()),
                        "properties": {},
                        "geometry": json.loads(geometries.geojson),
                    }
                )

            return {"type": "FeatureCollection", "features": features}

        feature_collection_1_geometries = [
            GEOSGeometry(json.dumps(feature["geometry"]))
            for feature in feature_collection_1["features"]
        ]
        feature_collection_1_geometries_union = GeometryCollection(
            *feature_collection_1_geometries
        ).unary_union

        feature_collection_2_geometries = [
            GEOSGeometry(json.dumps(feature["geometry"]))
            for feature in feature_collection_2["features"]
        ]
        feature_collection_2_geometries_union = GeometryCollection(
            *feature_collection_2_geometries
        ).unary_union

        return {
            "difference_derived_from_first_collection": _build_feature_collection(
                feature_collection_1_geometries_union.difference(
                    feature_collection_2_geometries_union
                )
            ),
            "difference_derived_from_second_collection": _build_feature_collection(
                feature_collection_2_geometries_union.difference(
                    feature_collection_1_geometries_union
                )
            ),
            "intersection_derived_from_both_collections": _build_feature_collection(
                feature_collection_1_geometries_union.intersection(
                    feature_collection_2_geometries_union
                )
            ),
        }
