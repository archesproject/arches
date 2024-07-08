"""
Copyright (C) 2019 J. Paul Getty Trust

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import ast
import re
import json
from arches.app.models.system_settings import settings
from arches.app.datatypes.base import BaseDataType
from arches.app.models.models import Widget
from arches.app.search.elasticsearch_dsl_builder import Match, Exists, Term
from arches.app.search.search_term import SearchTerm

from rdflib import ConjunctiveGraph as Graph
from rdflib import URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD, DC, DCTERMS
from django.utils.translation import gettext as _

archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
cidoc_nm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")

import logging

logger = logging.getLogger(__name__)

default_widget_name = "urldatatype"
default_url_widget = None
try:
    default_url_widget = Widget.objects.get(name=default_widget_name)
except Widget.DoesNotExist as e:
    logger.warning(
        "Setting 'url' datatype's default widget to None ({0} widget not found).".format(
            default_widget_name
        )
    )

details = {
    "datatype": "url",
    "iconclass": "fa fa-location-arrow",
    "modulename": "url.py",
    "classname": "URLDataType",
    "defaultwidget": default_url_widget,
    "defaultconfig": None,
    "configcomponent": "views/components/datatypes/url",
    "configname": "url-datatype-config",
    "isgeometric": False,
    "issearchable": True,
}


class FailRegexURLMatch(Exception):
    pass


class URLDataType(BaseDataType):
    """
    URL Datatype to store an optionally labelled hyperlink to a (typically) external resource
    """

    URL_REGEX = re.compile(
        r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    )

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

        if value is not None:
            try:
                if value.get("url"):
                    # check URL conforms to URL structure
                    url_test = self.URL_REGEX.match(value["url"])
                    if url_test is None:
                        raise FailRegexURLMatch
            except FailRegexURLMatch:
                message = _("This is not a valid HTTP/HTTPS URL")
                title = _("Invalid HTTP/HTTPS URL")
                error_message = self.create_error_message(
                    value, source, row_number, message, title
                )
                errors.append(error_message)

            # raise error if label added without URL (#10592)
            if value.get("url_label") and not value.get("url"):
                message = _("URL label cannot be saved without a URL")
                title = _("No URL added")
                error_message = self.create_error_message(
                    value, source, row_number, message, title
                )
                errors.append(error_message)

        return errors

    def transform_value_for_tile(self, value, **kwargs):
        """
        Used, for example, during import for transforming incomming data to

        Arguments
        value -- can either be a url string like "http://archesproject.org" or
        a json string like '{"url": "", "url_label": ""}'
        """

        try:
            return json.loads(value)
        except ValueError:
            # do this if json (invalid) is formatted with single quotes, re #6390
            try:
                return ast.literal_eval(value)
            except:
                if isinstance(value, dict):
                    return value
                else:
                    return {"url": value, "url_label": ""}
        except BaseException:
            # this will probably fail validation, but that is ok. We need the error to report the value.
            if isinstance(value, dict):
                return value
            else:
                return {"url": value, "url_label": ""}

    def get_display_value(self, tile, node, **kwargs):
        data = self.get_tile_data(tile)
        if data:
            display_value = data.get(str(node.nodeid))

            if display_value:
                return json.dumps(display_value)

    def to_json(self, tile, node):
        data = self.get_tile_data(tile)
        if data:
            return self.compile_json(tile, node, **data.get(str(node.nodeid)))

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        if nodevalue.get("url") is not None:
            if nodevalue.get("url_label") is not None:
                val = {
                    "string": nodevalue["url_label"],
                    "nodegroup_id": tile.nodegroup_id,
                    "provisional": provisional,
                }
                document["strings"].append(val)

            # FIXME: URLs searchable?
            val = {
                "string": nodevalue["url"],
                "nodegroup_id": tile.nodegroup_id,
                "provisional": provisional,
            }
            document["strings"].append(val)

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        if nodevalue.get("url") is not None:
            if nodevalue.get("url_label") is not None:
                if settings.WORDS_PER_SEARCH_TERM is None or (
                    len(nodevalue["url_label"].split(" "))
                    < settings.WORDS_PER_SEARCH_TERM
                ):
                    terms.append(SearchTerm(value=nodevalue["url_label"]))
            # terms.append(nodevalue['url'])       FIXME: URLs searchable?
        return terms

    def append_search_filters(self, value, node, query, request):
        # Match the label in the same manner as a String datatype
        try:
            if value["val"] != "":
                if "~" in value["op"]:
                    match_query = Match(
                        field="tiles.data.%s.url" % (str(node.pk)),
                        query=value["val"],
                        type="phrase_prefix",
                    )
                if "eq" in value["op"]:
                    match_query = Term(
                        field="tiles.data.%s.url.keyword" % (str(node.pk)),
                        term=value["val"],
                    )
                if "!" in value["op"]:
                    query.must_not(match_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(match_query)
        except KeyError as e:
            pass

    def get_rdf_uri(self, node, data, which="r"):
        if data and "url" in data:
            return URIRef(data["url"])
        return None

    def accepts_rdf_uri(self, uri):
        return self.URL_REGEX.match(uri) and not (
            uri.startswith("urn:uuid:")
            or uri.startswith(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT + "resources/")
        )

    def is_a_literal_in_rdf(self):
        # Should this be a terminating node? Should be True if it is...
        return False

    def ignore_keys(self):
        # We process label into the datatype, so downstream processing should ignore it.
        return [
            "http://www.w3.org/2000/01/rdf-schema#label http://www.w3.org/2000/01/rdf-schema#Literal"
        ]

    def to_rdf(self, edge_info, edge):
        # returns an in-memory graph object, containing the domain resource, its
        # type and the string as a string literal
        g = Graph()
        if (
            edge_info["range_tile_data"] is not None
            and edge_info["range_tile_data"].get("url") is not None
        ):
            g.add((edge_info["d_uri"], RDF.type, URIRef(edge.domainnode.ontologyclass)))
            g.add(
                (
                    edge_info["d_uri"],
                    URIRef(edge.ontologyproperty),
                    URIRef(edge_info["range_tile_data"]["url"]),
                )
            )
            if edge_info["range_tile_data"].get("url_label") is not None:
                g.add(
                    (
                        URIRef(edge_info["range_tile_data"]["url"]),
                        RDFS.label,
                        Literal(edge_info["range_tile_data"]["url_label"]),
                    )
                )
        return g

    def from_rdf(self, json_ld_node):
        """
        The json-ld representation of this datatype should look like the following (once expanded)
          {
            "http://www.w3.org/2000/01/rdf-schema#label": [
              {
                "@value": "Link to spectro report"
              }
            ],
            "@id": "https://host/url/to/link"
          }
        """

        value = {}
        if type(json_ld_node) == list:
            url_node = json_ld_node[0]
        else:
            url_node = json_ld_node
        try:
            value["url"] = url_node["@id"]
            value["url_label"] = None
            if "http://www.w3.org/2000/01/rdf-schema#label" in url_node:
                value["url_label"] = url_node[
                    "http://www.w3.org/2000/01/rdf-schema#label"
                ][0]["@value"]
        except (IndexError, AttributeError, KeyError) as e:
            print(f"Broke trying to import url datatype: {json_ld_node}")
            return None
        return value

    def default_es_mapping(self):
        """
        Default mapping if not specified is a text field
        """

        return {
            "properties": {
                "url": {
                    "type": "text",
                    "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}},
                },
                "url_label": {
                    "type": "text",
                    "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}},
                },
            }
        }

    def pre_tile_save(self, tile, nodeid):
        if (tile_val := tile.data[nodeid]) and "url_label" not in tile_val:
            tile_val["url_label"] = ""

    def clean(self, tile, nodeid):
        if data := tile.data[nodeid]:
            try:
                if not any([val.strip() for val in data.values()]):
                    tile.data[nodeid] = None
            except:
                pass  # Let self.validate handle malformed data

    def pre_structure_tile_data(self, tile, nodeid, **kwargs):
        if (tile_val := tile.data[nodeid]) and "url_label" not in tile_val:
            tile_val["url_label"] = ""
