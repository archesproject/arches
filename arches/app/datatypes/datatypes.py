import copy
import uuid
import json
import decimal
from arches.app.datatypes.core.util import get_value_from_jsonld
from arches.app.utils.file_validator import FileValidator
import filetype
import base64
import re
import logging
import os
from pathlib import Path
import ast
import time
from datetime import date, datetime
from mimetypes import MimeTypes

from django.core.files.images import get_image_dimensions
from django.db.models import fields

from arches.app.const import ExtensionType
from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from arches.app.models.concept import get_preflabel_from_valueid
from arches.app.models.system_settings import settings
from arches.app.models.fields.i18n import I18n_JSONField, I18n_String
from arches.app.utils.date_utils import ExtendedDateFormat
from arches.app.utils.module_importer import get_class_from_modulename
from arches.app.utils.permission_backend import user_is_resource_reviewer
from arches.app.utils.geo_utils import GeoUtils
from arches.app.utils.i18n import get_localized_value
from arches.app.utils.string_utils import str_to_bool
from arches.app.search.elasticsearch_dsl_builder import (
    Bool,
    Dsl,
    Exists,
    Match,
    Query,
    Range,
    RangeDSLException,
    Term,
    Terms,
    Wildcard,
    Prefix,
    Nested,
)
from arches.app.search.search_engine_factory import SearchEngineInstance as se
from arches.app.search.search_term import SearchTerm
from arches.app.search.mappings import RESOURCES_INDEX
from django.core.cache import cache
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from django.utils.translation import get_language, gettext as _

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

# One benefit of shifting to python3.x would be to use
# importlib.util.LazyLoader to load rdflib (and other lesser
# used but memory soaking libs)
from rdflib import Namespace, URIRef, Literal, BNode
from rdflib import ConjunctiveGraph as Graph
from rdflib.namespace import RDF, RDFS, XSD, DC, DCTERMS

# do not delete, used by module importer
from .core import *

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
            DataTypeFactory._datatypes = {
                datatype.datatype: datatype
                for datatype in models.DDataType.objects.all()
            }
        self.datatypes = DataTypeFactory._datatypes
        self.datatype_instances = DataTypeFactory._datatype_instances

    def get_instance(self, datatype):
        try:
            d_datatype = DataTypeFactory._datatypes[datatype]
        except KeyError:
            DataTypeFactory._datatypes = {
                datatype.datatype: datatype
                for datatype in models.DDataType.objects.all()
            }
            d_datatype = DataTypeFactory._datatypes[datatype]
            self.datatypes = DataTypeFactory._datatypes
        try:
            datatype_instance = DataTypeFactory._datatype_instances[
                d_datatype.classname
            ]
        except KeyError:
            class_method = get_class_from_modulename(
                d_datatype.modulename, d_datatype.classname, ExtensionType.DATATYPES
            )
            datatype_instance = class_method(d_datatype)
            DataTypeFactory._datatype_instances[d_datatype.classname] = (
                datatype_instance
            )
            self.datatype_instances = DataTypeFactory._datatype_instances
        return datatype_instance


