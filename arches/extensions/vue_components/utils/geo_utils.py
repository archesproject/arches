import json
import uuid

from django.contrib.gis.geos import GEOSGeometry

from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.geo_utils import GeoUtils as ArchesGeoUtils

TILE_EXTENT_ROUNDING_TOLERANCE_METERS = 0.001


class GeoUtils(ArchesGeoUtils):
    def buffer_feature_collection(self, feature_collection):
        unit_factors = {
            "meters": 1,
            "kilometers": 1000,
            "feet": 0.3048,
            "miles": 1609.344,
            "yards": 0.9144,
        }

        buffered_features = []

        for feature in feature_collection["features"]:
            geom = GEOSGeometry(json.dumps(feature["geometry"]))

            distance_meters = (
                feature["properties"]["buffer_distance"]
                * unit_factors[feature["properties"]["buffer_units"]]
            )

            geom.transform(settings.ANALYSIS_COORDINATE_SYSTEM_SRID)
            buffered_geom = geom.buffer(distance_meters)
            buffered_geom.transform(4326)

            buffered_features.append(
                {
                    "type": "Feature",
                    "id": str(uuid.uuid4()),
                    "properties": feature.get("properties", {}),
                    "geometry": json.loads(buffered_geom.geojson),
                }
            )

        return {"type": "FeatureCollection", "features": buffered_features}

    def get_resource_ids_within_extent(self, nodeid, extent_geojson):
        extent = GEOSGeometry(extent_geojson)
        extent.srid = models.GeoJSONGeometry._meta.get_field("geom").srid

        resource_ids = (
            models.GeoJSONGeometry.objects.filter(
                node_id=nodeid,
                geom__dwithin=(extent, TILE_EXTENT_ROUNDING_TOLERANCE_METERS),
            )
            .order_by("resourceinstance_id")
            .values_list("resourceinstance_id", flat=True)
            .distinct()
        )
        return [str(resource_id) for resource_id in resource_ids]
