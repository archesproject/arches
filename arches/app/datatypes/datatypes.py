import uuid
import json
import decimal
import base64
import re
import logging
import os
from pathlib import Path
import ast
from distutils import util
from datetime import datetime
from mimetypes import MimeTypes
from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.date_utils import ExtendedDateFormat
from arches.app.utils.module_importer import get_class_from_modulename
from arches.app.utils.permission_backend import user_is_resource_reviewer
from arches.app.utils.geo_utils import GeoUtils
import arches.app.utils.task_management as task_management
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Range, Term, Terms, Nested, Exists, RangeDSLException
from arches.app.search.search_engine_factory import SearchEngineInstance as se
from arches.app.search.mappings import RESOURCES_INDEX, RESOURCE_RELATIONS_INDEX
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.utils.translation import ugettext as _
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import GeometryCollection
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import Polygon
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from edtf import parse_edtf


# One benefit of shifting to python3.x would be to use
# importlib.util.LazyLoader to load rdflib (and other lesser
# used but memory soaking libs)
from rdflib import Namespace, URIRef, Literal, BNode
from rdflib import ConjunctiveGraph as Graph
from rdflib.namespace import RDF, RDFS, XSD, DC, DCTERMS

archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
cidoc_nm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")

EARTHCIRCUM = 40075016.6856
PIXELSPERTILE = 256

logger = logging.getLogger(__name__)

class DataTypeFactory(object):
    _datatypes = None
    _datatype_instances = {}

    def __init__(self):
        if DataTypeFactory._datatypes is None:
            DataTypeFactory._datatypes = {datatype.datatype: datatype for datatype in models.DDataType.objects.all()}
        self.datatypes = DataTypeFactory._datatypes
        self.datatype_instances = DataTypeFactory._datatype_instances

    def get_instance(self, datatype):
        try:
            d_datatype = DataTypeFactory._datatypes[datatype]
        except KeyError:
            DataTypeFactory._datatypes = {datatype.datatype: datatype for datatype in models.DDataType.objects.all()}
            d_datatype = DataTypeFactory._datatypes[datatype]
            self.datatypes = DataTypeFactory._datatypes
        try:
            datatype_instance = DataTypeFactory._datatype_instances[d_datatype.classname]
        except KeyError:
            class_method = get_class_from_modulename(d_datatype.modulename, d_datatype.classname, settings.DATATYPE_LOCATIONS)
            datatype_instance = class_method(d_datatype)
            DataTypeFactory._datatype_instances[d_datatype.classname] = datatype_instance
            self.datatype_instances = DataTypeFactory._datatype_instances
        return datatype_instance