class StringDataType(BaseDataType):
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
        try:
            if value is not None:
                for key in value.keys():
                    isinstance(value[key]["value"], str)
                    isinstance(value[key]["direction"], str)
        except:
            message = _("This is not a string")
            title = _("Invalid String Format")
            error_message = self.create_error_message(
                value, source, row_number, message, title
            )
            errors.append(error_message)
        return errors

    def rdf_transform(self, value):
        default_language = models.Language.objects.get(code=get_language())
        incoming_value = {}
        for val in value:
            if ("language" in val and val["language"] is not None) or (
                "@language" in val and val["@language"] is not None
            ):
                try:
                    language_code = (
                        val["language"] if "language" in val else val["@language"]
                    )
                    language = models.Language.objects.get(code=language_code)
                    incoming_value = {
                        **incoming_value,
                        language.code: {
                            "value": val["value"] if "value" in val else val["@value"],
                            "direction": language.default_direction,
                        },
                    }
                except models.Language.DoesNotExist:
                    ValueError(
                        "Language does not exist in Language table - cannot create string."
                    )
            else:
                incoming_value = {
                    **incoming_value,
                    default_language.code: {
                        "value": val["value"] if "value" in val else val["@value"],
                        "direction": default_language.default_direction,
                    },
                }

        return incoming_value if len(incoming_value.keys()) > 0 else None

    def validate_from_rdf(self, value):
        transformed_value = None
        if isinstance(value, list):
            transformed_value = self.rdf_transform(value)
        elif isinstance(value, str):
            transformed_value = self.rdf_transform([{"value": value}])
        incoming_value = value if transformed_value is None else transformed_value

        return self.validate(incoming_value)

    def clean(self, tile, nodeid):
        if tile.data[nodeid] in ["", "''"]:
            tile.data[nodeid] = None
        elif isinstance(tile.data[nodeid], dict):
            for language_dict in tile.data[nodeid].values():
                if language_dict["value"]:
                    break
            else:
                # No non-empty value was found.
                tile.data[nodeid] = None

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        if nodevalue is not None:
            for key in nodevalue.keys():
                val = {
                    "string": nodevalue[key]["value"],
                    "language": key,
                    "nodegroup_id": tile.nodegroup_id,
                    "provisional": provisional,
                }
                document["strings"].append(val)

    def transform_export_values(self, value, *args, **kwargs):
        language = kwargs.pop("language", None)
        if value is not None:
            try:
                if language is not None:
                    return value[language]["value"]
                else:
                    return value[get_language()]["value"]
            except KeyError:
                # sometimes certain requested language values aren't populated.  Just pass back with implicit None.
                pass

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []

        if nodevalue is not None and isinstance(nodevalue, dict):
            for key in nodevalue.keys():
                try:
                    if settings.WORDS_PER_SEARCH_TERM is None or (
                        len(nodevalue[key]["value"].split(" "))
                        < settings.WORDS_PER_SEARCH_TERM
                    ):
                        terms.append(
                            SearchTerm(value=nodevalue[key]["value"], lang=key)
                        )
                except:
                    pass
        return terms

    def append_null_search_filters(self, value, node, query, request):
        """
        Appends the search query dsl to search for fields that have not been populated or are empty strings
        """

        query.filter(Terms(field="graph_id", terms=[str(node.graph_id)]))

        data_exists_query = Exists(
            field=f"tiles.data.{str(node.pk)}.{value['lang']}.value"
        )
        tiles_w_node_exists = Nested(path="tiles", query=data_exists_query)

        if value["op"] == "not_null":
            query.must(tiles_w_node_exists)
            non_blank_string_query = Wildcard(
                field=f"tiles.data.{str(node.pk)}.{value['lang']}.value", query="?*"
            )
            query.must(Nested(path="tiles", query=non_blank_string_query))

        elif value["op"] == "null":
            # search for tiles that don't exist
            not_exists_query = Bool()
            not_exists_query.must_not(tiles_w_node_exists)
            query.should(not_exists_query)

            # search for tiles that do exist, but have empty strings
            non_blank_string_query = Term(
                field=f"tiles.data.{str(node.pk)}.{value['lang']}.value.keyword",
                query="",
            )
            query.should(Nested(path="tiles", query=non_blank_string_query))

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "":
                exact_terms = re.search('"(?P<search_string>.*)"', value["val"])
                if exact_terms:
                    if "~" in value["op"]:
                        match_query = Wildcard(
                            field="tiles.data.%s.%s.value.keyword"
                            % (str(node.pk), value["lang"]),
                            query=f"*{exact_terms.group('search_string')}*",
                            case_insensitive=False,
                        )
                    else:  # "eq" in value["op"]
                        match_query = Match(
                            field="tiles.data.%s.%s.value.keyword"
                            % (str(node.pk), value["lang"]),
                            query=exact_terms.group("search_string"),
                            type="phrase",
                        )
                elif "?" in value["val"] or "*" in value["val"]:
                    match_query = Wildcard(
                        field="tiles.data.%s.%s.value.keyword"
                        % (str(node.pk), value["lang"]),
                        query=value["val"],
                    )
                else:
                    if "~" in value["op"]:
                        match_query = Bool()
                        for word in value["val"].split(" "):
                            match_query.must(
                                Prefix(
                                    field="tiles.data.%s.%s.value"
                                    % (str(node.pk), value["lang"]),
                                    query=word,
                                )
                            )
                    else:  # "eq" in value["op"]
                        match_query = Match(
                            field="tiles.data.%s.%s.value"
                            % (str(node.pk), value["lang"]),
                            query=value["val"],
                            type="phrase",
                        )

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
            for key in edge_info["range_tile_data"].keys():
                if edge_info["range_tile_data"][key]["value"]:
                    g.add(
                        (
                            edge_info["d_uri"],
                            URIRef(edge.ontologyproperty),
                            Literal(
                                edge_info["range_tile_data"][key]["value"], lang=key
                            ),
                        )
                    )
        return g

    def transform_value_for_tile(self, value, **kwargs):
        language = None
        try:
            regex = re.compile(r"(.+)\|([A-Za-z-]+)$", flags=re.DOTALL | re.MULTILINE)
            match = regex.match(value)
            if match is not None:
                language = match.groups()[1]
                value = match.groups()[0]
        except Exception as e:
            pass

        try:
            parsed_value = json.loads(value)
        except Exception:
            try:
                parsed_value = ast.literal_eval(value)
            except Exception:
                parsed_value = value

        try:
            parsed_value.keys()
            return parsed_value
        except AttributeError:
            if language is not None:
                language_objects = list(models.Language.objects.filter(code=language))
                if len(language_objects) > 0:
                    return {
                        language: {
                            "value": value,
                            "direction": language_objects[0].default_direction,
                        }
                    }

            return {get_language(): {"value": value, "direction": "ltr"}}

    def from_rdf(self, json_ld_node):
        transformed_value = None
        if isinstance(json_ld_node, list):
            transformed_value = self.rdf_transform(json_ld_node)
        else:
            new_value = get_value_from_jsonld(json_ld_node)
            if new_value is not None:
                transformed_value = self.rdf_transform(
                    [{"value": new_value[0], "language": new_value[1]}]
                )
        return transformed_value

    def get_display_value(self, tile, node, **kwargs):
        data = self.get_tile_data(tile)
        requested_language = kwargs.pop("language", None)
        current_language = requested_language or get_language()
        if not current_language:
            current_language = settings.LANGUAGE_CODE
        if data:
            raw_value = data.get(str(node.nodeid))
            if raw_value is not None:
                try:
                    return raw_value[current_language]["value"]
                except KeyError:
                    pass

    def default_es_mapping(self):
        """
        Default mapping if not specified is a text field
        """
        # languages = models.Language.objects.all()
        # lang_mapping = {"properties": {"value": {"type": "text", "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}}}}}
        # for lang in languages:
        #     text_mapping = {"properties": {lang.code: lang_mapping}}
        text_mapping = {"properties": {}}
        return text_mapping

    def get_default_language_value_from_localized_node(self, tile, nodeid):
        return tile.data[str(nodeid)][settings.LANGUAGE_CODE]["value"]

    def is_multilingual_rdf(self, rdf):
        if len(rdf) > 1 and len(set(val["language"] for val in rdf)) > 1:
            return True
        else:
            return False

    def has_multicolumn_data(self):
        return True

    def get_column_header(self, node, **kwargs):
        """
        Returns a CSV column header or headers for a given node ID of this type
        """
        language_codes = kwargs.pop("language_codes")
        return [
            "{column} ({code})".format(column=node["file_field_name"], code=code)
            for code in language_codes
        ]

    def to_json(self, tile, node):
        data = self.get_tile_data(tile)
        if data:
            return self.compile_json(tile, node, **data.get(str(node.nodeid)))

    def pre_structure_tile_data(self, tile, nodeid, **kwargs):
        all_language_codes = {lang.code for lang in kwargs["languages"]}
        direction_lookup = {
            lang.code: lang.default_direction for lang in kwargs["languages"]
        }
        if tile.data[nodeid] is None:
            tile.data[nodeid] = {}
        tile_language_codes = set(tile.data[nodeid].keys())
        for code in all_language_codes - tile_language_codes:
            tile.data[nodeid][code] = {"value": "", "direction": direction_lookup[code]}


