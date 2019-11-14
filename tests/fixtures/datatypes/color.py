from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from arches.app.models.system_settings import settings
from rdflib import Namespace, URIRef, Literal, BNode
from rdflib import ConjunctiveGraph as Graph
from rdflib.namespace import RDF, RDFS, XSD, DC, DCTERMS
archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
cidoc_nm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")

string_widget = models.Widget.objects.get(name='text-widget')

details = {
    'datatype': 'color-datatype',
    'iconclass': 'fas fa-palette',
    'modulename': 'color.py',
    'classname': 'ColorDataType',
    'defaultwidget': string_widget,
    'defaultconfig': {},
    'configcomponent': '',
    'configname': '',
    'isgeometric': False
    }

class ColorDataType(BaseDataType):

    def validate(self, value, row_number=None, source=None, node=None):
        errors = []
        try:
            value.upper()
        except:
            errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} {3} - {4}. {5}'.format(self.datatype_model.datatype, value, row_number, source, 'this is not a string', 'This data was not imported.')})
        return errors

    def is_a_literal_in_rdf(self):
        return True

    def to_rdf(self, edge_info, edge):
        # returns an in-memory graph object, containing the domain resource, its
        # type and the string as a string literal
        g = Graph()
        if edge_info['range_tile_data'] is not None:
            g.add((edge_info['d_uri'], RDF.type, URIRef(edge.domainnode.ontologyclass)))
            g.add((edge_info['d_uri'], URIRef(edge.ontologyproperty), Literal(edge_info['range_tile_data'])))
        return g

    def from_rdf(self, json_ld_node):
        # returns the string value only
        value = get_value_from_jsonld(json_ld_node)
        try:
            return value[0]
        except (AttributeError, KeyError) as e:
            pass

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