import decimal
import json
import os
import uuid
from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.search.elasticsearch_dsl_builder import Match
from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from arches.app.utils.geo_utils import GeoUtils
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import GeometryCollection
from django.contrib.gis.geos import Polygon
from django.db import connection
from django.utils.translation import gettext as _
from rdflib import URIRef, Literal, ConjunctiveGraph as Graph
from string import Template


class GeojsonFeatureCollectionDataType(BaseDataType):
    def __init__(self, model=None):
        super(GeojsonFeatureCollectionDataType, self).__init__(model=model)
        self.geo_utils = GeoUtils()

    def validate(
        self,
        value,
        row_number=None,
        source=None,
        node=None,
        nodeid=None,
        strict=False,
        **kwargs,
    ):
        errors = []

        def validate_geom_bbox(geom):
            try:
                bbox = Polygon(settings.DATA_VALIDATION_BBOX)

                if bbox.contains(geom) == False:
                    message = _(
                        "Geometry does not fall within the bounding box of the selected coordinate system. \
                         Adjust your coordinates or your settings.DATA_EXTENT_VALIDATION property."
                    )
                    title = _("Geometry Out Of Bounds")
                    errors.append(
                        {
                            "type": "ERROR",
                            "message": "datatype: {0} value: {1} {2} - {3}. {4}".format(
                                self.datatype_model.datatype,
                                value,
                                source,
                                message,
                                "This data was not imported.",
                            ),
                            "title": title,
                        }
                    )
            except Exception:
                message = _("Not a properly formatted geometry")
                title = _("Invalid Geometry Format")
                errors.append(
                    {
                        "type": "ERROR",
                        "message": "datatype: {0} value: {1} {2} - {3}. {4}.".format(
                            self.datatype_model.datatype,
                            value,
                            source,
                            message,
                            "This data was not imported.",
                        ),
                        "title": title,
                    }
                )

        if value is not None:
            for feature in value["features"]:
                try:
                    geom = GEOSGeometry(JSONSerializer().serialize(feature["geometry"]))
                    if geom.valid:
                        validate_geom_bbox(geom)
                    else:
                        raise Exception
                except Exception:
                    message = _("Unable to serialize some geometry features.")
                    title = _("Unable to Serialize Geometry")
                    error_message = self.create_error_message(
                        value, source, row_number, message, title
                    )
                    errors.append(error_message)
        return errors

    def to_json(self, tile, node):
        data = self.get_tile_data(tile)
        if data:
            return self.compile_json(tile, node, geojson=data.get(str(node.nodeid)))

    def clean(self, tile, nodeid):
        if tile.data[nodeid] is not None and "features" in tile.data[nodeid]:
            if len(tile.data[nodeid]["features"]) == 0:
                tile.data[nodeid] = None
        if tile.data[nodeid] == "":
            tile.data[nodeid] = None

    def check_geojson_value(self, value):
        if type(value) is str:
            geojson = json.loads(value)
        else:
            geojson = value

        features = []
        if geojson["type"] == "FeatureCollection":
            for feature in geojson["features"]:
                if "Multi" in feature["geometry"]["type"]:
                    new_collection = self.geo_utils.convert_multipart_to_singlepart(
                        feature["geometry"]
                    )
                    for new_feature in new_collection["features"]:
                        new_feature["id"] = geojson.get("id", str(uuid.uuid4()))
                    features = features + new_collection["features"]
                else:
                    # keep the feature id if it exists, or generate a fresh one.
                    feature["id"] = feature.get("id", str(uuid.uuid4()))
                    features.append(feature)
            geojson["features"] = features
            return geojson
        else:
            raise TypeError

    def transform_value_for_tile(self, value, **kwargs):
        if "format" in kwargs and kwargs["format"] == "esrijson":
            arches_geojson = self.check_geojson_value(
                json.dumps(self.geo_utils.arcgisjson_to_geojson(value))
            )
        else:
            try:
                arches_geojson = self.check_geojson_value(value)
            except (json.JSONDecodeError, KeyError, TypeError):
                try:
                    geometry = GEOSGeometry(value, srid=4326)
                    if geometry.geom_type == "GeometryCollection":
                        arches_geojson = self.geo_utils.convert_geos_geom_collection_to_feature_collection(
                            geometry
                        )
                    else:
                        arches_geojson = {}
                        arches_geojson["type"] = "FeatureCollection"
                        arches_geojson["features"] = []
                        arches_json_geometry = {}
                        arches_json_geometry["geometry"] = (
                            JSONDeserializer().deserialize(geometry.json)
                        )
                        arches_json_geometry["type"] = "Feature"
                        arches_json_geometry["id"] = str(uuid.uuid4())
                        arches_json_geometry["properties"] = {}
                        arches_geojson["features"].append(arches_json_geometry)
                except ValueError:
                    if value in ("", None, "None"):
                        return None

        return arches_geojson

    def transform_export_values(self, value, *args, **kwargs):
        wkt_geoms = []
        for feature in value["features"]:
            wkt_geoms.append(GEOSGeometry(json.dumps(feature["geometry"])))
        return GeometryCollection(wkt_geoms)

    def update(self, tile, data, nodeid=None, action=None):
        new_features_array = tile.data[nodeid]["features"] + data["features"]
        tile.data[nodeid]["features"] = new_features_array
        updated_data = tile.data[nodeid]
        return updated_data

    def find_num(self, current_item):
        if len(current_item) and isinstance(current_item[0], float):
            return decimal.Decimal(str(current_item[0])).as_tuple().exponent
        else:
            return self.find_num(current_item[0])

    def _feature_length_in_bytes(self, feature):
        return len(str(feature).encode("UTF-8"))

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        max_length = (
            32000  # this was 32766, but do we need space for extra part of JSON?
        )

        features = []
        nodevalue["properties"] = {}
        if self._feature_length_in_bytes(nodevalue) < max_length:
            features.append(nodevalue)
        else:
            for feature in nodevalue["features"]:
                new_feature = {"type": "FeatureCollection", "features": [feature]}
                if self._feature_length_in_bytes(new_feature) < max_length:
                    features.append(new_feature)
                else:
                    chunks = self.split_geom(feature, max_length)
                    features = features + chunks

        for feature in features:
            document["geometries"].append(
                {
                    "geom": feature,
                    "nodegroup_id": tile.nodegroup_id,
                    "provisional": provisional,
                    "tileid": tile.pk,
                }
            )
        bounds = self.get_bounds_from_value(nodevalue)
        if bounds is not None:
            minx, miny, maxx, maxy = bounds
            centerx = maxx - (maxx - minx) / 2
            centery = maxy - (maxy - miny) / 2
            document["points"].append(
                {
                    "point": {"lon": centerx, "lat": centery},
                    "nodegroup_id": tile.nodegroup_id,
                    "provisional": provisional,
                }
            )

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif (
                value["op"] == "Point"
                or value["op"] == "LineString"
                or value["op"] == "Polygon"
            ):
                match_query = Match(
                    field="tiles.data.%s.features.geometry.type" % (str(node.pk)),
                    query=value["op"],
                    type="phrase",
                )
                query.must(match_query)
        except KeyError as e:
            pass

    def split_geom(self, feature, max_feature_in_bytes=32766):
        geom = feature["geometry"]
        coordinates = (
            geom["coordinates"]
            if geom["type"] == "LineString"
            else geom["coordinates"][0]
        )
        num_points = len(coordinates)
        num_chunks = self._feature_length_in_bytes(feature) / max_feature_in_bytes
        max_points = int(num_points / num_chunks)

        with connection.cursor() as cur:
            cur.execute(
                "select st_asgeojson(st_subdivide(ST_GeomFromGeoJSON(%s::jsonb), %s))",
                [JSONSerializer().serialize(feature["geometry"]), max_points],
            )

            id = feature["id"] if "id" in feature else ""
            smaller_chunks = [
                {
                    "id": id,
                    "type": "Feature",
                    "geometry": json.loads(item[0]),
                }
                for item in cur.fetchall()
            ]
            feature_collections = [
                {"type": "FeatureCollection", "features": [geometry]}
                for geometry in smaller_chunks
            ]
            return feature_collections

    def get_bounds(self, tile, node):
        bounds = None
        try:
            node_data = tile.data[str(node.pk)]
            bounds = self.get_bounds_from_value(node_data)
        except KeyError as e:
            print(e)
        return bounds

    def get_bounds_from_value(self, node_data):
        bounds = None
        for feature in node_data["features"]:
            geom_collection = GEOSGeometry(
                JSONSerializer().serialize(feature["geometry"])
            )

            if bounds is None:
                bounds = geom_collection.extent
            else:
                minx, miny, maxx, maxy = bounds
                if geom_collection.extent[0] < minx:
                    minx = geom_collection.extent[0]
                if geom_collection.extent[1] < miny:
                    miny = geom_collection.extent[1]
                if geom_collection.extent[2] > maxx:
                    maxx = geom_collection.extent[2]
                if geom_collection.extent[3] > maxy:
                    maxy = geom_collection.extent[3]

                bounds = (minx, miny, maxx, maxy)

        return bounds

    def get_map_layer(self, node=None, preview=False):
        if node is None:
            return None
        elif node.config is None:
            return None
        tile_exists = models.TileModel.objects.filter(
            nodegroup_id=node.nodegroup_id, data__has_key=str(node.nodeid)
        ).exists()
        if not preview and (not tile_exists or not node.config["layerActivated"]):
            return None

        source_name = "resources-%s" % node.nodeid
        layer_name = "%s - %s" % (node.graph.name, node.name)
        if not preview and node.config["layerName"] != "":
            layer_name = node.config["layerName"]
        layer_icon = node.graph.iconclass
        if not preview and node.config["layerIcon"] != "":
            layer_icon = node.config["layerIcon"]

        layer_legend = node.config["layerLegend"]

        if not preview and node.config["advancedStyling"]:
            try:
                style = json.loads(node.config["advancedStyle"])
                for layer in style:
                    layer["source-layer"] = str(node.pk)
                layer_def = json.dumps(style)
            except ValueError:
                layer_def = "[]"
        else:
            with open(
                os.path.dirname(os.path.realpath(__file__))
                + "/geojson_feature_collection_layer_template.txt"
            ) as f:
                src = Template(f.read())
                layer_def = src.substitute(
                    {
                        "source_name": source_name,
                        "nodeid": node.nodeid,
                        "pointColor": node.config["pointColor"],
                        "pointHaloColor": node.config["pointHaloColor"],
                        "radius": node.config["radius"],
                        "expanded_radius": int(node.config["radius"]) * 2,
                        "haloRadius": node.config["haloRadius"],
                        "expanded_haloRadius": int(node.config["haloRadius"]) * 2,
                        "lineColor": node.config["lineColor"],
                        "lineHaloColor": node.config["lineHaloColor"],
                        "weight": node.config["weight"],
                        "haloWeight": node.config["haloWeight"],
                        "expanded_weight": int(node.config["weight"]) * 2,
                        "expanded_haloWeight": int(node.config["haloWeight"]) * 2,
                        "fillColor": node.config["fillColor"],
                        "outlineColor": node.config["outlineColor"],
                        "outlineWeight": node.config["outlineWeight"],
                        "expanded_outlineWeight": int(node.config["outlineWeight"]) * 2,
                    }
                )
        return {
            "nodeid": node.nodeid,
            "name": layer_name,
            "layer_definitions": layer_def,
            "icon": layer_icon,
            "legend": layer_legend,
            "addtomap": node.config["addToMap"],
        }

    def after_update_all(self, tile=None):
        with connection.cursor() as cursor:
            if tile is not None:
                cursor.execute(
                    "SELECT * FROM refresh_tile_geojson_geometries(%s);",
                    [tile.pk],
                )
            else:
                cursor.execute("SELECT * FROM refresh_geojson_geometries();")

    def default_es_mapping(self):
        mapping = {
            "properties": {
                "features": {
                    "properties": {
                        "geometry": {
                            "properties": {
                                "coordinates": {"type": "float"},
                                "type": {"type": "keyword"},
                            }
                        },
                        "id": {"type": "keyword"},
                        "type": {"type": "keyword"},
                        "properties": {"type": "object"},
                    }
                },
                "type": {"type": "keyword"},
            }
        }
        return mapping

    def is_a_literal_in_rdf(self):
        return True

    def to_rdf(self, edge_info, edge):
        # Default to string containing JSON
        g = Graph()
        if edge_info["range_tile_data"] is not None:
            data = edge_info["range_tile_data"]
            if data["type"] == "FeatureCollection":
                for f in data["features"]:
                    if "id" in f:
                        del f["id"]
                    del f["properties"]
            g.add(
                (
                    edge_info["d_uri"],
                    URIRef(edge.ontologyproperty),
                    Literal(JSONSerializer().serialize(data)),
                )
            )
        return g

    def from_rdf(self, json_ld_node):
        # Allow either a JSON literal or a string containing JSON
        try:
            val = json.loads(json_ld_node["@value"])
        except:
            raise ValueError(
                f"Bad Data in GeoJSON, should be JSON string: {json_ld_node}"
            )
        if "features" not in val or type(val["features"]) != list:
            raise ValueError(f"GeoJSON must have features array")
        for f in val["features"]:
            if "properties" not in f:
                f["properties"] = {}
        return val

    def validate_from_rdf(self, value):
        if type(value) == str:
            # first deserialize it from a string
            value = json.loads(value)
        return self.validate(value)

    def pre_tile_save(self, tile, nodeid):
        if tile.data[nodeid]:
            tile.data[nodeid] = self.check_geojson_value(tile.data[nodeid])
