from django.utils.translation import gettext as _
from rdflib import URIRef, Literal, ConjunctiveGraph as Graph
from rdflib.namespace import RDF

from arches.app.datatypes.base import BaseDataType
from arches.app.datatypes.core.util import get_value_from_jsonld
from django.conf import settings
from arches.app.search.elasticsearch_dsl_builder import (
    Bool,
    Exists,
    Match,
    Term,
    Terms,
    Wildcard,
    Nested,
)
from arches.app.search.search_term import SearchTerm


class NonLocalizedStringDataType(BaseDataType):
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
                value.upper()
        except:
            message = _("This is not a string")
            error_message = self.create_error_message(
                value, source, row_number, message
            )
            errors.append(error_message)
        return errors

    def clean(self, tile, nodeid):
        if tile.data[nodeid] in ["", "''"]:
            tile.data[nodeid] = None

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        if nodevalue is not None:
            val = {
                "string": nodevalue,
                "language": "",
                "nodegroup_id": tile.nodegroup_id,
                "provisional": provisional,
            }
            document["strings"].append(val)

    def transform_export_values(self, value, *args, **kwargs):
        if value is not None:
            return value

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []

        if nodevalue is not None:
            if settings.WORDS_PER_SEARCH_TERM is None or (
                len(nodevalue.split(" ")) < settings.WORDS_PER_SEARCH_TERM
            ):
                terms.append(SearchTerm(value=nodevalue, lang=""))
        return terms

    def append_null_search_filters(self, value, node, query: Bool, request):
        """
        Appends the search query dsl to search for fields that have not been populated or are empty strings
        """
        query.filter(Terms(field="graph_id", terms=[str(node.graph_id)]))

        data_exists_query = Exists(field=f"tiles.data.{str(node.pk)}")
        tiles_w_node_exists = Nested(path="tiles", query=data_exists_query)

        if value["op"] == "not_null":
            query.must(tiles_w_node_exists)
            non_blank_string_query = Wildcard(
                field=f"tiles.data.{str(node.pk)}", query="?*"
            )
            query.must(Nested(path="tiles", query=non_blank_string_query))

        elif value["op"] == "null":
            # search for tiles that don't exist
            not_exists_query = Bool()
            not_exists_query.must_not(tiles_w_node_exists)
            query.should(not_exists_query)

            # search for tiles that do exist, but have empty strings
            non_blank_string_query = Term(
                field=f"tiles.data.{str(node.pk)}.keyword",
                query="",
            )
            query.should(Nested(path="tiles", query=non_blank_string_query))

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "":
                match_type = "phrase_prefix" if "~" in value["op"] else "phrase"
                match_query = Match(
                    field="tiles.data.%s" % (str(node.pk)),
                    query=value["val"],
                    type=match_type,
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
            g.add(
                (
                    edge_info["d_uri"],
                    URIRef(edge.ontologyproperty),
                    Literal(edge_info["range_tile_data"]),
                )
            )
        return g

    def from_rdf(self, json_ld_node):
        # returns the string value only
        # FIXME: Language?
        value = get_value_from_jsonld(json_ld_node)
        try:
            return value[0]
        except (AttributeError, KeyError) as e:
            pass
