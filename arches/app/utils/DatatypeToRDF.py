import json
from arches.app.utils.betterJSONSerializer import JSONSerializer
from rdflib import Namespace, URIRef, Literal, Graph
from rdflib.namespace import RDF, RDFS, XSD
from arches.app.models.models import Value
from arches.app.models.system_settings import settings
from arches.app.models.concept import Concept, ConceptValue

archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)

def _handle_semantic(graph, domainnode, rangenode, edge, tile, 
                     domain_tile_data, range_tile_data, graph_uri):
    pass

def _handle_number(graph, domainnode, rangenode, edge, tile, 
                   domain_tile_data, range_tile_data, graph_uri):
    if edge.domainnode.istopnode:
        graph.add((domainnode, RDF.type, graph_uri))
    graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))

    graph.add((domainnode, URIRef(edge.ontologyproperty), Literal(range_tile_data)))

def _handle_boolean(graph, domainnode, rangenode, edge, tile, 
                    domain_tile_data, range_tile_data, graph_uri):
    if edge.domainnode.istopnode:
        graph.add((domainnode, RDF.type, graph_uri))
    graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))

    graph.add((domainnode, URIRef(edge.ontologyproperty), Literal(Boolean(range_tile_data))))

def _handle_string(graph, domainnode, rangenode, edge, tile, 
                   domain_tile_data, range_tile_data, graph_uri):
    if edge.domainnode.istopnode:
        graph.add((domainnode, RDF.type, graph_uri))
    graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))

    graph.add((domainnode, URIRef(edge.ontologyproperty), Literal(str(range_tile_data))))

def _handle_date(graph, domainnode, rangenode, edge, tile,
                 domain_tile_data, range_tile_data, graph_uri):
    if edge.domainnode.istopnode:
        graph.add((domainnode, RDF.type, graph_uri)) 
    graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))

    graph.add((domainnode, URIRef(edge.ontologyproperty), Literal(str(range_tile_data), datatype=XSD.dateTime)))

def _append_resource_node(graph, domainnode, edge, resource_inst):
    rangenode = URIRef(archesproject['resources/%s' % resource_inst])
    graph.add((rangenode, RDF.type, URIRef(edge.rangenode.ontologyclass)))
    graph.add((domainnode, URIRef(edge.ontologyproperty), rangenode))
    # XXX Insert label here if exists on instance

def _handle_resource_instance(graph, domainnode, rangenode, edge, tile,
                              domain_tile_data, range_tile_data, graph_uri):
    # manipulate rangenode's id from range_tile_data
    # resource-instance (rather than -list) will always be single value
    if edge.domainnode.istopnode:
        graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))

    # should really assert that the range_tile_data is a string and a valid resource
    # instance UUID
    _append_resource_node(graph, domainnode, edge, range_tile_data)


def _handle_resource_instance_list(graph, domainnode, rangenode, edge, tile, 
                                   domain_tile_data, range_tile_data, graph_uri):

    if edge.domainnode.istopnode:
        graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))

    for r in range_tile_data:
        _append_resource_node(graph, domainnode, edge, r)


def _handle_domain_value(graph, domainnode, rangenode, edge, tile,
                         domain_tile_data, range_tile_data, graph_uri):
    pass

def _handle_geojson_feature_collection(graph, domainnode, rangenode, edge, tile,
                                       domain_tile_data, range_tile_data, graph_uri):
    pass

def _append_concept_node(graph, domainnode, edge, concept_value_id):
    info = {}
    c = ConceptValue(concept_value_id)
    # FIXME: switch this to a DB call that gets all this in one or forces the
    # ORM to do that and cache.
    info['label'] = c.value
    info['concept_id'] = c.conceptid
    info['lang'] = c.language

    rangenode = URIRef(archesproject['concepts/%s' % info['concept_id']] )

    graph.add((rangenode, RDF.type, URIRef(edge.rangenode.ontologyclass)))
    graph.add((domainnode, URIRef(edge.ontologyproperty), rangenode))

    # add in some convenience information for the concept:
    # FIXME: Add the language back in, once pyld fixes its problem with uppercase lang
    # tokens -> https://github.com/digitalbazaar/pyld/issues/86
    #graph.add((rangenode, URIRef(RDFS.label), Literal(info['label'], lang=info['lang'])))

    graph.add((rangenode, URIRef(RDFS.label), Literal(info['label'])))

    # add in additional identifiers?
    # the DB/ORM way
    # for identifier in Value.objects.get(valuetype__exact="identifier"):

