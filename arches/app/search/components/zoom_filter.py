import logging
from django.contrib.gis.geos import GEOSGeometry
from django.db import connection
from django.utils.translation import ugettext as _
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Bool, Nested, Terms, GeoShape, Exists
from arches.app.search.components.base import BaseSearchFilter

logger = logging.getLogger(__name__)

details = {
    "searchcomponentid": "",
    "name": "Zoom Filter",
    "icon": "",
    "modulename": "zoom_filter.py",
    "classname": "ZoomFilter",
    "type": "filter",
    "componentpath": "views/components/search/zoom-filter",
    "componentname": "zoom-filter",
    "sortorder": "0",
    "enabled": False,
}


class ZoomFilter(BaseSearchFilter):
    def append_dsl(self, search_results_object, permitted_nodegroups, include_provisional):
        print("HELLOOOOOOOOOO")
        search_query = Bool()
        querysting_params = self.request.GET.get(details["componentname"], "")
        spatial_filter = JSONDeserializer().deserialize(querysting_params)
        if "features" in spatial_filter:
            if len(spatial_filter["features"]) > 0:
                feature_geom = spatial_filter["features"][0]["geometry"]
                feature_properties = {}
                if "properties" in spatial_filter["features"][0]:
                    feature_properties = spatial_filter["features"][0]["properties"]
                buffer = {"width": 0, "unit": "ft"}
                if "buffer" in feature_properties:
                    buffer = feature_properties["buffer"]
                search_buffer = _buffer(feature_geom, buffer["width"], buffer["unit"])
                feature_geom = JSONDeserializer().deserialize(search_buffer.geojson)
                geoshape = GeoShape(
                    field="geometries.geom.features.geometry", type=feature_geom["type"], coordinates=feature_geom["coordinates"]
                )

                spatial_query = Bool()
                spatial_query.filter(geoshape)

                # get the nodegroup_ids that the user has permission to search
                spatial_query.filter(Terms(field="geometries.nodegroup_id", terms=permitted_nodegroups))

                if include_provisional is False:
                    spatial_query.filter(Terms(field="geometries.provisional", terms=["false"]))

                elif include_provisional == "only provisional":
                    spatial_query.filter(Terms(field="geometries.provisional", terms=["true"]))

                search_query.filter(Bool(must_not=Exists(field="geometries.geom.features.geometry")))
                search_query.filter(Nested(path="geometries", query=spatial_query))
                # search_query.should(Bool(must_not=Exists(field="geometries.geom.features.geometry")))

        search_results_object["query"].add_query(search_query)

        if details["componentname"] not in search_results_object:
            search_results_object[details["componentname"]] = {}

        try:
            search_results_object[details["componentname"]]["search_buffer"] = feature_geom
        except NameError:
            logger.info(_("Feature geometry is not defined"))


def _buffer(geojson, width=0, unit="ft"):
    geojson = JSONSerializer().serialize(geojson)
    geom = GEOSGeometry(geojson, srid=4326)

    try:
        width = float(width)
    except Exception:
        width = 0

    if width > 0:
        if unit == "ft":
            width = width / 3.28084
        with connection.cursor() as cursor:
            # Transform geom to the analysis SRID, buffer it, and transform it back to wgs84
            cursor.execute(
                """SELECT ST_TRANSFORM(
                    ST_BUFFER(ST_TRANSFORM(ST_SETSRID(%s::geometry, 4326), %s), %s),
                4326)""",
                (geom.hex.decode("utf-8"), settings.ANALYSIS_COORDINATE_SYSTEM_SRID, width),
            )
            res = cursor.fetchone()
            geom = GEOSGeometry(res[0], srid=4326)
    return geom