class NumberDataType(BaseDataType):
    def validate(
        self,
        value,
        row_number=None,
        source="",
        node=None,
        nodeid=None,
        strict=False,
        **kwargs,
    ):
        errors = []

        try:
            if value == "":
                value = None
            if value is not None:
                decimal.Decimal(value)
        except Exception:
            dt = self.datatype_model.datatype
            message = _("Not a properly formatted number")
            title = _("Invalid Number Format")
            error_message = self.create_error_message(
                value, source, row_number, message, title
            )
            errors.append(error_message)
        return errors

    def get_display_value(self, tile, node, **kwargs):
        data = self.get_tile_data(tile)
        if data:
            display_value = data.get(str(node.nodeid))
            if display_value is not None:
                return str(display_value)

    def transform_value_for_tile(self, value, **kwargs):
        try:
            if value == "":
                value = None
            elif value.isdigit():
                value = int(value)
            else:
                value = float(value)
        except (AttributeError, ValueError):
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
        document["numbers"].append(
            {
                "number": nodevalue,
                "nodegroup_id": tile.nodegroup_id,
                "provisional": provisional,
            }
        )

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
                search_query = Range(
                    field="tiles.data.%s" % (str(node.pk)), **operators
                )
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
            if type(edge_info["range_tile_data"]) == float
            and edge_info["range_tile_data"].is_integer()
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
    def validate(
        self,
        value,
        row_number=None,
        source="",
        node=None,
        nodeid=None,
        strict=False,
        **kwargs,
    ):
        errors = []
        try:
            if value is not None:
                str_to_bool(str(value))
        except ValueError:
            message = _("Not of type boolean")
            title = _("Invalid Boolean")
            error_message = self.create_error_message(
                value, source, row_number, message, title
            )
            errors.append(error_message)

        return errors

    def get_display_value(self, tile, node, **kwargs):
        data = self.get_tile_data(tile)
        if data:
            raw_value = data.get(str(node.nodeid))
            if raw_value is not None:
                return str(raw_value)

        # TODO: When APIv1 is retired, replace the body of get_display_value with the following
        # data = self.get_tile_data(tile)

        # if data:
        #     trueDisplay = node.config["trueLabel"]
        #     falseDisplay = node.config["falseLabel"]
        #     raw_value = data.get(str(node.nodeid))
        #     if raw_value is not None:
        #         return trueDisplay if raw_value else falseDisplay

    def to_json(self, tile, node):
        """
        Returns a value for display in a json object
        """

        data = self.get_tile_data(tile)
        if data:
            value = data.get(str(node.nodeid))
            label = (
                node.config["trueLabel"] if value is True else node.config["falseLabel"]
            )
            return self.compile_json(tile, node, display_value=label, value=value)

    def transform_value_for_tile(self, value, **kwargs):
        return str_to_bool(str(value))

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
            g.add(
                (
                    edge_info["d_uri"],
                    URIRef(edge.ontologyproperty),
                    Literal(edge_info["range_tile_data"]),
                )
            )
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
    def validate(
        self,
        value,
        row_number=None,
        source="",
        node=None,
        nodeid=None,
        strict=False,
        **kwargs,
    ):
        errors = []
        if value is not None:
            valid_date_format, valid = self.get_valid_date_format(value)
            if valid is False:
                message = _(
                    "Incorrect format. Confirm format is in settings.DATE_FORMATS or set the format in settings.DATE_IMPORT_EXPORT_FORMAT."
                )
                title = _("Invalid Date Format")
                error_message = self.create_error_message(
                    value, source, row_number, message, title
                )
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

    def set_timezone(self, value):
        try:
            value = value.astimezone()
        except:
            # The .astimezone function throws an error on Windows for dates before 1970
            value = self.backup_astimezone(value)
        return value.isoformat(timespec="milliseconds")

    def transform_value_for_tile(self, value, **kwargs):
        value = None if value == "" else value
        if value is not None:
            if isinstance(value, list):
                value = value[0]
            if isinstance(value, str):
                if len(value) < 4 and not value.startswith("-"):
                    # a year before 1000 but not BCE
                    value = value.zfill(4)
                valid_date_format, valid = self.get_valid_date_format(value)
                if valid:
                    value = datetime.strptime(value, valid_date_format)
                else:
                    value = datetime.strptime(value, settings.DATE_IMPORT_EXPORT_FORMAT)
            if isinstance(value, date):
                value = datetime(value.year, value.month, value.day)

        return self.set_timezone(value)

    def backup_astimezone(self, dt):
        def same_calendar(year):
            new_year = 1971
            while not is_same_calendar(year, new_year):
                new_year += 1
                # should never happen but don't want a infinite loop
                if new_year > 2020:  # pragma: no cover
                    msg = "Backup timezone conversion failed: no matching year found"
                    raise Exception(msg)
            return new_year

        def is_same_calendar(year1, year2):
            year1_weekday_1 = datetime.strptime(
                str(year1) + "-01-01", "%Y-%m-%d"
            ).weekday()
            year1_weekday_2 = datetime.strptime(
                str(year1) + "-03-01", "%Y-%m-%d"
            ).weekday()
            year2_weekday_1 = datetime.strptime(
                str(year2) + "-01-01", "%Y-%m-%d"
            ).weekday()
            year2_weekday_2 = datetime.strptime(
                str(year2) + "-03-01", "%Y-%m-%d"
            ).weekday()
            return (year1_weekday_1 == year2_weekday_1) and (
                year1_weekday_2 == year2_weekday_2
            )

        converted_dt = (
            dt.replace(year=same_calendar(dt.year)).astimezone().replace(year=dt.year)
        )
        return converted_dt

    def transform_export_values(self, value, *args, **kwargs):
        valid_date_format, valid = self.get_valid_date_format(value)
        if valid:
            value = datetime.strptime(value, valid_date_format).strftime(
                settings.DATE_IMPORT_EXPORT_FORMAT
            )
        else:
            logger.warning(_("{value} is an invalid date format").format(**locals()))
        return value

    def add_missing_colon_to_timezone(self, value):
        """
        Python will parse a timezone with a colon (-07:00) but will not add a colon to a timezone using strftime.
        Elastic will not index a time with a timezone without a colon, so this method ensures the colon is added
        if it is missing.
        """

        format = self.get_valid_date_format(value)[0]
        if format.endswith("z") and value[-5] in ("-", "+"):
            return "{0}:{1}".format(value[:-2], value[-2:])
        else:
            return value

    def pre_tile_save(self, tile, nodeid):
        if tile.data[nodeid]:
            tile.data[nodeid] = self.add_missing_colon_to_timezone(tile.data[nodeid])

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        document["dates"].append(
            {
                "date": ExtendedDateFormat(nodevalue).lower,
                "nodegroup_id": tile.nodegroup_id,
                "nodeid": nodeid,
                "provisional": provisional,
            }
        )

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "" and value["val"] is not None:
                try:
                    date_value = (
                        datetime.strptime(value["val"], "%Y-%m-%d %H:%M:%S%z")
                        .astimezone()
                        .isoformat()
                    )
                except ValueError:
                    date_value = value["val"]
                if value["op"] != "eq":
                    operators = {"gte": None, "lte": None, "lt": None, "gt": None}
                    operators[value["op"]] = date_value
                else:
                    operators = {"gte": date_value, "lte": date_value}
                search_query = Range(
                    field="tiles.data.%s" % (str(node.pk)), **operators
                )
                query.must(search_query)
        except KeyError:
            pass

    def after_update_all(self, tile=None):
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
            g.add(
                (
                    edge_info["d_uri"],
                    URIRef(edge.ontologyproperty),
                    Literal(edge_info["range_tile_data"], datatype=XSD.dateTime),
                )
            )
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

    def get_display_value(self, tile, node, **kwargs):
        data = self.get_tile_data(tile)
        try:
            og_value = data[str(node.nodeid)]
            valid_date_format, valid = self.get_valid_date_format(og_value)
            new_date_format = settings.DATE_FORMATS["Python"][
                settings.DATE_FORMATS["JavaScript"].index(node.config["dateFormat"])
            ]
            value = datetime.strptime(og_value, valid_date_format).strftime(
                new_date_format
            )
        except TypeError:
            value = data[str(node.nodeid)]
        return value


