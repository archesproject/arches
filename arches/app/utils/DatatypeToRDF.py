import json
from arches.app.utils.betterJSONSerializer import JSONSerializer
from rdflib import Namespace, URIRef, Literal, Graph, BNode
from rdflib.namespace import RDF, RDFS, XSD, DC, DCTERMS
from arches.app.models.models import Value
from arches.app.models.system_settings import settings
from arches.app.models.concept import Concept, ConceptValue

archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
cidoc = Namespace("http://www.cidoc-crm.org/cidoc-crm/")

# Handle basic field types (number, bookean, string and date):
def _handle_number(graph, domainnode, rangenode, edge, tile, 
                   domain_tile_data, range_tile_data, graph_uri):

    graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))
    # Check if actually an int in disguise
    rtd = int(range_tile_data) if range_tile_data.is_integer() else range_tile_data
    graph.add((domainnode, URIRef(edge.ontologyproperty), Literal(rtd)))

def _handle_boolean(graph, domainnode, rangenode, edge, tile, 
                    domain_tile_data, range_tile_data, graph_uri):

    graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))
    graph.add((domainnode, URIRef(edge.ontologyproperty), Literal(Boolean(range_tile_data))))

def _handle_string(graph, domainnode, rangenode, edge, tile, 
                   domain_tile_data, range_tile_data, graph_uri):

    graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))
    graph.add((domainnode, URIRef(edge.ontologyproperty), Literal(str(range_tile_data))))

def _handle_date(graph, domainnode, rangenode, edge, tile,
                 domain_tile_data, range_tile_data, graph_uri):

    graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))
    graph.add((domainnode, URIRef(edge.ontologyproperty), Literal(str(range_tile_data), datatype=XSD.dateTime)))

def _append_resource_node(graph, domainnode, edge, resource_inst):
    # Helper function. Adds a typed node (based on what type the edge
    # expects the range node to be) to the graph. Uses the current host as
    # the URI namespace.
    rangenode = URIRef(archesproject['resources/%s' % resource_inst])
    graph.add((rangenode, RDF.type, URIRef(edge.rangenode.ontologyclass)))
    graph.add((domainnode, URIRef(edge.ontologyproperty), rangenode))
    # FIXME Insert label here if exists on instance?

def _handle_resource_instance(graph, domainnode, rangenode, edge, tile,
                              domain_tile_data, range_tile_data, graph_uri):
    # use the resource instance id from range_tile_data
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

    if range_tile_data:
        for r in range_tile_data:
            _append_resource_node(graph, domainnode, edge, r)

def _append_concept_node(graph, domainnode, edge, concept_value_id):
    info = {}
    c = ConceptValue(concept_value_id)
    info['label'] = c.value
    info['concept_id'] = c.conceptid
    info['lang'] = c.language

    # Use the conceptid URI rather than the pk for the ConceptValue
    rangenode = URIRef(archesproject['concepts/%s' % info['concept_id']] )

    graph.add((rangenode, RDF.type, URIRef(edge.rangenode.ontologyclass)))
    graph.add((domainnode, URIRef(edge.ontologyproperty), rangenode))

    # FIXME: Add the language back in, once pyld fixes its problem with uppercase lang
    # tokens -> https://github.com/digitalbazaar/pyld/issues/86
    #graph.add((rangenode, URIRef(RDFS.label), Literal(info['label'], lang=info['lang'])))

    graph.add((rangenode, URIRef(RDFS.label), Literal(info['label'])))

    # add in additional identifiers for the concept
    # the DB/ORM way for eg:
    # for identifier_obj in Value.objects.get(valuetype__exact="identifier"):

def _handle_concept(graph, domainnode, rangenode, edge, tile,
                    domain_tile_data, range_tile_data, graph_uri):
    if edge.domainnode.istopnode:
        graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))

    _append_concept_node(graph, domainnode, edge, str(range_tile_data))

def _handle_concept_list(graph, domainnode, rangenode, edge, tile, 
                         domain_tile_data, range_tile_data, graph_uri):
    if edge.domainnode.istopnode:
        graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))
    if range_tile_data:
        for r in range_tile_data:
            _append_concept_node(graph, domainnode, edge, str(r))

def _get_aat_refs(graph):
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
       graph.parse(data=unit_nt, format="nt")

       return {'pixels': URIRef("http://vocab.getty.edu/aat/300266190"),
               'bytes': URIRef("http://vocab.getty.edu/aat/300265869"),
               'height': URIRef("http://vocab.getty.edu/aat/300055644"),
               'width': URIRef("http://vocab.getty.edu/aat/300055647"),
               'file size': URIRef("http://vocab.getty.edu/aat/300265863"),}

