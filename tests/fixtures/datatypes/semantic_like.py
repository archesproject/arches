from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from arches.app.models.system_settings import settings
from rdflib import Namespace, URIRef, Literal, BNode
from rdflib import ConjunctiveGraph as Graph
from rdflib.namespace import RDF, RDFS, XSD, DC, DCTERMS
archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
cidoc_nm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")

details = {
    'datatype': 'semantic-like-datatype',
    'iconclass': 'fas fa-palette',
    'modulename': 'semantic_like.py',
    'classname': 'SemanticLikeDataType',
    'defaultwidget': None,
    'defaultconfig': {},
    'configcomponent': '',
    'configname': '',
    'isgeometric': False
    }

class SemanticLikeDataType(BaseDataType):

    def validate(self, value, row_number=None, source=None):
        return True

    def is_a_literal_in_rdf(self):
        return False

    # def to_rdf(self, edge_info, edge):
    #     # returns an in-memory graph object, containing the domain resource, its
    #     # type and the string as a string literal
    #     g = Graph()
    #     if edge_info['range_tile_data'] is not None:
    #         g.add((edge_info['d_uri'], RDF.type, URIRef(edge.domainnode.ontologyclass)))
    #         g.add((edge_info['d_uri'], URIRef(edge.ontologyproperty), Literal(edge_info['range_tile_data'])))
    #     return g

    # def from_rdf(self, json_ld_node):
    #     # returns the string value only
    #     # FIXME: Language?
    #     value = get_value_from_jsonld(json_ld_node)
    #     try:
    #         return value[0]
    #     except (AttributeError, KeyError) as e:
    #         pass