class EDTFDataType(BaseDataType):
    def transform_value_for_tile(self, value, **kwargs):
        transformed_value = ExtendedDateFormat(value)
        if transformed_value.edtf is None:
            return value
        return str(transformed_value.edtf)

    def pre_tile_save(self, tile, nodeid):
        tile.data[nodeid] = self.transform_value_for_tile(tile.data[nodeid])

    def validate(
        self,
        value,
        row_number=None,
        source="",
        node=None,
        nodeid=None,
        strict=False,
        **kwargs,
    ):
        errors = []
        if value is not None:
            if not ExtendedDateFormat(value).is_valid():
                message = _(
                    "Incorrect Extended Date Time Format. See http://www.loc.gov/standards/datetime/ for supported formats"
                )
                title = _("Invalid EDTF Format")
                error_message = self.create_error_message(
                    value, source, row_number, message, title
                )
                errors.append(error_message)
        return errors

    def get_display_value(self, tile, node, **kwargs):
        data = self.get_tile_data(tile)
        try:
            value = data[str(node.nodeid)]["value"]
        except TypeError:
            value = data[str(node.nodeid)]
        return value

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        def add_date_to_doc(document, edtf):
            if edtf.lower == edtf.upper:
                if edtf.lower is not None:
                    document["dates"].append(
                        {
                            "date": edtf.lower,
                            "nodegroup_id": tile.nodegroup_id,
                            "nodeid": nodeid,
                            "provisional": provisional,
                        }
                    )
            else:
                dr = {}
                if edtf.lower_fuzzy is not None:
                    dr["gte"] = edtf.lower_fuzzy
                    document["dates"].append(
                        {
                            "date": edtf.lower_fuzzy,
                            "nodegroup_id": tile.nodegroup_id,
                            "nodeid": nodeid,
                            "provisional": provisional,
                        }
                    )
                if edtf.upper_fuzzy is not None:
                    dr["lte"] = edtf.upper_fuzzy
                    document["dates"].append(
                        {
                            "date": edtf.upper_fuzzy,
                            "nodegroup_id": tile.nodegroup_id,
                            "nodeid": nodeid,
                            "provisional": provisional,
                        }
                    )
                document["date_ranges"].append(
                    {
                        "date_range": dr,
                        "nodegroup_id": tile.nodegroup_id,
                        "nodeid": nodeid,
                        "provisional": provisional,
                    }
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
            invalid_filter_exception = Exception(
                _(
                    'Only dates that specify an exact year, month, \
                        and day can be used with the "=", ">", "<", ">=", and "<=" operators'
                )
            )

            if value["op"] == "eq":
                if edtf.lower != edtf.upper:
                    raise invalid_filter_exception
                else:
                    operators = {"gte": edtf.lower, "lte": edtf.lower}
                    query.must(
                        Range(
                            field="tiles.data.%s.dates.date" % (str(node.pk)),
                            **operators,
                        )
                    )
            else:
                if value["op"] == "overlaps":
                    operators = {"gte": edtf.lower, "lte": edtf.upper}
                else:
                    if edtf.lower != edtf.upper:
                        raise invalid_filter_exception

                    operators = {value["op"]: edtf.lower or edtf.upper}

                try:
                    group_query = Bool()
                    group_query.should(
                        Range(
                            field="tiles.data.%s.dates.date" % (str(node.pk)),
                            **operators,
                        )
                    )
                    group_query.should(
                        Range(
                            field="tiles.data.%s.date_ranges.date_range"
                            % (str(node.pk)),
                            relation="intersects",
                            **operators,
                        )
                    )
                    query.must(group_query)
                except RangeDSLException:
                    if edtf.lower is None and edtf.upper is None:
                        raise Exception(_("Invalid date specified."))

        if not value.get("op"):
            pass
        elif value["op"] == "null" or value["op"] == "not_null":
            self.append_null_search_filters(value, node, query, request)
        elif value["val"] != "" and value["val"] is not None:
            edtf = ExtendedDateFormat(value["val"])
            if edtf.result_set:
                for result in edtf.result_set:
                    add_date_to_doc(query, result)
            else:
                add_date_to_doc(query, edtf)

    def default_es_mapping(self):
        mapping = {
            "properties": {
                "value": {
                    "type": "text",
                    "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}},
                }
            }
        }
        return mapping


class FileListDataType(BaseDataType):
    def __init__(self, model=None):
        super(FileListDataType, self).__init__(model=model)
        self.node_lookup = {}

    def validate_file_types(self, request=None, nodeid=None):
        errors = []
        validator = FileValidator()
        files = request.FILES.getlist("file-list_" + nodeid, [])
        for file in files:
            errors = errors + validator.validate_file_type(
                file.file, file.name.split(".")[-1]
            )
        return errors

    def validate(
        self,
        value,
        row_number=None,
        source=None,
        node=None,
        nodeid=None,
        strict=False,
        path=None,
        request=None,
        **kwargs,
    ):
        errors = []
        file_type_errors = []
        if request:
            file_type_errors = errors + self.validate_file_types(request, str(node.pk))

        if len(file_type_errors) > 0:
            title = _("Invalid File Type")
            errors.append(
                {
                    "type": "ERROR",
                    "message": _("File type not permitted"),
                    "title": title,
                }
            )

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
            power = 2**10
            n = 0
            power_labels = {0: "", 1: "kilo", 2: "mega", 3: "giga", 4: "tera"}
            while size > power:
                size /= power
                n += 1
            return size, power_labels[n] + "bytes"

        try:
            config = node.config
            limit = config["maxFiles"]
            max_size = config["maxFileSize"] if "maxFileSize" in config.keys() else None

            images_only = config.get("imagesOnly", False)
            if images_only and request:
                for metadata in value:
                    if not any(
                        localizedString["value"]
                        for localizedString in metadata.get("altText", {}).values()
                    ):
                        errors.append(
                            {
                                "type": "ERROR",
                                "title": _("Missing alt text"),
                                "message": _(
                                    "The image '{0}' is missing an alternative text."
                                ).format(metadata["name"]),
                            }
                        )
                files = request.FILES.getlist(f"file-list_{node.nodeid}", [])
                for file in files:
                    width, height = get_image_dimensions(file.file)
                    if not width or not height:
                        title = _("Invalid File Type")
                        errors.append(
                            {
                                "type": "ERROR",
                                "message": _("This node allows only images."),
                                "title": title,
                            }
                        )

            if (
                value is not None
                and config["activateMax"] is True
                and len(value) > limit
            ):
                message = _(
                    "This node has a limit of {0} files. Please reduce files.".format(
                        limit
                    )
                )
                title = _("Exceed Maximun Number of Files")
                errors.append({"type": "ERROR", "message": message, "title": title})

            if max_size is not None:
                formatted_max_size = format_bytes(max_size)
                for v in value:
                    if v["size"] > max_size:
                        message = _(
                            "This node has a file-size limit of {0}. Please reduce file size or contact your sysadmin.".format(
                                formatted_max_size
                            )
                        )
                        title = _("Exceed File Size Limit")
                        errors.append(
                            {"type": "ERROR", "message": message, "title": title}
                        )
            if path:
                for file in value:
                    if not default_storage.exists(os.path.join(path, file["name"])):
                        message = _(
                            'The file "{0}" does not exist in "{1}"'.format(
                                file["name"], path
                            )
                        )
                        title = _("File Not Found")
                        errors.append(
                            {"type": "ERROR", "message": message, "title": title}
                        )
        except Exception as e:
            dt = self.datatype_model.datatype
            message = _("datatype: {0}, value: {1} - {2} .".format(dt, value, e))
            title = _("Unexpected File Error")
            errors.append({"type": "ERROR", "message": message, "title": title})
        return errors

    def clean(self, tile, nodeid):
        super().clean(tile, nodeid)
        if tile.data[nodeid] == []:
            tile.data[nodeid] = None

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        try:
            for f in tile.data[str(nodeid)]:
                val = {
                    "string": f["name"],
                    "nodegroup_id": tile.nodegroup_id,
                    "provisional": provisional,
                }
                document["strings"].append(val)
        except (KeyError, TypeError) as e:
            for k, pe in tile.provisionaledits.items():
                for f in pe["value"][nodeid]:
                    val = {
                        "string": f["name"],
                        "nodegroup_id": tile.nodegroup_id,
                        "provisional": provisional,
                    }
                    document["strings"].append(val)

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "":
                if value["op"] == "gte" or value["op"] == "lte":
                    operators = {"gte": None, "lte": None, "lt": None, "gt": None}
                    operators[value["op"]] = float(value["val"]) * 1000000
                search_query = Range(
                    field="tiles.data.%s.size" % (str(node.pk)), **operators
                )
                query.must(search_query)

        except KeyError as e:
            pass

    def get_search_terms(self, nodevalue, nodeid):
        terms = []
        for file_obj in nodevalue:
            if file_obj["name"] is not None:
                terms.append(SearchTerm(value=file_obj["name"]))

        return terms

    def get_display_value(self, tile, node, **kwargs):
        data = self.get_tile_data(tile)
        files = data[str(node.nodeid)]
        file_urls = ""
        if files is not None:
            file_urls = " | ".join([file["url"] for file in files])

        return file_urls

    def to_json(self, tile, node):
        data = self.get_tile_data(tile)
        if data:
            return self.compile_json(tile, node, file_details=data[str(node.nodeid)])

    def post_tile_save(self, tile, nodeid, request):
        if request is not None:
            # this does not get called when saving data from the mobile app
            previously_saved_tile = models.TileModel.objects.filter(pk=tile.tileid)
            user = request.user
            if hasattr(request.user, "userprofile") is not True:
                models.UserProfile.objects.create(user=request.user)
            user_is_reviewer = user_is_resource_reviewer(request.user)
            current_tile_data = self.get_tile_data(tile)
            if previously_saved_tile.count() == 1:
                previously_saved_tile_data = self.get_tile_data(
                    previously_saved_tile[0]
                )
                if (
                    previously_saved_tile_data
                    and previously_saved_tile_data[nodeid] is not None
                ):
                    for previously_saved_file in previously_saved_tile_data[nodeid]:
                        previously_saved_file_has_been_removed = True
                        for incoming_file in current_tile_data[nodeid]:
                            if (
                                previously_saved_file["file_id"]
                                == incoming_file["file_id"]
                            ):
                                previously_saved_file_has_been_removed = False
                        if previously_saved_file_has_been_removed:
                            try:
                                deleted_file = models.File.objects.get(
                                    pk=previously_saved_file["file_id"]
                                )
                                deleted_file.delete()
                            except models.File.DoesNotExist:
                                logger.exception(_("File does not exist"))

            files = request.FILES.getlist(
                "file-list_" + nodeid + "_preloaded", []
            ) + request.FILES.getlist("file-list_" + nodeid, [])
            tile_exists = models.TileModel.objects.filter(pk=tile.tileid).exists()

            for file_data in files:
                file_model = models.File()
                file_model.path = file_data
                file_model.tile = tile
                if tile_exists:
                    file_model.save()
                if current_tile_data[nodeid] is not None:
                    resave_tile = False
                    updated_file_records = []
                    for file_json in current_tile_data[nodeid]:
                        if (
                            file_json["name"] == file_data.name
                            and file_json["url"] is None
                        ):
                            file_json["file_id"] = str(file_model.pk)
                            file_json["url"] = settings.MEDIA_URL + str(
                                file_model.fileid
                            )
                            file_json["path"] = file_model.path.name
                            file_json["status"] = "uploaded"
                            resave_tile = True
                        updated_file_records.append(file_json)
                    if resave_tile is True:
                        # resaving model to assign url from file_model
                        # importing proxy model errors, so cannot use super on the proxy model to save
                        if previously_saved_tile.count() == 1:
                            tile_to_update = previously_saved_tile[0]
                            if user_is_reviewer:
                                tile_to_update.data[nodeid] = updated_file_records
                            else:
                                tile_to_update.provisionaledits[str(user.id)]["value"][
                                    nodeid
                                ] = updated_file_records
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
                        renderer_class, renderer_type = (
                            renderer_mime[0],
                            renderer_mime[1],
                        )
                        if len(file_mime) == 2:
                            file_class = file_mime[0]
                            if (
                                renderer_class.lower() == file_class.lower()
                                and renderer_type == "*"
                            ):
                                compatible_renderers.append(renderer["id"])
        return compatible_renderers

    def transform_value_for_tile(self, value, **kwargs):
        """
        Accepts a comma delimited string of file paths as 'value' to create a file datatype value
        with corresponding file record in the files table for each path. Only the basename of each path is used, so
        the accuracy of the full path is not important. However the name of each file must match the name of a file in
        the directory from which Arches will request files. By default, this is the directory in a project as defined
        in settings.UPLOADED_FILES_DIR.

        """

        mime = MimeTypes()
        tile_data = []
        source_path = kwargs.get("path")
        for file_path in [filename.strip() for filename in value.split(",")]:
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
            file_path = "%s/%s" % (settings.UPLOADED_FILES_DIR, str(tile_file["name"]))
            tile_file["file_id"] = str(uuid.uuid4())
            if source_path:
                source_file = os.path.join(source_path, tile_file["name"])
                fs = default_storage
                try:
                    with default_storage.open(source_file) as f:
                        current_file, created = models.File.objects.get_or_create(
                            fileid=tile_file["file_id"]
                        )
                        filename = fs.save(
                            os.path.join(
                                settings.UPLOADED_FILES_DIR, os.path.basename(f.name)
                            ),
                            File(f),
                        )
                        current_file.path = os.path.join(filename)
                        current_file.save()
                        tile_file["size"] = current_file.path.size
                except FileNotFoundError:
                    logger.exception(_("File does not exist"))

            else:
                models.File.objects.get_or_create(
                    fileid=tile_file["file_id"], path=file_path
                )

            tile_file["url"] = settings.MEDIA_URL + tile_file["file_id"]
            tile_file["accepted"] = True
            compatible_renderers = self.get_compatible_renderers(tile_file)
            if len(compatible_renderers) == 1:
                tile_file["renderer"] = compatible_renderers[0]
            tile_data.append(tile_file)
        return json.loads(json.dumps(tile_data))

    def pre_tile_save(self, tile, nodeid):
        # TODO If possible this method should probably replace 'handle request'
        if tile.data[nodeid]:
            for file in tile.data[nodeid]:
                try:
                    if file["file_id"]:
                        if file["url"] == f'{settings.MEDIA_URL}{file["file_id"]}':
                            val = uuid.UUID(
                                file["file_id"]
                            )  # to test if file_id is uuid
                            file_path = "%s/%s" % (
                                settings.UPLOADED_FILES_DIR,
                                file["name"],
                            )
                            try:
                                file_model = models.File.objects.get(pk=file["file_id"])
                            except ObjectDoesNotExist:
                                # Do not use get_or_create here because django can create a different file name applied to the file_path
                                # for the same file_id causing a 'create' when a 'get' was intended
                                file_model = models.File.objects.create(
                                    pk=file["file_id"], path=file_path
                                )
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
        return ",".join(
            [
                settings.MEDIA_URL
                + settings.UPLOADED_FILES_DIR
                + "/"
                + str(file["name"])
                for file in value
            ]
        )

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
                if (
                    lm > 9999999999
                ):  # not a straight timestamp, but includes milliseconds
                    lm = f_data["lastModified"] / 1000
                g.add(
                    (
                        f_uri,
                        DCTERMS.modified,
                        Literal(datetime.utcfromtimestamp(lm).isoformat()),
                    )
                )

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

    def collects_multiple_values(self):
        return True

    def default_es_mapping(self):
        return {
            "properties": {
                "file_id": {
                    "type": "text",
                    "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}},
                },
                "name": {
                    "type": "text",
                    "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}},
                },
                "type": {
                    "type": "text",
                    "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}},
                },
                "url": {
                    "type": "text",
                    "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}},
                },
                "status": {
                    "type": "text",
                    "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}},
                },
            }
        }


class BaseDomainDataType(BaseDataType):
    def __init__(self, model=None):
        super(BaseDomainDataType, self).__init__(model=model)
        self.value_lookup = {}

    def get_option_text(self, node, option_id):
        for option in node.config["options"]:
            if option["id"] == option_id:
                return option["text"]
        return {}

    def get_localized_option_text(self, node, option_id, return_lang=False):
        for option in node.config["options"]:
            if option["id"] == option_id:
                return get_localized_value(option["text"], return_lang=return_lang)
        raise Exception(
            _(
                "No domain option found for option id {0}, in node config: {1}".format(
                    option_id, node.config["options"]
                )
            )
        )

    def get_option_id_from_text(self, value):
        # this could be better written with most of the logic in SQL tbh
        # this returns the FIRST option that matches the text, but there could be
        # more than 1 option with that value!!.  If we knew the node then we could fix this issue.

        found_option = None
        dt = self.datatype_model.datatype
        domain_val_node_query = models.Node.objects.filter(datatype=dt)
        try:
            for x in domain_val_node_query:
                for option in x.config["options"]:
                    for option_text in option["text"].values():
                        if value == option_text:
                            found_option = option["id"]
                            # once we find at least one value we can just
                            # exit the nested loops by raising an excpetion
                            raise Exception()
        except:
            pass

        return found_option

    def is_a_literal_in_rdf(self):
        return True

    def lookup_domainid_by_value(self, value, nodeid):
        language = get_language()
        if nodeid not in self.value_lookup:
            config = models.Node.objects.get(pk=nodeid).config
            options = {}
            for val in config["options"]:
                options[val["text"][language]] = val["id"]
            self.value_lookup[nodeid] = options
        return self.value_lookup[nodeid][value]


class DomainDataType(BaseDomainDataType):
    def validate(
        self,
        value,
        row_number=None,
        source="",
        node=None,
        nodeid=None,
        strict=False,
        **kwargs,
    ):
        found_option = False
        errors = []
        if value is not None:
            try:
                uuid.UUID(str(value))
                found_option = (
                    len(
                        models.Node.objects.filter(
                            config__contains={"options": [{"id": value}]}
                        )
                    )
                    > 0
                )
            except ValueError as e:
                found_option = (
                    True if self.get_option_id_from_text(value) is not None else False
                )

            if not found_option:
                message = _(
                    "Invalid domain id. Please check the node this value is mapped to for a list of valid domain ids."
                )
                title = _("Invalid Domain Id")
                error_message = self.create_error_message(
                    value, source, row_number, message, title
                )
                errors.append(error_message)
        return errors

    def transform_value_for_tile(self, value, **kwargs):
        if value is not None:
            value = value.strip()
            try:
                uuid.UUID(value)
            except ValueError:
                try:
                    value = self.lookup_domainid_by_value(value, kwargs["nodeid"])
                except KeyError:
                    value = value
        return value

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        node = models.Node.objects.get(nodeid=nodeid)
        domain_text = self.get_option_text(node, nodevalue)
        for lang, text in domain_text.items():
            if settings.WORDS_PER_SEARCH_TERM is None or (
                len(text.split(" ")) < settings.WORDS_PER_SEARCH_TERM
            ):
                terms.append(SearchTerm(value=text, lang=lang))
        return terms

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        node = models.Node.objects.get(nodeid=nodeid)
        domain_text = self.get_option_text(node, nodevalue)

        for key in domain_text.keys():
            val = {
                "string": domain_text[key],
                "language": key,
                "nodegroup_id": tile.nodegroup_id,
                "provisional": provisional,
            }
            document["strings"].append(val)

    def get_display_value(self, tile, node, **kwargs):
        data = self.get_tile_data(tile)
        try:
            return self.get_localized_option_text(node, data[str(node.nodeid)])
        except:
            return ""

    def transform_export_values(self, value, *args, **kwargs):
        ret = ""
        if (
            kwargs["concept_export_value_type"] is None
            or kwargs["concept_export_value_type"] == ""
            or kwargs["concept_export_value_type"] == "label"
        ):
            ret = self.get_localized_option_text(
                models.Node.objects.get(nodeid=kwargs["node"]), value
            )
        elif kwargs["concept_export_value_type"] == "both":
            ret = (
                value
                + "|"
                + self.get_localized_option_text(
                    models.Node.objects.get(nodeid=kwargs["node"]), value
                )
            )
        elif kwargs["concept_export_value_type"] == "id":
            ret = value
        return ret

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "":
                search_query = Match(
                    field="tiles.data.%s" % (str(node.pk)),
                    type="phrase",
                    query=value["val"],
                )
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
            option = self.get_localized_option_text(
                edge.rangenode, edge_info["range_tile_data"], return_lang=True
            )
            lang = list(option.keys())[0]
            text = option[lang]
            g.add((edge_info["d_uri"], RDF.type, URIRef(edge.domainnode.ontologyclass)))
            g.add(
                (
                    edge_info["d_uri"],
                    URIRef(edge.ontologyproperty),
                    Literal(text, lang=lang),
                )
            )
        return g

    def from_rdf(self, json_ld_node):
        # depends on how much is passed to the method
        # if just the 'leaf' node, then not much can be done aside from return the list of nodes it might be from
        # a string may be present in multiple domains for instance
        # via models.Node.objects.filter(config__options__contains=[{"text": value}])
        value = get_value_from_jsonld(json_ld_node)
        return self.get_option_id_from_text(value[0])

    def i18n_as_sql(self, i18n_json_field, compiler, connection):
        """
        Creates a sql snippet that can be used to update the
        config object associated with this datatype.
        This snippet will be used in a SQL UPDATE statement.
        """

        sql = i18n_json_field.attname
        for prop, value in i18n_json_field.raw_value.items():
            escaped_value = json.dumps(value).replace("%", "%%").replace("'", "''")
            if prop == "options":
                sql = f"""
                    __arches_i18n_update_jsonb_array('options.text', '{{"options": {escaped_value}}}', {sql}, '{i18n_json_field.lang}')
                """
            else:
                sql = f"jsonb_set({sql}, array['{prop}'], '{escaped_value}')"
        return sql

    def i18n_serialize(self, i18n_json_field: I18n_JSONField):
        """
        Takes a localized list of options eg:
        {"options": [{"text":{"en": "blue", "es": "azul"}}, {"text":{"en": "red", "es": "rojo"}}]}
        and returns the value as a string based on the active language
        Eg: if the active language is Spanish then the above returned
        object would be {"options": [{"text":"azul"},{"text":"rojo"}]}

        Arguments:
        i18n_json_field -- the I18n_JSONField being serialized
        """

        ret = copy.deepcopy(i18n_json_field.raw_value)
        for option in ret["options"]:
            option["text"] = str(I18n_String(option["text"]))
        return ret

    def i18n_to_localized_object(self, i18n_json_field: I18n_JSONField):
        """
        Takes a list of optione that is assumed to hold a localized value
        eg: {"options": [{"text":"azul"},{"text":"rojo"}]}
        and returns the value as an object keyed to the active language
        Eg: if the active language is Spanish then the above returned
        object would be {"options": [{"text":{"es":"azul"}},{"text":{"es":"rojo"}}]}

        Arguments:
        i18n_json_field -- the I18n_JSONField being localized
        """

        ret = copy.deepcopy(i18n_json_field.raw_value)
        for option in ret["options"]:
            if not isinstance(option["text"], dict):
                option["text"] = {i18n_json_field.lang: option["text"]}
        return ret


class DomainListDataType(BaseDomainDataType):
    def transform_value_for_tile(self, value, **kwargs):
        result = []
        if value is not None:
            if not isinstance(value, list):
                value = value.split(",")
            for v in value:
                try:
                    stripped = v.strip()
                    uuid.UUID(stripped)
                    v = stripped
                except ValueError:
                    try:
                        v = self.lookup_domainid_by_value(v, kwargs["nodeid"])
                    except KeyError:
                        v = v
                result.append(v)
        return result

    def validate(
        self,
        values,
        row_number=None,
        source="",
        node=None,
        nodeid=None,
        strict=False,
        **kwargs,
    ):
        domainDataType = DomainDataType()
        domainDataType.datatype_name = "domain-value"
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
            for lang, text in domain_text.items():
                if settings.WORDS_PER_SEARCH_TERM is None or (
                    len(text.split(" ")) < settings.WORDS_PER_SEARCH_TERM
                ):
                    terms.append(SearchTerm(value=text, lang=lang))

        return terms

    def clean(self, tile, nodeid):
        super().clean(tile, nodeid)
        if tile.data[nodeid] == []:
            tile.data[nodeid] = None

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        domain_text_values = set([])
        node = models.Node.objects.get(nodeid=nodeid)
        for value in nodevalue:
            domain_text = self.get_option_text(node, value)
            # domain_text_values.add(text_value)
            for key in domain_text.keys():
                val = {
                    "string": domain_text[key],
                    "language": key,
                    "nodegroup_id": tile.nodegroup_id,
                    "provisional": provisional,
                }
                document["strings"].append(val)

    def get_display_value(self, tile, node, **kwargs):
        new_values = []
        data = self.get_tile_data(tile)
        if data[str(node.nodeid)] is not None:
            for val in data[str(node.nodeid)]:
                try:
                    option = self.get_localized_option_text(node, val)
                    new_values.append(option)
                except:
                    pass
        return ",".join(new_values)

    def transform_export_values(self, value, *args, **kwargs):
        new_values = []
        for val in value:
            if (
                kwargs["concept_export_value_type"] is None
                or kwargs["concept_export_value_type"] == ""
                or kwargs["concept_export_value_type"] == "label"
            ):
                new_values.append(
                    self.get_localized_option_text(
                        models.Node.objects.get(nodeid=kwargs["node"]), val
                    )
                )
            elif kwargs["concept_export_value_type"] == "both":
                new_values.append(
                    val
                    + "|"
                    + self.get_localized_option_text(
                        models.Node.objects.get(nodeid=kwargs["node"]), val
                    )
                )
            elif kwargs["concept_export_value_type"] == "id":
                new_values.append(val)
        return ",".join(new_values)

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "" and value["val"] != []:
                search_query = Match(
                    field="tiles.data.%s" % (str(node.pk)),
                    type="phrase",
                    query=value["val"],
                )
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

    def validate(
        self,
        value,
        row_number=None,
        source="",
        node=None,
        nodeid=None,
        strict=False,
        **kwargs,
    ):
        errors = []
        if value is not None:
            resourceXresourceIds = self.get_nodevalues(value)
            for resourceXresourceId in resourceXresourceIds:
                try:
                    resourceid = resourceXresourceId["resourceId"]
                    uuid.UUID(resourceid)
                    if strict:
                        try:
                            if not node:
                                node = models.Node.objects.get(pk=nodeid)
                            if node.config["searchString"] != "":
                                dsl = node.config["searchDsl"]
                                if dsl:
                                    query = Query(se)
                                    bool_query = Bool()
                                    ri_query = Dsl(dsl)
                                    bool_query.must(ri_query)
                                    ids_query = Dsl({"ids": {"values": [resourceid]}})
                                    bool_query.must(ids_query)
                                    query.add_query(bool_query)
                                    try:
                                        results = query.search(index=RESOURCES_INDEX)
                                        count = results["hits"]["total"]["value"]
                                        assert count == 1
                                    except:
                                        raise ObjectDoesNotExist()
                            if len(node.config["graphs"]) > 0:
                                graphids = map(
                                    lambda x: x["graphid"], node.config["graphs"]
                                )
                                if not models.ResourceInstance.objects.filter(
                                    pk=resourceid, graph_id__in=graphids
                                ).exists():
                                    raise ObjectDoesNotExist()
                        except ObjectDoesNotExist:
                            message = _(
                                "The related resource with id '{0}' is not in the system.".format(
                                    resourceid
                                )
                            )
                            errors.append({"type": "ERROR", "message": message})
                except (ValueError, TypeError):
                    message = _(
                        "The related resource with id '{0}' is not a valid uuid.".format(
                            str(value)
                        )
                    )
                    title = _("Invalid Resource Instance Datatype")
                    error_message = self.create_error_message(
                        value, source, row_number, message, title
                    )
                    errors.append(error_message)

        return errors

    def clean(self, tile, nodeid):
        super().clean(tile, nodeid)
        if tile.data[nodeid] == []:
            tile.data[nodeid] = None

    def pre_tile_save(self, tile, nodeid):
        relationships = tile.data[nodeid]
        if relationships:
            for relationship in relationships:
                relationship["resourceXresourceId"] = str(uuid.uuid4())

    def post_tile_save(self, tile, nodeid, request):
        ret = False
        sql = """
            SELECT * FROM __arches_create_resource_x_resource_relationships('%s') as t;
        """ % (
            tile.pk
        )

        with connection.cursor() as cursor:
            cursor.execute(sql)
            ret = cursor.fetchone()
        return ret

    def get_display_value(self, tile, node, **kwargs):
        from arches.app.models.resource import (
            Resource,
        )  # import here rather than top to avoid circular import

        resourceid = None
        data = self.get_tile_data(tile)
        nodevalue = self.get_nodevalues(data[str(node.nodeid)])

        items = []
        for resourceXresource in nodevalue:
            try:
                resourceid = resourceXresource["resourceId"]
                related_resource = Resource.objects.get(pk=resourceid)
                displayname = related_resource.displayname()
                if displayname is not None:
                    items.append(displayname)
            except (TypeError, KeyError):
                pass
            except:
                logger.info(f'Resource with id "{resourceid}" not in the system.')
        return ", ".join(items)

    def get_relationship_display_value(self, relationship_valueid):
        preflabel = get_preflabel_from_valueid(relationship_valueid, get_language())
        if preflabel:
            return preflabel["value"]
        else:
            return None

    def to_json(self, tile, node):
        from arches.app.models.resource import (
            Resource,
        )  # import here rather than top to avoid circular import

        data = self.get_tile_data(tile)
        if data:
            nodevalue = self.get_nodevalues(data[str(node.nodeid)])

            for resourceXresource in nodevalue:
                try:
                    return self.compile_json(tile, node, **resourceXresource)
                except (TypeError, KeyError):
                    pass
                except:
                    resourceid = resourceXresource["resourceId"]
                    logger.info(f'Resource with id "{resourceid}" not in the system.')

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        nodevalue = self.get_nodevalues(nodevalue)
        for relatedResourceItem in nodevalue:
            relationship = None
            document["ids"].append(
                {
                    "id": relatedResourceItem["resourceId"],
                    "nodegroup_id": tile.nodegroup_id,
                    "provisional": provisional,
                }
            )
            if relatedResourceItem.get("resourceName", "") != "":
                document["strings"].append(
                    {
                        "string": relatedResourceItem["resourceName"],
                        "nodegroup_id": tile.nodegroup_id,
                        "provisional": provisional,
                    }
                )
            for ontology_property_item in [
                relatedResourceItem.get("ontologyProperty", ""),
                relatedResourceItem.get("inverseOntologyProperty", ""),
            ]:
                if ontology_property_item != "":
                    try:
                        uuid.UUID(ontology_property_item)
                        relationship = (
                            self.get_relationship_display_value(ontology_property_item)
                            or ontology_property_item
                        )
                    except ValueError:
                        relationship = ontology_property_item
                    document["strings"].append(
                        {
                            "string": relationship,
                            "nodegroup_id": tile.nodegroup_id,
                            "provisional": provisional,
                        }
                    )

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        nodevalue = self.get_nodevalues(nodevalue)
        for relatedResourceItem in nodevalue:
            if relatedResourceItem.get("resourceName", "") != "":
                terms.append(
                    SearchTerm(value=relatedResourceItem["resourceName"], lang="")
                )
            for ontology_property_item in [
                relatedResourceItem.get("ontologyProperty", ""),
                relatedResourceItem.get("inverseOntologyProperty", ""),
            ]:
                if ontology_property_item != "":
                    try:
                        uuid.UUID(ontology_property_item)
                        relationship = (
                            self.get_relationship_display_value(ontology_property_item)
                            or ontology_property_item
                        )
                        terms.append(SearchTerm(value=relationship, lang=""))
                    except ValueError:
                        terms.append(SearchTerm(value=ontology_property_item, lang=""))

        return terms

    def transform_value_for_tile(self, value, **kwargs):
        try:
            return json.loads(value)
        except ValueError:
            # do this if json (invalid) is formatted with single quotes, re #6390
            try:
                return ast.literal_eval(value)
            except:
                return value
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
                search_query = Terms(
                    field="tiles.data.%s.resourceId.keyword" % (str(node.pk)),
                    terms=value["val"],
                )
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
        return uri.startswith("urn:uuid:") or uri.startswith(
            settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT + "resources/"
        )

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

            ontologyclass_lookup = {}
            for res_inst in res_insts:
                rangenode = self.get_rdf_uri(None, res_inst)
                try:
                    res_inst_graphid = models.ResourceInstance.objects.get(
                        pk=res_inst["resourceId"]
                    ).graph_id
                    try:
                        r_type = ontologyclass_lookup[res_inst_graphid]
                    except KeyError:
                        r_type = models.Node.objects.get(
                            graph=res_inst_graphid, istopnode=True
                        ).ontologyclass
                        ontologyclass_lookup[res_inst_graphid] = r_type
                except models.ResourceInstance.DoesNotExist:
                    # This should never happen excpet if trying to export when the
                    # referenced resource hasn't been saved to the database yet
                    r_type = edge.rangenode.ontologyclass
                _add_resource(
                    edge_info["d_uri"], edge.ontologyproperty, rangenode, r_type
                )
        return g

    def from_rdf(self, json_ld_node):
        res_inst_uri = json_ld_node["@id"]
        # `id` should be in the form schema:{...}/{UUID}
        # eg `urn:uuid:{UUID}`
        #    `http://arches_instance.getty.edu/resources/{UUID}`
        p = re.compile(
            r"(?P<r>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/?$"
        )
        m = p.search(res_inst_uri)
        if m is not None:
            # return m.groupdict()["r"]
            return [
                {
                    "resourceId": m.groupdict()["r"],
                    "ontologyProperty": "",
                    "inverseOntologyProperty": "",
                    "resourceXresourceId": "",
                }
            ]

    def ignore_keys(self):
        return [
            "http://www.w3.org/2000/01/rdf-schema#label http://www.w3.org/2000/01/rdf-schema#Literal"
        ]

    def references_resource_type(self):
        """
        This resource references another resource type (eg resource-instance-datatype, etc...)
        """

        return True

    def default_es_mapping(self):
        mapping = {
            "properties": {
                "resourceId": {
                    "type": "text",
                    "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}},
                },
                "ontologyProperty": {
                    "type": "text",
                    "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}},
                },
                "inverseOntologyProperty": {
                    "type": "text",
                    "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}},
                },
                "resourceXresourceId": {
                    "type": "text",
                    "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}},
                },
            }
        }
        return mapping


class ResourceInstanceListDataType(ResourceInstanceDataType):
    def to_json(self, tile, node):
        from arches.app.models.resource import (
            Resource,
        )  # import here rather than top to avoid circular import

        resourceid = None
        data = self.get_tile_data(tile)
        if data:
            nodevalue = self.get_nodevalues(data[str(node.nodeid)])
            items = []

            for resourceXresource in nodevalue:
                try:
                    resourceid = resourceXresource["resourceId"]
                    related_resource = Resource.objects.get(pk=resourceid)
                    displayname = related_resource.displayname()
                    resourceXresource["display_value"] = displayname
                    items.append(resourceXresource)
                except (TypeError, KeyError):
                    pass
                except:
                    logger.info(f'Resource with id "{resourceid}" not in the system.')
            return self.compile_json(tile, node, instance_details=items)

    def collects_multiple_values(self):
        return True


class NodeValueDataType(BaseDataType):
    def validate(
        self,
        value,
        row_number=None,
        source="",
        node=None,
        nodeid=None,
        strict=False,
        **kwargs,
    ):
        errors = []
        if value:
            try:
                models.TileModel.objects.get(tileid=value)
            except ObjectDoesNotExist:
                message = _(
                    "{0} {1} is not a valid tile id. This data was not imported.".format(
                        value, row_number
                    )
                )
                title = _("Invalid Tile Id")
                errors.append({"type": "ERROR", "message": message, "title": title})
        return errors

    def get_display_value(self, tile, node, **kwargs):
        datatype_factory = DataTypeFactory()
        try:
            value_node = models.Node.objects.get(nodeid=node.config["nodeid"])
            data = self.get_tile_data(tile)
            tileid = data[str(node.nodeid)]
            if tileid:
                value_tile = models.TileModel.objects.get(tileid=tileid)
                datatype = datatype_factory.get_instance(value_node.datatype)
                return datatype.get_display_value(value_tile, value_node)
            return ""
        except:
            raise Exception(
                f'Node with name "{node.name}" is not configured correctly.'
            )

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        pass

    def append_search_filters(self, value, node, query, request):
        pass


class AnnotationDataType(BaseDataType):
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
        return errors

    def to_json(self, tile, node):
        data = self.get_tile_data(tile)
        if data:
            return self.compile_json(tile, node, geojson=data.get(str(node.nodeid)))

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        return

    def transform_value_for_tile(self, value, **kwargs):
        try:
            return json.loads(value)
        except ValueError:
            # do this if json (invalid) is formatted with single quotes, re #6390
            try:
                return ast.literal_eval(value)
            except:
                return None
        except TypeError:
            # data should come in as json but python list is accepted as well
            if isinstance(value, list):
                return value

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
