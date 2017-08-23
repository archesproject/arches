import os
import datetime
from format import Writer
from arches.app.models import models
from rdflib import Namespace
from rdflib import URIRef, BNode, Literal
from rdflib import Graph, Dataset
from rdflib.namespace import RDF, RDFS

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class RdfWriter(Writer):

    def __init__(self):
        self.format = 'rdf-xml'
        super(RdfWriter, self).__init__()

    # def transform_value_for_export(self, datatype, value, concept_export_value_type, node):
    #     datatype_instance = self.datatype_factory.get_instance(datatype)
    #     value = datatype_instance.transform_export_values(value, concept_export_value_type=concept_export_value_type, node=node)
    #     return value

    def write_resources(self, resources, resource_export_configs=None, single_file=False):
        rdf_for_export = []
        ds = Dataset()

        n = Namespace('http://archesproject.com/')
        crm = Namespace('http://cidoc-crm/')

        ds.bind('archesproject', n, False)
        ds.bind('crm', crm, False)

        cache = {}

        def get_nodegroup_edges_by_collector_node(node):
            edges = []
            nodegroup = node.nodegroup
            def getchildedges(node):
                for edge in models.Edge.objects.filter(domainnode=node):
                    if nodegroup == edge.rangenode.nodegroup:
                        edges.append(edge)
                        getchildedges(edge.rangenode)

            getchildedges(node)
            return edges

        graph_cache = {}
        def get_graph_parts(graphid):
            if graphid not in graph_cache:
                graph_cache[graphid] = {
                    'rootgraph': None,
                    'subgraphs': {}
                }
                graph = models.GraphModel.objects.get(pk=graphid)
                nodegroups = set()
                for node in graph.node_set.all():
                    if node.nodegroup:
                        nodegroups.add(node.nodegroup)
                    if node.istopnode:
                        root_edges = get_nodegroup_edges_by_collector_node(node)
                        print root_edges
                for nodegroup in nodegroups:
                    graph_cache[graphid]['subgraphs'][nodegroup] = {
                        'edges': [],
                        'inedge': None,
                        'parentnode_nodegroup': None
                    }
                    graph_cache[graphid]['subgraphs'][nodegroup]['inedge'] = models.Edge.objects.get(rangenode_id=nodegroup.pk)
                    graph_cache[graphid]['subgraphs'][nodegroup]['parentnode_nodegroup'] = graph_cache[graphid]['subgraphs'][nodegroup]['inedge'].domainnode.nodegroup

                    # def getchildedges(node):
                    #     for edge in models.Edge.objects.filter(domainnode=node):
                    #         if nodegroup == node.nodegroup:
                    #             graph_cache[graphid]['subgraphs'][nodegroup]['edges'].append(edge)
                    #         getchildedges(edge.rangenode)

                    #getchildedges(models.Node.objects.get(pk=nodegroup.pk))
                    graph_cache[graphid]['subgraphs'][nodegroup]['edges'] = get_nodegroup_edges_by_collector_node(models.Node.objects.get(pk=nodegroup.pk))


            return graph_cache[graphid]

        resourceinstance_id = 'a755e16b-7e2a-11e7-8810-14109fd34195'
        g = ds.graph(URIRef('http:/archesproject.com/resource/%s' % resourceinstance_id))
        resourceinstance = models.ResourceInstance.objects.get(pk=resourceinstance_id)
        graph_info = get_graph_parts(resourceinstance.graph_id)
        for tile in models.TileModel.objects.filter(resourceinstance=resourceinstance):

            for edge in graph_info['subgraphs'][tile.nodegroup]['edges']:
                domainnode = n["%s--%s" % (str(edge.domainnode.pk), str(tile.pk))] #BNode()
                rangenode = n["%s--%s" % (str(edge.rangenode.pk), str(tile.pk))] #BNode()
                g.add((domainnode, RDF.type, crm[edge.domainnode.ontologyclass]))
                g.add((rangenode, RDF.type, crm[edge.rangenode.ontologyclass]))
               
                g.add((domainnode, crm[edge.ontologyproperty], rangenode))
                try:
                    g.add((domainnode, RDF.value, Literal(tile.data[str(edge.domainnode_id)]))) 
                except:
                    pass    
                try:
                    g.add((rangenode, RDF.value, Literal(tile.data[str(edge.rangenode_id)]))) 
                except:
                    pass    

            if graph_info['subgraphs'][tile.nodegroup]['parentnode_nodegroup'] == None:
                edge = graph_info['subgraphs'][tile.nodegroup]['inedge']
                domainnode = n[str(edge.domainnode.pk)] #BNode()
                rangenode = n["%s--%s" % (str(edge.rangenode.pk), str(tile.pk))] #BNode()
                g.add((domainnode, RDF.type, crm[edge.domainnode.ontologyclass]))
                g.add((rangenode, RDF.type, crm[edge.rangenode.ontologyclass]))
                g.add((domainnode, crm[edge.ontologyproperty], rangenode))

            if graph_info['subgraphs'][tile.nodegroup]['parentnode_nodegroup'] != None:
                edge = graph_info['subgraphs'][tile.nodegroup]['inedge']
                domainnode = n["%s--%s" % (str(edge.domainnode.pk), str(tile.parenttile.pk))] #BNode()
                rangenode = n["%s--%s" % (str(edge.rangenode.pk), str(tile.pk))] #BNode()
                g.add((domainnode, RDF.type, crm[edge.domainnode.ontologyclass]))
                g.add((rangenode, RDF.type, crm[edge.rangenode.ontologyclass]))
                g.add((domainnode, crm[edge.ontologyproperty], rangenode))


        name_prefix = resource_export_configs[0]['resource_model_name']
        iso_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = os.path.join('{0}_{1}.{2}'.format(name_prefix, iso_date, 'rdf'))

        dest = StringIO()
        dest.write(g.serialize(format='pretty-xml'))
        rdf_for_export.append({'name':file_name, 'outputfile': dest})

        # print g.connected()