class StringDataType(BaseDataType):
    def validate(self, value, row_number=None, source=None, node=None, nodeid=None):
        errors = []
        try:
            if value is not None:
                value.upper()
        except:
            message = _("This is not a string")
            error_message = self.create_error_message(value, source, row_number, message)
            errors.append(error_message)
        return errors

    def clean(self, tile, nodeid):
        if tile.data[nodeid] in ["", "''"]:
            tile.data[nodeid] = None

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        val = {"string": nodevalue, "nodegroup_id": tile.nodegroup_id, "provisional": provisional}
        document["strings"].append(val)

    def transform_export_values(self, value, *args, **kwargs):
        if value is not None:
            return value

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        if nodevalue is not None:
            if settings.WORDS_PER_SEARCH_TERM is None or (len(nodevalue.split(" ")) < settings.WORDS_PER_SEARCH_TERM):
                terms.append(nodevalue)
        return terms

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "":
                match_type = "phrase_prefix" if "~" in value["op"] else "phrase"
                match_query = Match(field="tiles.data.%s" % (str(node.pk)), query=value["val"], type=match_type)
                if "!" in value["op"]:
                    query.must_not(match_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(match_query)
        except KeyError as e:
            pass

    def is_a_literal_in_rdf(self):
        return True

    def to_rdf(self, edge_info, edge):
        # returns an in-memory graph object, containing the domain resource, its
        # type and the string as a string literal
        g = Graph()
        if edge_info["range_tile_data"] is not None:
            g.add((edge_info["d_uri"], RDF.type, URIRef(edge.domainnode.ontologyclass)))
            g.add((edge_info["d_uri"], URIRef(edge.ontologyproperty), Literal(edge_info["range_tile_data"])))
        return g

    def from_rdf(self, json_ld_node):
        # returns the string value only
        # FIXME: Language?
        value = get_value_from_jsonld(json_ld_node)
        try:
            return value[0]
        except (AttributeError, KeyError) as e:
            pass


class NumberDataType(BaseDataType):
    def validate(self, value, row_number=None, source="", node=None, nodeid=None):
        errors = []

        try:
            if value == "":
                value = None
            if value is not None:
                decimal.Decimal(value)
        except Exception:
            dt = self.datatype_model.datatype
            message = _("Not a properly formatted number")
            error_message = self.create_error_message(value, source, row_number, message)
            errors.append(error_message)
        return errors

    def transform_value_for_tile(self, value, **kwargs):
        try:
            if value == "":
                value = None
            elif value.isdigit():
                value = int(value)
            else:
                value = float(value)
        except AttributeError:
            pass
        return value

    def pre_tile_save(self, tile, nodeid):
        try:
            if tile.data[nodeid] == "":
                tile.data[nodeid] = None
            elif tile.data[nodeid].isdigit():
                tile.data[nodeid] = int(tile.data[nodeid])
            else:
                tile.data[nodeid] = float(tile.data[nodeid])
        except AttributeError:
            pass

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        document["numbers"].append({"number": nodevalue, "nodegroup_id": tile.nodegroup_id, "provisional": provisional})

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "":
                if value["op"] != "eq":
                    operators = {"gte": None, "lte": None, "lt": None, "gt": None}
                    operators[value["op"]] = value["val"]
                else:
                    operators = {"gte": value["val"], "lte": value["val"]}
                search_query = Range(field="tiles.data.%s" % (str(node.pk)), **operators)
                query.must(search_query)
        except KeyError:
            pass

    def is_a_literal_in_rdf(self):
        return True

    def to_rdf(self, edge_info, edge):
        # returns an in-memory graph object, containing the domain resource, its
        # type and the number as a numeric literal (as this is how it is in the JSON)
        g = Graph()
        rtd = (
            int(edge_info["range_tile_data"])
            if type(edge_info["range_tile_data"]) == float and edge_info["range_tile_data"].is_integer()
            else edge_info["range_tile_data"]
        )
        if rtd is not None:
            g.add((edge_info["d_uri"], RDF.type, URIRef(edge.domainnode.ontologyclass)))
            g.add((edge_info["d_uri"], URIRef(edge.ontologyproperty), Literal(rtd)))
        return g

    def from_rdf(self, json_ld_node):
        # expects a node taken from an expanded json-ld graph
        # returns the value, or None if no "@value" key is found
        value = get_value_from_jsonld(json_ld_node)
        try:
            return value[0]  # should already be cast as a number in the JSON
        except (AttributeError, KeyError) as e:
            pass

    def default_es_mapping(self):
        mapping = {"type": "double"}
        return mapping


class BooleanDataType(BaseDataType):
    def validate(self, value, row_number=None, source="", node=None, nodeid=None):
        errors = []
        try:
            if value is not None:
                type(bool(util.strtobool(str(value)))) is True
        except Exception:
            message = _("Not of type boolean")
            error_message = self.create_error_message(value, source, row_number, message)
            errors.append(error_message)

        return errors

    def transform_value_for_tile(self, value, **kwargs):
        return bool(util.strtobool(str(value)))

    def append_search_filters(self, value, node, query, request):
        try:
            if value["val"] == "null" or value["val"] == "not_null":
                value["op"] = value["val"]
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "" and value["val"] is not None:
                term = True if value["val"] == "t" else False
                query.must(Term(field="tiles.data.%s" % (str(node.pk)), term=term))
        except KeyError as e:
            pass

    def to_rdf(self, edge_info, edge):
        # returns an in-memory graph object, containing the domain resource, its
        # type and the number as a numeric literal (as this is how it is in the JSON)
        g = Graph()
        if edge_info["range_tile_data"] is not None:
            g.add((edge_info["d_uri"], RDF.type, URIRef(edge.domainnode.ontologyclass)))
            g.add((edge_info["d_uri"], URIRef(edge.ontologyproperty), Literal(edge_info["range_tile_data"])))
        return g

    def is_a_literal_in_rdf(self):
        return True

    def from_rdf(self, json_ld_node):
        # expects a node taken from an expanded json-ld graph
        # returns the value, or None if no "@value" key is found
        value = get_value_from_jsonld(json_ld_node)
        try:
            return value[0]
        except (AttributeError, KeyError) as e:
            pass

    def default_es_mapping(self):
        mapping = {"type": "boolean"}
        return mapping


class DateDataType(BaseDataType):
    def validate(self, value, row_number=None, source="", node=None, nodeid=None):
        errors = []
        if value is not None:
            valid_date_format, valid = self.get_valid_date_format(value)
            if valid is False:
                message = _(
                    "Incorrect format. Confirm format is in settings.DATE_FORMATS or set the format in settings.DATE_IMPORT_EXPORT_FORMAT."
                )
                error_message = self.create_error_message(value, source, row_number, message)
                errors.append(error_message)
        return errors

    def get_valid_date_format(self, value):
        valid = False
        valid_date_format = ""
        date_formats = settings.DATE_FORMATS["Python"]
        for date_format in date_formats:
            if valid is False:
                try:
                    datetime.strptime(value, date_format)
                    valid = True
                    valid_date_format = date_format
                except ValueError:
                    pass
        return valid_date_format, valid

    def transform_value_for_tile(self, value, **kwargs):
        if type(value) == list:
            value = value[0]
        valid_date_format, valid = self.get_valid_date_format(value)
        if valid:
            value = datetime.strptime(value, valid_date_format).astimezone().isoformat(timespec="milliseconds")
        else:
            v = datetime.strptime(value, settings.DATE_IMPORT_EXPORT_FORMAT)
            value = v.astimezone().isoformat(timespec="milliseconds")
        return value

    def transform_export_values(self, value, *args, **kwargs):
        valid_date_format, valid = self.get_valid_date_format(value)
        if valid:
            value = datetime.strptime(value, valid_date_format).strftime(settings.DATE_IMPORT_EXPORT_FORMAT)
        else:
            logger.warning(_("{value} is an invalid date format").format(**locals()))
        return value

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        document["dates"].append(
            {"date": ExtendedDateFormat(nodevalue).lower, "nodegroup_id": tile.nodegroup_id, "nodeid": nodeid, "provisional": provisional}
        )

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "" and value["val"] is not None:
                try:
                    date_value = datetime.strptime(value["val"], "%Y-%m-%d %H:%M:%S%z").astimezone().isoformat()
                except ValueError:
                    date_value = value["val"]
                if value["op"] != "eq":
                    operators = {"gte": None, "lte": None, "lt": None, "gt": None}
                    operators[value["op"]] = date_value
                else:
                    operators = {"gte": date_value, "lte": date_value}
                search_query = Range(field="tiles.data.%s" % (str(node.pk)), **operators)
                query.must(search_query)
        except KeyError:
            pass

    def after_update_all(self):
        config = cache.get("time_wheel_config_anonymous")
        if config is not None:
            cache.delete("time_wheel_config_anonymous")

    def is_a_literal_in_rdf(self):
        return True

    def to_rdf(self, edge_info, edge):
        # returns an in-memory graph object, containing the domain resource, its
        # type and the number as a numeric literal (as this is how it is in the JSON)
        g = Graph()
        if edge_info["range_tile_data"] is not None:
            g.add((edge_info["d_uri"], RDF.type, URIRef(edge.domainnode.ontologyclass)))
            g.add((edge_info["d_uri"], URIRef(edge.ontologyproperty), Literal(edge_info["range_tile_data"], datatype=XSD.dateTime)))
        return g

    def from_rdf(self, json_ld_node):
        # expects a node taken from an expanded json-ld graph
        # returns the value, or None if no "@value" key is found
        value = get_value_from_jsonld(json_ld_node)
        try:
            return value[0]
        except (AttributeError, KeyError) as e:
            pass

    def default_es_mapping(self):
        es_date_formats = "||".join(settings.DATE_FORMATS["Elasticsearch"])
        mapping = {"type": "date", "format": es_date_formats}
        return mapping

    def get_display_value(self, tile, node):
        data = self.get_tile_data(tile)
        try:
            og_value = data[str(node.pk)]
            valid_date_format, valid = self.get_valid_date_format(og_value)
            new_date_format = settings.DATE_FORMATS["Python"][settings.DATE_FORMATS["JavaScript"].index(node.config["dateFormat"])]
            value = datetime.strptime(og_value, valid_date_format).strftime(new_date_format)
        except TypeError:
            value = data[str(node.pk)]
        return value


class EDTFDataType(BaseDataType):
    def validate(self, value, row_number=None, source="", node=None, nodeid=None):
        errors = []
        if value is not None:
            if not ExtendedDateFormat(value).is_valid():
                message = _("Incorrect Extended Date Time Format. See http://www.loc.gov/standards/datetime/ for supported formats.")
                error_message = self.create_error_message(value, source, row_number, message)
                errors.append(error_message)
        return errors

    def get_display_value(self, tile, node):
        data = self.get_tile_data(tile)
        try:
            value = data[str(node.pk)]["value"]
        except TypeError:
            value = data[str(node.pk)]
        return value

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        def add_date_to_doc(document, edtf):
            if edtf.lower == edtf.upper:
                if edtf.lower is not None:
                    document["dates"].append(
                        {"date": edtf.lower, "nodegroup_id": tile.nodegroup_id, "nodeid": nodeid, "provisional": provisional}
                    )
            else:
                dr = {}
                if edtf.lower_fuzzy is not None:
                    dr["gte"] = edtf.lower_fuzzy
                    document["dates"].append(
                        {"date": edtf.lower_fuzzy, "nodegroup_id": tile.nodegroup_id, "nodeid": nodeid, "provisional": provisional}
                    )
                if edtf.upper_fuzzy is not None:
                    dr["lte"] = edtf.upper_fuzzy
                    document["dates"].append(
                        {"date": edtf.upper_fuzzy, "nodegroup_id": tile.nodegroup_id, "nodeid": nodeid, "provisional": provisional}
                    )
                document["date_ranges"].append(
                    {"date_range": dr, "nodegroup_id": tile.nodegroup_id, "nodeid": nodeid, "provisional": provisional}
                )

        # update the indexed tile value to support adv. search
        tile.data[nodeid] = {"value": nodevalue, "dates": [], "date_ranges": []}

        node = models.Node.objects.get(nodeid=nodeid)
        edtf = ExtendedDateFormat(nodevalue, **node.config)
        if edtf.result_set:
            for result in edtf.result_set:
                add_date_to_doc(document, result)
                add_date_to_doc(tile.data[nodeid], result)
        else:
            add_date_to_doc(document, edtf)
            add_date_to_doc(tile.data[nodeid], edtf)

    def append_search_filters(self, value, node, query, request):
        def add_date_to_doc(query, edtf):
            if value["op"] == "eq":
                if edtf.lower != edtf.upper:
                    raise Exception(_('Only dates that specify an exact year, month, and day can be used with the "=" operator'))
                query.should(Match(field="tiles.data.%s.dates.date" % (str(node.pk)), query=edtf.lower, type="phrase_prefix"))
            else:
                if value["op"] == "overlaps":
                    operators = {"gte": edtf.lower, "lte": edtf.upper}
                else:
                    if edtf.lower != edtf.upper:
                        raise Exception(
                            _(
                                'Only dates that specify an exact year, month, \
                                    and day can be used with the ">", "<", ">=", and "<=" operators'
                            )
                        )

                    operators = {value["op"]: edtf.lower or edtf.upper}

                try:
                    query.should(Range(field="tiles.data.%s.dates.date" % (str(node.pk)), **operators))
                    query.should(Range(field="tiles.data.%s.date_ranges.date_range" % (str(node.pk)), relation="intersects", **operators))
                except RangeDSLException:
                    if edtf.lower is None and edtf.upper is None:
                        raise Exception(_("Invalid date specified."))

        if value["op"] == "null" or value["op"] == "not_null":
            self.append_null_search_filters(value, node, query, request)
        elif value["val"] != "" and value["val"] is not None:
            edtf = ExtendedDateFormat(value["val"])
            if edtf.result_set:
                for result in edtf.result_set:
                    add_date_to_doc(query, result)
            else:
                add_date_to_doc(query, edtf)

    def default_es_mapping(self):
        mapping = {"properties": {"value": {"type": "text", "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}}}}}
        return mapping


class GeojsonFeatureCollectionDataType(BaseDataType):
    def validate(self, value, row_number=None, source=None, node=None, nodeid=None):
        errors = []
        coord_limit = 1500
        coordinate_count = 0

        def validate_geom(geom, coordinate_count=0):
            try:
                coordinate_count += geom.num_coords
                bbox = Polygon(settings.DATA_VALIDATION_BBOX)
                if coordinate_count > coord_limit:
                    message = f"Geometry has too many coordinates for Elasticsearch ({coordinate_count}), \
                        Please limit to less then {coord_limit} coordinates of 5 digits of precision or less."
                    errors.append(
                        {
                            "type": "ERROR",
                            "message": "datatype: {0} value: {1} {2} - {3}. {4}".format(
                                self.datatype_model.datatype, value, source, message, "This data was not imported."
                            ),
                        }
                    )

                if bbox.contains(geom) == False:
                    message = "Geometry does not fall within the bounding box of the selected coordinate system. \
                         Adjust your coordinates or your settings.DATA_EXTENT_VALIDATION property."
                    errors.append(
                        {
                            "type": "ERROR",
                            "message": "datatype: {0} value: {1} {2} - {3}. {4}".format(
                                self.datatype_model.datatype, value, source, message, "This data was not imported."
                            ),
                        }
                    )
            except Exception:
                message = "Not a properly formatted geometry"
                errors.append(
                    {
                        "type": "ERROR",
                        "message": "datatype: {0} value: {1} {2} - {3}. {4}.".format(
                            self.datatype_model.datatype, value, source, message, "This data was not imported."
                        ),
                    }
                )

        if value is not None:
            for feature in value["features"]:
                try:
                    geom = GEOSGeometry(JSONSerializer().serialize(feature["geometry"]))
                    validate_geom(geom, coordinate_count)
                except Exception:
                    message = _("Unable to serialize some geometry features")
                    error_message = self.create_error_message(value, source, row_number, message)
                    errors.append(error_message)
        return errors

    def clean(self, tile, nodeid):
        if tile.data[nodeid] is not None and "features" in tile.data[nodeid]:
            if len(tile.data[nodeid]["features"]) == 0:
                tile.data[nodeid] = None

    def transform_value_for_tile(self, value, **kwargs):
        if "format" in kwargs and kwargs["format"] == "esrijson":
            arches_geojson = GeoUtils().arcgisjson_to_geojson(value)
        else:
            arches_geojson = {}
            arches_geojson["type"] = "FeatureCollection"
            arches_geojson["features"] = []
            geometry = GEOSGeometry(value, srid=4326)
            if geometry.geom_type == "GeometryCollection":
                for geom in geometry:
                    arches_json_geometry = {}
                    arches_json_geometry["geometry"] = JSONDeserializer().deserialize(GEOSGeometry(geom, srid=4326).json)
                    arches_json_geometry["type"] = "Feature"
                    arches_json_geometry["id"] = str(uuid.uuid4())
                    arches_json_geometry["properties"] = {}
                    arches_geojson["features"].append(arches_json_geometry)
            else:
                arches_json_geometry = {}
                arches_json_geometry["geometry"] = JSONDeserializer().deserialize(geometry.json)
                arches_json_geometry["type"] = "Feature"
                arches_json_geometry["id"] = str(uuid.uuid4())
                arches_json_geometry["properties"] = {}
                arches_geojson["features"].append(arches_json_geometry)

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

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        document["geometries"].append({"geom": nodevalue, "nodegroup_id": tile.nodegroup_id, "provisional": provisional, "tileid": tile.pk})
        bounds = self.get_bounds_from_value(nodevalue)
        if bounds is not None:
            minx, miny, maxx, maxy = bounds
            centerx = maxx - (maxx - minx) / 2
            centery = maxy - (maxy - miny) / 2
            document["points"].append(
                {"point": {"lon": centerx, "lat": centery}, "nodegroup_id": tile.nodegroup_id, "provisional": provisional}
            )

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
            geom_collection = GEOSGeometry(JSONSerializer().serialize(feature["geometry"]))

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
        count = models.TileModel.objects.filter(nodegroup_id=node.nodegroup_id, data__has_key=str(node.nodeid)).count()
        if not preview and (count < 1 or not node.config["layerActivated"]):
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
            layer_def = """[
                {
                    "id": "resources-fill-%(nodeid)s",
                    "type": "fill",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Polygon"],["==", "total", 1]],
                    "paint": {
                        "fill-color": "%(fillColor)s"
                    }
                },
                {
                    "id": "resources-fill-%(nodeid)s-click",
                    "type": "fill",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Polygon"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "fill-color": "%(fillColor)s"
                    }
                },
                {
                    "id": "resources-fill-%(nodeid)s-hover",
                    "type": "fill",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Polygon"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "fill-color": "%(fillColor)s"
                    }
                },
                {
                    "id": "resources-poly-outline-%(nodeid)s",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all",["==", "$type", "Polygon"],["==", "total", 1]],
                    "paint": {
                        "line-width": ["case",
                            ["boolean", ["feature-state", "hover"], false],
                            %(expanded_outlineWeight)s,
                            %(outlineWeight)s
                        ],
                        "line-color": "%(outlineColor)s"
                    }
                },
                {
                    "id": "resources-poly-outline-%(nodeid)s-hover",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all",["==", "$type", "Polygon"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "line-width": %(expanded_outlineWeight)s,
                        "line-color": "%(outlineColor)s"
                    }
                },
                {
                    "id": "resources-poly-outline-%(nodeid)s-click",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all",["==", "$type", "Polygon"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "line-width": %(expanded_outlineWeight)s,
                        "line-color": "%(outlineColor)s"
                    }
                },
                {
                    "id": "resources-line-halo-%(nodeid)s",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "LineString"],["==", "total", 1]],
                    "paint": {
                        "line-width": ["case",
                            ["boolean", ["feature-state", "hover"], false],
                            %(expanded_haloWeight)s,
                            %(haloWeight)s
                        ],
                        "line-color": "%(lineHaloColor)s"
                    }
                },
                {
                    "id": "resources-line-%(nodeid)s",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all",["==", "$type", "LineString"],["==", "total", 1]],
                    "paint": {
                        "line-width": ["case",
                            ["boolean", ["feature-state", "hover"], false],
                            %(expanded_weight)s,
                            %(weight)s
                        ],
                        "line-color": "%(lineColor)s"
                    }
                },
                {
                    "id": "resources-line-halo-%(nodeid)s-hover",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all",["==", "$type", "LineString"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "line-width": %(expanded_haloWeight)s,
                        "line-color": "%(lineHaloColor)s"
                    }
                },
                {
                    "id": "resources-line-%(nodeid)s-hover",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all",["==", "$type", "LineString"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "line-width": %(expanded_weight)s,
                        "line-color": "%(lineColor)s"
                    }
                },
                {
                    "id": "resources-line-halo-%(nodeid)s-click",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "LineString"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "line-width": %(expanded_haloWeight)s,
                        "line-color": "%(lineHaloColor)s"
                    }
                },
                {
                    "id": "resources-line-%(nodeid)s-click",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "LineString"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "line-width": %(expanded_weight)s,
                        "line-color": "%(lineColor)s"
                    }
                },

                {
                    "id": "resources-point-halo-%(nodeid)s-hover",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "circle-radius": %(expanded_haloRadius)s,
                        "circle-color": "%(pointHaloColor)s"
                    }
                },
                {
                    "id": "resources-point-%(nodeid)s-hover",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "circle-radius": %(expanded_radius)s,
                        "circle-color": "%(pointColor)s"
                    }
                },

                {
                    "id": "resources-point-halo-%(nodeid)s",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],["==", "total", 1]],
                    "paint": {
                        "circle-radius": ["case",
                            ["boolean", ["feature-state", "hover"], false],
                            %(expanded_haloRadius)s,
                            %(haloRadius)s
                        ],
                        "circle-color": "%(pointHaloColor)s"
                    }
                },
                {
                    "id": "resources-point-%(nodeid)s",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],["==", "total", 1]],
                    "paint": {
                        "circle-radius": ["case",
                            ["boolean", ["feature-state", "hover"], false],
                            %(expanded_radius)s,
                            %(radius)s
                        ],
                        "circle-color": "%(pointColor)s"
                    }
                },

                {
                    "id": "resources-point-halo-%(nodeid)s-click",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "circle-radius": %(expanded_haloRadius)s,
                        "circle-color": "%(pointHaloColor)s"
                    }
                },
                {
                    "id": "resources-point-%(nodeid)s-click",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "circle-radius": %(expanded_radius)s,
                        "circle-color": "%(pointColor)s"
                    }
                },
                {
                    "id": "resources-cluster-point-halo-%(nodeid)s",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],[">", "total", 1]],
                    "paint": {
                        "circle-radius": {
                            "property": "total",
                            "stops": [
                                [0,   22],
                                [50, 24],
                                [100, 26],
                                [200, 28],
                                [400, 30],
                                [800, 32],
                                [1200, 34],
                                [1600, 36],
                                [2000, 38],
                                [2500, 40],
                                [3000, 42],
                                [4000, 44],
                                [5000, 46]
                            ]
                        },
                        "circle-color": "%(pointHaloColor)s"
                    }
                },
                {
                    "id": "resources-cluster-point-%(nodeid)s",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],[">", "total", 1]],
                    "paint": {
                         "circle-radius": {
                             "property": "total",
                             "type": "exponential",
                             "stops": [
                                 [0,   12],
                                 [50, 14],
                                 [100, 16],
                                 [200, 18],
                                 [400, 20],
                                 [800, 22],
                                 [1200, 24],
                                 [1600, 26],
                                 [2000, 28],
                                 [2500, 30],
                                 [3000, 32],
                                 [4000, 34],
                                 [5000, 36]
                             ]
                         },
                        "circle-color": "%(pointColor)s"
                    }
                },
                {
                     "id": "resources-cluster-count-%(nodeid)s",
                     "type": "symbol",
                     "source": "%(source_name)s",
                     "source-layer": "%(nodeid)s",
                     "layout": {
                         "text-field": "{total}",
                         "text-size": 10
                     },
                     "paint": {
                        "text-color": "#fff"
                    },
                     "filter": ["all", [">", "total", 1]]
                 }
            ]""" % {
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
        return {
            "nodeid": node.nodeid,
            "name": layer_name,
            "layer_definitions": layer_def,
            "icon": layer_icon,
            "legend": layer_legend,
            "addtomap": node.config["addToMap"],
        }

    def after_update_all(self):
        from arches.app.tasks import refresh_materialized_view, log_error

        celery_worker_running = task_management.check_if_celery_available()
        if celery_worker_running is True:
            res = refresh_materialized_view.apply_async((), link_error=log_error.s())
        elif settings.AUTO_REFRESH_GEOM_VIEW:
            with connection.cursor() as cursor:
                sql = """
                    REFRESH MATERIALIZED VIEW mv_geojson_geoms;
                """
                cursor.execute(sql)

    def default_es_mapping(self):
        # let ES dyanamically map this datatype
        return

    def is_a_literal_in_rdf(self):
        return True

    def to_rdf(self, edge_info, edge):
        # Default to string containing JSON
        g = Graph()
        if edge_info["range_tile_data"] is not None:
            data = edge_info["range_tile_data"]
            if data["type"] == "FeatureCollection":
                for f in data["features"]:
                    del f["id"]
                    del f["properties"]
            g.add((edge_info["d_uri"], URIRef(edge.ontologyproperty), Literal(JSONSerializer().serialize(data))))
        return g

    def from_rdf(self, json_ld_node):
        # Allow either a JSON literal or a string containing JSON
        try:
            val = json.loads(json_ld_node["@value"])
        except:
            raise ValueError(f"Bad Data in GeoJSON, should be JSON string: {json_ld_node}")
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


class FileListDataType(BaseDataType):
    def __init__(self, model=None):
        super(FileListDataType, self).__init__(model=model)
        self.node_lookup = {}

    def validate(self, value, row_number=None, source=None, node=None, nodeid=None):
        if node:
            self.node_lookup[str(node.pk)] = node
        elif nodeid:
            if str(nodeid) in self.node_lookup:
                node = self.node_lookup[str(nodeid)]
            else:
                node = models.Node.objects.get(nodeid=nodeid)
                self.node_lookup[str(nodeid)] = node

        def format_bytes(size):
            # 2**10 = 1024
            power = 2 ** 10
            n = 0
            power_labels = {0: "", 1: "kilo", 2: "mega", 3: "giga", 4: "tera"}
            while size > power:
                size /= power
                n += 1
            return size, power_labels[n] + "bytes"

        errors = []
        try:
            config = node.config
            limit = config["maxFiles"]
            max_size = config["maxFileSize"] if "maxFileSize" in config.keys() else None

            if value is not None and config["activateMax"] is True and len(value) > limit:
                message = _("This node has a limit of {0} files. Please reduce files.".format(limit))
                errors.append({"type": "ERROR", "message": message})

            if max_size is not None:
                formatted_max_size = format_bytes(max_size)
                for v in value:
                    if v["size"] > max_size:
                        message = _(
                            "This node has a file-size limit of {0}. Please reduce file size or contact your sysadmin.".format(
                                formatted_max_size
                            )
                        )
                        errors.append({"type": "ERROR", "message": message})
        except Exception as e:
            dt = self.datatype_model.datatype
            message = _("datatype: {0}, value: {1} - {2} .".format(dt, value, e))
            errors.append({"type": "ERROR", "message": message})
        return errors

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        try:
            for f in tile.data[str(nodeid)]:
                val = {"string": f["name"], "nodegroup_id": tile.nodegroup_id, "provisional": provisional}
                document["strings"].append(val)
        except KeyError as e:
            for k, pe in tile.provisionaledits.items():
                for f in pe["value"][nodeid]:
                    val = {"string": f["name"], "nodegroup_id": tile.nodegroup_id, "provisional": provisional}
                    document["strings"].append(val)

    def get_search_terms(self, nodevalue, nodeid):
        terms = []
        for file_obj in nodevalue:
            if file_obj["name"] is not None:
                terms.append(file_obj["name"])

        return terms

    def get_display_value(self, tile, node):
        data = self.get_tile_data(tile)
        files = data[str(node.pk)]
        file_list_str = ""
        if files is not None:
            for f in files:
                file_list_str = file_list_str + f["name"] + " | "

        return file_list_str

    def handle_request(self, current_tile, request, node):
        # this does not get called when saving data from the mobile app
        previously_saved_tile = models.TileModel.objects.filter(pk=current_tile.tileid)
        user = request.user
        if hasattr(request.user, "userprofile") is not True:
            models.UserProfile.objects.create(user=request.user)
        user_is_reviewer = user_is_resource_reviewer(request.user)
        current_tile_data = self.get_tile_data(current_tile)
        if previously_saved_tile.count() == 1:
            previously_saved_tile_data = self.get_tile_data(previously_saved_tile[0])
            if previously_saved_tile_data[str(node.pk)] is not None:
                for previously_saved_file in previously_saved_tile_data[str(node.pk)]:
                    previously_saved_file_has_been_removed = True
                    for incoming_file in current_tile_data[str(node.pk)]:
                        if previously_saved_file["file_id"] == incoming_file["file_id"]:
                            previously_saved_file_has_been_removed = False
                    if previously_saved_file_has_been_removed:
                        try:
                            deleted_file = models.File.objects.get(pk=previously_saved_file["file_id"])
                            deleted_file.delete()
                        except models.File.DoesNotExist:
                            logger.exception(_("File does not exist"))

        files = request.FILES.getlist("file-list_" + str(node.pk), [])

        for file_data in files:
            file_model = models.File()
            file_model.path = file_data
            file_model.tile = current_tile
            if models.TileModel.objects.filter(pk=current_tile.tileid).count() > 0:
                file_model.save()
            if current_tile_data[str(node.pk)] is not None:
                resave_tile = False
                updated_file_records = []
                for file_json in current_tile_data[str(node.pk)]:
                    if file_json["name"] == file_data.name and file_json["url"] is None:
                        file_json["file_id"] = str(file_model.pk)
                        file_json["url"] = "/files/" + str(file_model.fileid)
                        file_json["status"] = "uploaded"
                        resave_tile = True
                    updated_file_records.append(file_json)
                if resave_tile is True:
                    # resaving model to assign url from file_model
                    # importing proxy model errors, so cannot use super on the proxy model to save
                    if previously_saved_tile.count() == 1:
                        tile_to_update = previously_saved_tile[0]
                        if user_is_reviewer:
                            tile_to_update.data[str(node.pk)] = updated_file_records
                        else:
                            tile_to_update.provisionaledits[str(user.id)]["value"][str(node.pk)] = updated_file_records
                        tile_to_update.save()

    def get_compatible_renderers(self, file_data):
        extension = Path(file_data["name"]).suffix.strip(".")
        compatible_renderers = []
        for renderer in settings.RENDERERS:
            if extension.lower() == renderer["ext"].lower():
                compatible_renderers.append(renderer["id"])
            else:
                excluded_extensions = renderer["exclude"].split(",")
                if extension not in excluded_extensions:
                    renderer_mime = renderer["type"].split("/")
                    file_mime = file_data["type"].split("/")
                    if len(renderer_mime) == 2:
                        renderer_class, renderer_type = renderer_mime[0], renderer_mime[1]
                        if len(file_mime) == 2:
                            file_class = file_mime[0]
                            if renderer_class.lower() == file_class.lower() and renderer_type == "*":
                                compatible_renderers.append(renderer["id"])
        return compatible_renderers

    def transform_value_for_tile(self, value, **kwargs):
        """
        Accepts a comma delimited string of file paths as 'value' to create a file datatype value
        with corresponding file record in the files table for each path. Only the basename of each path is used, so
        the accuracy of the full path is not important. However the name of each file must match the name of a file in
        the directory from which Arches will request files. By default, this is the 'uploadedfiles' directory
        in a project.

        """

        mime = MimeTypes()
        tile_data = []
        for file_path in value.split(","):
            tile_file = {}
            try:
                file_stats = os.stat(file_path)
                tile_file["lastModified"] = file_stats.st_mtime
                tile_file["size"] = file_stats.st_size
            except FileNotFoundError as e:
                pass
            tile_file["status"] = "uploaded"
            tile_file["name"] = os.path.basename(file_path)
            tile_file["type"] = mime.guess_type(file_path)[0]
            tile_file["type"] = "" if tile_file["type"] is None else tile_file["type"]
            file_path = "uploadedfiles/" + str(tile_file["name"])
            tile_file["file_id"] = str(uuid.uuid4())
            models.File.objects.get_or_create(fileid=tile_file["file_id"], path=file_path)
            tile_file["url"] = "/files/" + tile_file["file_id"]
            tile_file["accepted"] = True
            compatible_renderers = self.get_compatible_renderers(tile_file)
            if len(compatible_renderers) == 1:
                tile_file["renderer"] = compatible_renderers[0]
            tile_data.append(tile_file)
        return json.loads(json.dumps(tile_data))

    def pre_tile_save(self, tile, nodeid):
        # TODO If possible this method should probably replace 'handle request' and perhaps 'process mobile data'
        if tile.data[nodeid]:
            for file in tile.data[nodeid]:
                try:
                    if file["file_id"]:
                        if file["url"] == "/files/{}".format(file["file_id"]):
                            val = uuid.UUID(file["file_id"])  # to test if file_id is uuid
                            file_path = "uploadedfiles/" + file["name"]
                            try:
                                file_model = models.File.objects.get(pk=file["file_id"])
                            except ObjectDoesNotExist:
                                # Do not use get_or_create here because django can create a different file name applied to the file_path
                                # for the same file_id causing a 'create' when a 'get' was intended
                                file_model = models.File.objects.create(pk=file["file_id"], path=file_path)
                            if not file_model.tile_id:
                                file_model.tile = tile
                                file_model.save()
                        else:
                            logger.warning(_("The file url is invalid"))
                    else:
                        logger.warning(_("A file is not available for this tile"))
                except ValueError:
                    logger.warning(_("This file's fileid is not a valid UUID"))

    def transform_export_values(self, value, *args, **kwargs):
        return ",".join([settings.MEDIA_URL + "uploadedfiles/" + str(file["name"]) for file in value])

    def is_a_literal_in_rdf(self):
        return False

    def get_rdf_uri(self, node, data, which="r"):
        if type(data) == list:
            l = []
            for x in data:
                if x["url"].startswith("/"):
                    l.append(URIRef(archesproject[x["url"][1:]]))
                else:
                    l.append(URIRef(archesproject[x["url"]]))
            return l
        elif data:
            if data["url"].startswith("/"):
                return URIRef(archesproject[data["url"][1:]])
            else:
                return URIRef(archesproject[data["url"]])
        else:
            return node

    def to_rdf(self, edge_info, edge):
        # outputs a graph holding an RDF representation of the file stored in the Arches instance

        g = Graph()

        unit_nt = """
        <http://vocab.getty.edu/aat/300055644> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.cidoc-crm.org/cidoc-crm/E55_Type> .
        <http://vocab.getty.edu/aat/300055644> <http://www.w3.org/2000/01/rdf-schema#label> "height" .
        <http://vocab.getty.edu/aat/300055647> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.cidoc-crm.org/cidoc-crm/E55_Type> .
        <http://vocab.getty.edu/aat/300055647> <http://www.w3.org/2000/01/rdf-schema#label> "width" .
        <http://vocab.getty.edu/aat/300265863> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.cidoc-crm.org/cidoc-crm/E55_Type> .
        <http://vocab.getty.edu/aat/300265863> <http://www.w3.org/2000/01/rdf-schema#label> "file size" .
        <http://vocab.getty.edu/aat/300265869> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.cidoc-crm.org/cidoc-crm/E58_Measurement_Unit> .
        <http://vocab.getty.edu/aat/300265869> <http://www.w3.org/2000/01/rdf-schema#label> "bytes" .
        <http://vocab.getty.edu/aat/300266190> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.cidoc-crm.org/cidoc-crm/E58_Measurement_Unit> .
        <http://vocab.getty.edu/aat/300266190> <http://www.w3.org/2000/01/rdf-schema#label> "pixels" .
        """

        g.parse(data=unit_nt, format="nt")

        aatrefs = {
            "pixels": URIRef("http://vocab.getty.edu/aat/300266190"),
            "bytes": URIRef("http://vocab.getty.edu/aat/300265869"),
            "height": URIRef("http://vocab.getty.edu/aat/300055644"),
            "width": URIRef("http://vocab.getty.edu/aat/300055647"),
            "file size": URIRef("http://vocab.getty.edu/aat/300265863"),
        }

        def add_dimension(graphobj, domain_uri, unittype, unit, value):
            dim_node = BNode()
            graphobj.add((domain_uri, cidoc_nm["P43_has_dimension"], dim_node))
            graphobj.add((dim_node, RDF.type, cidoc_nm["E54_Dimension"]))
            graphobj.add((dim_node, cidoc_nm["P2_has_type"], aatrefs[unittype]))
            graphobj.add((dim_node, cidoc_nm["P91_has_unit"], aatrefs[unit]))
            graphobj.add((dim_node, RDF.value, Literal(value)))

        for f_data in edge_info["range_tile_data"]:
            # f_data will be something like:
            # "{\"accepted\": true, \"content\": \"blob:http://localhost/cccadfd0-64fc-104a-8157-3c96aca0b9bd\",
            # \"file_id\": \"f4cd6596-cd75-11e8-85e0-0242ac1b0003\", \"height\": 307, \"index\": 0,
            # \"lastModified\": 1535067185606, \"name\": \"FUjJqP6.jpg\", \"size\": 19350,
            # \"status\": \"uploaded\", \"type\": \"image/jpeg\", \"url\": \"/files/uploadedfiles/FUjJqP6.jpg\",
            # \"width\": 503}"

            # range URI should be the file URL/URI, and the rest of the details should hang off that
            # FIXME - (Poor) assumption that file is on same host as Arches instance host config.
            if f_data["url"].startswith("/"):
                f_uri = URIRef(archesproject[f_data["url"][1:]])
            else:
                f_uri = URIRef(archesproject[f_data["url"]])
            g.add((edge_info["d_uri"], URIRef(edge.ontologyproperty), f_uri))
            g.add((f_uri, RDF.type, URIRef(edge.rangenode.ontologyclass)))
            g.add((f_uri, DC["format"], Literal(f_data["type"])))
            g.add((f_uri, RDFS.label, Literal(f_data["name"])))

            # FIXME - improve this ms in timestamp handling code in case of odd OS environments
            # FIXME - Use the timezone settings for export?
            if f_data["lastModified"]:
                lm = f_data["lastModified"]
                if lm > 9999999999:  # not a straight timestamp, but includes milliseconds
                    lm = f_data["lastModified"] / 1000
                g.add((f_uri, DCTERMS.modified, Literal(datetime.utcfromtimestamp(lm).isoformat())))

            if "size" in f_data:
                add_dimension(g, f_uri, "file size", "bytes", f_data["size"])
            if "height" in f_data:
                add_dimension(g, f_uri, "height", "pixels", f_data["height"])
            if "width" in f_data:
                add_dimension(g, f_uri, "width", "pixels", f_data["width"])

        return g

    def from_rdf(self, json_ld_node):
        # Currently up in the air about how best to do file imports via JSON-LD
        pass

    def process_mobile_data(self, tile, node, db, couch_doc, node_value):
        """
        Takes a tile, couch db instance, couch record, and the node value from
        a provisional edit. Creates a django instance, saves the corresponding
        attachement as a file, updates the provisional edit value with the
        file location information and returns the revised provisional edit value
        """

        try:
            for file in node_value:
                attachment = db.get_attachment(couch_doc["_id"], file["file_id"])
                if attachment is not None:
                    attachment_file = attachment.read()
                    file_data = ContentFile(attachment_file, name=file["name"])
                    file_model, created = models.File.objects.get_or_create(fileid=file["file_id"])

                    if created:
                        file_model.path = file_data

                    file_model.tile = tile
                    file_model.save()
                    if file["name"] == file_data.name and "url" not in list(file.keys()):
                        file["file_id"] = str(file_model.pk)
                        file["url"] = str(file_model.path.url)
                        file["status"] = "uploaded"
                        file["accepted"] = True
                        file["size"] = file_data.size

        except KeyError as e:
            pass
        return node_value

    def collects_multiple_values(self):
        return True

    def default_es_mapping(self):
        return {
            "properties": {
                "file_id": {"type": "text", "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}}},
                "name": {"type": "text", "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}}},
                "type": {"type": "text", "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}}},
                "url": {"type": "text", "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}}},
                "status": {"type": "text", "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}}},
            }
        }


class BaseDomainDataType(BaseDataType):
    def get_option_text(self, node, option_id):
        for option in node.config["options"]:
            if option["id"] == option_id:
                return option["text"]
        return ""

    def get_option_id_from_text(self, value):
        # this could be better written with most of the logic in SQL tbh
        for dnode in models.Node.objects.filter(config__contains={"options": [{"text": value}]}):
            for option in dnode.config["options"]:
                if option["text"] == value:
                    yield option["id"], dnode.nodeid

    def is_a_literal_in_rdf(self):
        return True


class DomainDataType(BaseDomainDataType):
    def validate(self, value, row_number=None, source="", node=None, nodeid=None):
        errors = []
        key = "id"
        if value is not None:
            try:
                uuid.UUID(str(value))
            except ValueError as e:
                key = "text"

            domain_val_node_query = models.Node.objects.filter(config__contains={"options": [{key: value}]})

            if len(domain_val_node_query) != 1:
                row_number = row_number if row_number else ""
                if len(domain_val_node_query) == 0:
                    message = _("Invalid domain id. Please check the node this value is mapped to for a list of valid domain ids.")
                    error_message = self.create_error_message(value, source, row_number, message)
                    errors.append(error_message)
        return errors

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        node = models.Node.objects.get(nodeid=nodeid)
        domain_text = self.get_option_text(node, nodevalue)
        if domain_text is not None:
            if settings.WORDS_PER_SEARCH_TERM is None or (len(domain_text.split(" ")) < settings.WORDS_PER_SEARCH_TERM):
                terms.append(domain_text)
        return terms

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        domain_text = None
        for tile in document["tiles"]:
            for k, v in tile.data.items():
                if v == nodevalue:
                    node = models.Node.objects.get(nodeid=k)
                    domain_text = self.get_option_text(node, v)

        if domain_text not in document["strings"] and domain_text is not None:
            document["strings"].append({"string": domain_text, "nodegroup_id": tile.nodegroup_id, "provisional": provisional})

    def get_display_value(self, tile, node):
        data = self.get_tile_data(tile)
        return self.get_option_text(node, data[str(node.nodeid)])

    def transform_export_values(self, value, *args, **kwargs):
        ret = ""
        if (
            kwargs["concept_export_value_type"] is None
            or kwargs["concept_export_value_type"] == ""
            or kwargs["concept_export_value_type"] == "label"
        ):
            ret = self.get_option_text(models.Node.objects.get(nodeid=kwargs["node"]), value)
        elif kwargs["concept_export_value_type"] == "both":
            ret = value + "|" + self.get_option_text(models.Node.objects.get(nodeid=kwargs["node"]), value)
        elif kwargs["concept_export_value_type"] == "id":
            ret = value
        return ret

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "":
                search_query = Match(field="tiles.data.%s" % (str(node.pk)), type="phrase", query=value["val"])
                if "!" in value["op"]:
                    query.must_not(search_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(search_query)

        except KeyError as e:
            pass

    def to_rdf(self, edge_info, edge):
        # returns an in-memory graph object, containing the domain resource, its
        # type and the number as a numeric literal (as this is how it is in the JSON)
        g = Graph()
        if edge_info["range_tile_data"] is not None:
            g.add((edge_info["d_uri"], RDF.type, URIRef(edge.domainnode.ontologyclass)))
            g.add(
                (
                    edge_info["d_uri"],
                    URIRef(edge.ontologyproperty),
                    Literal(self.get_option_text(edge.rangenode, edge_info["range_tile_data"])),
                )
            )
        return g

    def from_rdf(self, json_ld_node):
        # depends on how much is passed to the method
        # if just the 'leaf' node, then not much can be done aside from return the list of nodes it might be from
        # a string may be present in multiple domains for instance
        # via models.Node.objects.filter(config__options__contains=[{"text": value}])
        value = get_value_from_jsonld(json_ld_node)
        try:
            return [str(v_id) for v_id, n_id in self.get_option_id_from_text(value[0])][0]
        except (AttributeError, KeyError, TypeError) as e:
            print(e)


class DomainListDataType(BaseDomainDataType):
    def transform_value_for_tile(self, value, **kwargs):
        if value is not None:
            if not isinstance(value, list):
                value = value.split(",")
        return value

    def validate(self, values, row_number=None, source="", node=None, nodeid=None):
        domainDataType = DomainDataType()
        errors = []
        if values is not None:
            for value in values:
                errors = errors + domainDataType.validate(value, row_number)
        return errors

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        node = models.Node.objects.get(nodeid=nodeid)
        for val in nodevalue:
            domain_text = self.get_option_text(node, val)
            if domain_text is not None:
                if settings.WORDS_PER_SEARCH_TERM is None or (len(domain_text.split(" ")) < settings.WORDS_PER_SEARCH_TERM):
                    terms.append(domain_text)

        return terms

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        domain_text_values = set([])
        for tile in document["tiles"]:
            for k, v in tile.data.items():
                if v == nodevalue:
                    node = models.Node.objects.get(nodeid=k)
                    for value in nodevalue:
                        text_value = self.get_option_text(node, value)
                        domain_text_values.add(text_value)

        for value in domain_text_values:
            if value not in document["strings"]:
                document["strings"].append({"string": value, "nodegroup_id": tile.nodegroup_id, "provisional": provisional})

    def get_display_value(self, tile, node):
        new_values = []
        data = self.get_tile_data(tile)
        if data[str(node.nodeid)] is not None:
            for val in data[str(node.nodeid)]:
                option = self.get_option_text(node, val)
                new_values.append(option)
        return ",".join(new_values)

    def transform_export_values(self, value, *args, **kwargs):
        new_values = []
        for val in value:
            if (
                kwargs["concept_export_value_type"] is None
                or kwargs["concept_export_value_type"] == ""
                or kwargs["concept_export_value_type"] == "label"
            ):
                new_values.append(self.get_option_text(models.Node.objects.get(nodeid=kwargs["node"]), val))
            elif kwargs["concept_export_value_type"] == "both":
                new_values.append(val + "|" + self.get_option_text(models.Node.objects.get(nodeid=kwargs["node"]), val))
            elif kwargs["concept_export_value_type"] == "id":
                new_values.append(val)
        return ",".join(new_values)

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "" and value["val"] != []:
                search_query = Match(field="tiles.data.%s" % (str(node.pk)), type="phrase", query=value["val"])
                if "!" in value["op"]:
                    query.must_not(search_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(search_query)
        except KeyError as e:
            pass

    def to_rdf(self, edge_info, edge):
        g = Graph()
        domtype = DomainDataType()

        for domain_id in edge_info["range_tile_data"]:
            indiv_info = edge_info.copy()
            indiv_info["range_tile_data"] = domain_id
            g += domtype.to_rdf(indiv_info, edge)
        return g

    def from_rdf(self, json_ld_node):
        # returns a list of lists of {domain id, node id}
        domtype = DomainDataType()

        return [domtype.from_rdf(item) for item in json_ld_node]

    def collects_multiple_values(self):
        return True


class ResourceInstanceDataType(BaseDataType):
    """
        tile data comes from the client looking like this:
        {
            "resourceId": "",
            "ontologyProperty": "",
            "inverseOntologyProperty": ""
        }

    """

    def get_id_list(self, nodevalue):
        if not isinstance(nodevalue, list):
            nodevalue = [nodevalue]
        return nodevalue

    def validate(self, value, row_number=None, source="", node=None, nodeid=None):
        errors = []
        if value is not None:
            resourceXresourceIds = self.get_id_list(value)
            for resourceXresourceId in resourceXresourceIds:
                resourceid = resourceXresourceId["resourceId"]
                try:
                    models.ResourceInstance.objects.get(pk=resourceid)
                except ObjectDoesNotExist:
                    message = _(
                        "Resource id: {0} is not in the system. This relationship will be added once resource {0} is loaded.".format(
                            resourceid
                        )
                    )
                    errors.append({"type": "WARNING", "message": message})
        return errors

    def pre_tile_save(self, tile, nodeid):
        tiledata = tile.data[str(nodeid)]
        # Ensure tiledata is a list (with JSON-LD import it comes in as an object)
        if type(tiledata) != list and tiledata is not None:
            tiledata = [tiledata]
        if tiledata is None or tiledata == []:
            # resource relationship has been removed
            try:
                for rr in models.ResourceXResource.objects.filter(tileid_id=tile.pk, nodeid_id=nodeid):
                    rr.delete()
            except:
                pass
        else:

            resourceXresourceSaved = set()
            for related_resource in tiledata:
                resourceXresourceId = (
                    None
                    if ("resourceXresourceId" not in related_resource or related_resource["resourceXresourceId"] == "")
                    else related_resource["resourceXresourceId"]
                )
                defaults = {
                    "resourceinstanceidfrom_id": tile.resourceinstance_id,
                    "resourceinstanceidto_id": related_resource["resourceId"],
                    "notes": "",
                    "relationshiptype": related_resource["ontologyProperty"],
                    "inverserelationshiptype": related_resource["inverseOntologyProperty"],
                    "tileid_id": tile.pk,
                    "nodeid_id": nodeid,
                }
                if related_resource["ontologyProperty"] == "" or related_resource["inverseOntologyProperty"] == "":
                    if models.ResourceInstance.objects.filter(pk=related_resource["resourceId"]).exists():
                        target_graphid = str(models.ResourceInstance.objects.get(pk=related_resource["resourceId"]).graph_id)
                        for graph in models.Node.objects.get(pk=nodeid).config["graphs"]:
                            if graph["graphid"] == target_graphid:
                                if related_resource["ontologyProperty"] == "":
                                    try:
                                        defaults["relationshiptype"] = graph["ontologyProperty"]
                                    except:
                                        pass
                                if related_resource["inverseOntologyProperty"] == "":
                                    try:
                                        defaults["inverserelationshiptype"] = graph["inverseOntologyProperty"]
                                    except:
                                        pass
                try:
                    rr = models.ResourceXResource.objects.get(pk=resourceXresourceId)
                    for key, value in defaults.items():
                        setattr(rr, key, value)
                    rr.save()
                except models.ResourceXResource.DoesNotExist:
                    rr = models.ResourceXResource(**defaults)
                    rr.save()
                related_resource["resourceXresourceId"] = str(rr.pk)
                resourceXresourceSaved.add(rr.pk)

            # get a list of all resourceXresources with the same tile and node
            # if there are any ids in that list that aren't in the resourceXresourceSaved
            # then those need to be removed from the db
            resourceXresourceInDb = set(
                models.ResourceXResource.objects.filter(tileid_id=tile.pk, nodeid_id=nodeid).values_list("pk", flat=True)
            )
            to_delete = resourceXresourceInDb - resourceXresourceSaved
            for rr in models.ResourceXResource.objects.filter(pk__in=to_delete):
                rr.delete()

    def post_tile_delete(self, tile, nodeid, index=True):
        if tile.data and tile.data[nodeid] and index:
            for related in tile.data[nodeid]:
                se.delete(index=RESOURCE_RELATIONS_INDEX, id=related["resourceXresourceId"])

    def get_display_value(self, tile, node):
        from arches.app.models.resource import Resource  # import here rather than top to avoid circular import

        resourceid = None
        data = self.get_tile_data(tile)
        nodevalue = self.get_id_list(data[str(node.nodeid)])

        items = []
        for resourceXresource in nodevalue:
            try:
                resourceid = resourceXresource["resourceId"]
                related_resource = Resource.objects.get(pk=resourceid)
                displayname = related_resource.displayname
                if displayname is not None:
                    items.append(displayname)
            except (TypeError, KeyError):
                pass
            except:
                logger.info(f'Resource with id "{resourceid}" not in the system.')
        return ", ".join(items)

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        if type(nodevalue) != list and nodevalue is not None:
            nodevalue = [nodevalue]
        if nodevalue:
            for relatedResourceItem in nodevalue:
                document["ids"].append(
                    {"id": relatedResourceItem["resourceId"], "nodegroup_id": tile.nodegroup_id, "provisional": provisional}
                )
                if "resourceName" in relatedResourceItem and relatedResourceItem["resourceName"] not in document["strings"]:
                    document["strings"].append(
                        {"string": relatedResourceItem["resourceName"], "nodegroup_id": tile.nodegroup_id, "provisional": provisional}
                    )

    def transform_value_for_tile(self, value, **kwargs):
        try:
            return json.loads(value)
        except ValueError:
            # do this if json (invalid) is formatted with single quotes, re #6390
            return ast.literal_eval(value)
        except TypeError:
            # data should come in as json but python list is accepted as well
            if isinstance(value, list):
                return value


    def transform_export_values(self, value, *args, **kwargs):
        return json.dumps(value)

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "" and value["val"] != []:
                # search_query = Match(field="tiles.data.%s.resourceId" % (str(node.pk)), type="phrase", query=value["val"])
                search_query = Terms(field="tiles.data.%s.resourceId.keyword" % (str(node.pk)), terms=value["val"])
                if "!" in value["op"]:
                    query.must_not(search_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(search_query)
        except KeyError as e:
            pass

    def get_rdf_uri(self, node, data, which="r"):
        if not data:
            return URIRef("")
        elif type(data) == list:
            return [URIRef(archesproject[f"resources/{x['resourceId']}"]) for x in data]
        return URIRef(archesproject[f"resources/{data['resourceId']}"])

    def accepts_rdf_uri(self, uri):
        return uri.startswith("urn:uuid:") or uri.startswith(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT + "resources/")

    def to_rdf(self, edge_info, edge):
        g = Graph()

        def _add_resource(d, p, r, r_type):
            if r_type is not None:
                g.add((r, RDF.type, URIRef(r_type)))
            g.add((d, URIRef(p), r))

        if edge_info["range_tile_data"] is not None:
            res_insts = edge_info["range_tile_data"]
            if not isinstance(res_insts, list):
                res_insts = [res_insts]

            for res_inst in res_insts:
                rangenode = self.get_rdf_uri(None, res_inst)
                try:
                    res_inst_obj = models.ResourceInstance.objects.get(pk=res_inst["resourceId"])
                    r_type = res_inst_obj.graph.node_set.get(istopnode=True).ontologyclass
                except models.ResourceInstance.DoesNotExist:
                    # This should never happen excpet if trying to export when the
                    # referenced resource hasn't been saved to the database yet
                    r_type = edge.rangenode.ontologyclass
                _add_resource(edge_info["d_uri"], edge.ontologyproperty, rangenode, r_type)
        return g

    def from_rdf(self, json_ld_node):
        res_inst_uri = json_ld_node["@id"]
        # `id` should be in the form schema:{...}/{UUID}
        # eg `urn:uuid:{UUID}`
        #    `http://arches_instance.getty.edu/resources/{UUID}`
        p = re.compile(r"(?P<r>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/?$")
        m = p.search(res_inst_uri)
        if m is not None:
            # return m.groupdict()["r"]
            return [{"resourceId": m.groupdict()["r"], "ontologyProperty": "", "inverseOntologyProperty": "", "resourceXresourceId": ""}]

    def ignore_keys(self):
        return ["http://www.w3.org/2000/01/rdf-schema#label http://www.w3.org/2000/01/rdf-schema#Literal"]

    def references_resource_type(self):
        """
        This resource references another resource type (eg resource-instance-datatype, etc...)
        """

        return True

    def default_es_mapping(self):
        mapping = {
            "properties": {
                "resourceId": {"type": "text", "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}}},
                "ontologyProperty": {"type": "text", "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}}},
                "inverseOntologyProperty": {"type": "text", "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}}},
                "resourceXresourceId": {"type": "text", "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}}},
            }
        }
        return mapping


class ResourceInstanceListDataType(ResourceInstanceDataType):

    def collects_multiple_values(self):
        return True


class NodeValueDataType(BaseDataType):
    def validate(self, value, row_number=None, source="", node=None, nodeid=None):
        errors = []
        if value:
            try:
                models.TileModel.objects.get(tileid=value)
            except ObjectDoesNotExist:
                errors.append({"type": "ERROR", "message": f"{value} {row_number} is not a valid tile id. This data was not imported."})
        return errors

    def get_display_value(self, tile, node):
        datatype_factory = DataTypeFactory()
        value_node = models.Node.objects.get(nodeid=node.config["nodeid"])
        data = self.get_tile_data(tile)
        tileid = data[str(node.pk)]
        if tileid:
            value_tile = models.TileModel.objects.get(tileid=tileid)
            datatype = datatype_factory.get_instance(value_node.datatype)
            return datatype.get_display_value(value_tile, value_node)
        return ""

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        pass

    def append_search_filters(self, value, node, query, request):
        pass


class AnnotationDataType(BaseDataType):
    def validate(self, value, source=None, node=None):
        errors = []
        return errors

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        # document["strings"].append({"string": nodevalue["address"], "nodegroup_id": tile.nodegroup_id})
        return

    def get_search_terms(self, nodevalue, nodeid=None):
        # return [nodevalue["address"]]
        return []

    def default_es_mapping(self):
        # let ES dyanamically map this datatype
        return


def get_value_from_jsonld(json_ld_node):
    try:
        return (json_ld_node[0].get("@value"), json_ld_node[0].get("@language"))
    except KeyError as e:
        try:
            return (json_ld_node.get("@value"), json_ld_node.get("@language"))
        except AttributeError as e:
            return
    except IndexError as e:
        return