def _handle_concept(graph, domainnode, rangenode, edge, tile,
                    domain_tile_data, range_tile_data, graph_uri):
    if edge.domainnode.istopnode:
        graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))

    _append_concept_node(graph, domainnode, edge, str(range_tile_data))

def _handle_concept_list(graph, domainnode, rangenode, edge, tile, 
                         domain_tile_data, range_tile_data, graph_uri):
    if edge.domainnode.istopnode:
        graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))
    for r in range_tile_data:
        _append_concept_node(graph, domainnode, edge, str(r))

def _handle_csv_chart_json(graph, domainnode, rangenode, edge, tile,
                    domain_tile_data, range_tile_data, graph_uri):
    pass

def _handle_edtf(graph, domainnode, rangenode, edge, tile,
                    domain_tile_data, range_tile_data, graph_uri):
    pass

def _handle_iiif_drawing(graph, domainnode, rangenode, edge, tile,
                    domain_tile_data, range_tile_data, graph_uri):
    pass

def _handle_node_value(graph, domainnode, rangenode, edge, tile,
                    domain_tile_data, range_tile_data, graph_uri):
    pass

def _handle_file_list(graph, domainnode, rangenode, edge, tile, 
                      domain_tile_data, range_tile_data, graph_uri):
    pass

def _handle_domain_value_list(graph, domainnode, rangenode, edge, tile,
                         domain_tile_data, range_tile_data, graph_uri):
    pass

def _handle__default(graph, domainnode, rangenode, edge, tile,
                     domain_tile_data, range_tile_data, graph_uri):
    graph.add((rangenode, RDF.type, URIRef(edge.rangenode.ontologyclass)))
    graph.add((domainnode, URIRef(edge.ontologyproperty), rangenode))

    # This is in the original default method, but graph_uri just shouldn't be a type
    #if edge.domainnode.istopnode:
    #    graph.add((domainnode, RDF.type, graph_uri))

    graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))

    if domain_tile_data != None:
        graph.add((domainnode, 
               RDF.value, 
               Literal(JSONSerializer().serialize(domain_tile_data))))

    if range_tile_data != None:
        graph.add((rangenode, 
               RDF.value, 
               Literal(JSONSerializer().serialize(range_tile_data))))

_output_mapping = {#"semantic": _handle_semantic,
                   "number": _handle_number,
                   "boolean": _handle_boolean,
                   "string": _handle_string,
                   "date": _handle_date,
                   #"csv-chart-json": _handle_csv_chart_json,
                   #"iiif-drawing": _handle_iiif_drawing,
                   #"edtf": _handle_edtf,
                   #"node-value": _handle_node_value,
                   "resource-instance": _handle_resource_instance,
                   #"domain-value": _handle_domain_value,
                   #"domain-value-list": _handle_domain_value_list,
                   #"geojson-feature-collection": _handle_geojson_feature_collection,
                   "concept": _handle_concept,
                   "concept-list": _handle_concept_list,
                   #"file-list": _handle_file_list,
                   "resource-instance-list": _handle_resource_instance_list,
                   "_default": _handle__default,
                   }

def add_tile_information_to_graph(graph, domainnode_data, rangenode_data, edge, tile, graph_uri):
    domainnode, d_datatype = domainnode_data
    rangenode, r_datatype = rangenode_data
    range_tile_data = None
    domain_tile_data = None

    if d_datatype not in ['number', 'boolean','string', 'date', 'resource-instance', 'concept', 'resource-instance-list']:
        if str(edge.rangenode_id) in tile.data:
            range_tile_data = tile.data[str(edge.rangenode_id)]
        if str(edge.domainnode_id) in tile.data:
            domain_tile_data = tile.data[str(edge.domainnode_id)]
        # output based on the datatype of the rangenode:
        graph_handler = _output_mapping.get(r_datatype, _handle__default)
        graph_handler(graph, domainnode, rangenode, edge, tile, domain_tile_data, range_tile_data, graph_uri)
    else:
        # If the domain is not in that datatype list, then it is not a leaf node 
        # within the RDF representation. If it is, then it is or will be handled
        # as a range node from some other edge object.
        # In other words, the RDF representation doesn't hold this sort of reified
        # data and we can ignore it.
        pass