def _handle_file_list(graph, domainnode, rangenode, edge, tile, 
                      domain_tile_data, range_tile_data, graph_uri):

    from datetime import datetime

    aatrefs = _get_aat_refs(graph)
    # All files should have a size, but things like height and width will be 
    # only found in images
    # FIXME find the full list of image types that have h/w in their serialisations

    def add_dimension(graph, domain_uri, unittype, unit, value):
        dim_node = BNode()
        graph.add((domain_uri, cidoc["P43_has_dimension"], dim_node))
        graph.add((dim_node, RDF.type, cidoc["E54_Dimension"]))
        graph.add((dim_node, cidoc["P2_has_type"], aatrefs[unittype]))
        graph.add((dim_node, cidoc["P91_has_unit"], aatrefs[unit]))
        graph.add((dim_node, RDF.value, Literal(value)))

    for f_data in range_tile_data:
        # f_data will be something like:
        # "{\"accepted\": true, \"content\": \"blob:http://localhost/cccadfd0-64fc-104a-8157-3c96aca0b9bd\", 
        # \"file_id\": \"f4cd6596-cd75-11e8-85e0-0242ac1b0003\", \"height\": 307, \"index\": 0,
        # \"lastModified\": 1535067185606, \"name\": \"FUjJqP6.jpg\", \"size\": 19350, 
        # \"status\": \"uploaded\", \"type\": \"image/jpeg\", \"url\": \"/files/uploadedfiles/FUjJqP6.jpg\",
        # \"width\": 503}"
        
        # range URI should be the file URL/URI, and the rest of the details should hang off that
        # FIXME - (Poor) assumption that file is on same host as Arches instance host config.
        if f_data['url'].startswith("/"):
            f_uri = URIRef(archesproject[f_data['url'][1:]])
        else:
            f_uri = URIRef(archesproject[f_data['url']])
        graph.add((domainnode, URIRef(edge.ontologyproperty), f_uri))
        graph.add((f_uri, RDF.type, URIRef(edge.rangenode.ontologyclass)))
        graph.add((f_uri, DC['format'], Literal(f_data['type'])))
        graph.add((f_uri, RDFS.label, Literal(f_data['name'])))

        # FIXME - improve this ms in timestamp handling code in case of odd OS environments
        # FIXME - Use the timezone settings for export?
        if f_data['lastModified']:
            lm = f_data['lastModified']
            if lm > 9999999999:   # not a straight timestamp, but includes milliseconds
                lm = f_data['lastModified'] / 1000
            graph.add((f_uri, DCTERMS.modified, Literal(datetime.utcfromtimestamp(lm).isoformat()) ))

        if 'size' in f_data:
            add_dimension(graph, f_uri, "file size", "bytes", f_data['size'])
        if 'height' in f_data:
            add_dimension(graph, f_uri, "height", "pixels", f_data['height'])
        if 'width' in f_data:
            add_dimension(graph, f_uri, "width", "pixels", f_data['width'])

# placeholders:
def _handle_domain_value(graph, domainnode, rangenode, edge, tile,
                         domain_tile_data, range_tile_data, graph_uri):
    pass

def _handle_geojson_feature_collection(graph, domainnode, rangenode, edge, tile,
                                       domain_tile_data, range_tile_data, graph_uri):
    pass

def _handle_semantic(graph, domainnode, rangenode, edge, tile, 
                     domain_tile_data, range_tile_data, graph_uri):
    return _handle__default(graph, domainnode, rangenode, edge, tile,
      domain_tile_data, range_tile_data, graph_uri)

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

_output_mapping = {"semantic": _handle_semantic,
                   "number": _handle_number,
                   "boolean": _handle_boolean,
                   "string": _handle_string,
                   "date": _handle_date,
                   "resource-instance": _handle_resource_instance,
                   "concept": _handle_concept,
                   "concept-list": _handle_concept_list,
                   "file-list": _handle_file_list,
                   "resource-instance-list": _handle_resource_instance_list,
                   # Complex Types to potentially tackle later if needed:
                   #"domain-value": _handle_domain_value,
                   #"domain-value-list": _handle_domain_value_list,
                   #"geojson-feature-collection": _handle_geojson_feature_collection,
                   #"csv-chart-json": _handle_csv_chart_json,
                   #"iiif-drawing": _handle_iiif_drawing,
                   #"edtf": _handle_edtf,
                   #"node-value": _handle_node_value,
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