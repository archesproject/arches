import os
import datetime
from format import Writer
from arches.app.models import models
from arches.app.models.system_settings import settings
from rdflib import Namespace
from rdflib import URIRef, Literal
from rdflib import Graph
from rdflib.namespace import RDF, RDFS

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class RdfWriter(Writer):

    def __init__(self, **kwargs):
        self.format = kwargs.pop('format', 'xml')
        super(RdfWriter, self).__init__(**kwargs)

    def write_resources(self, graph_id=None, resourceinstanceids=None):
        super(RdfWriter, self).write_resources(graph_id=graph_id, resourceinstanceids=resourceinstanceids)

        g = self.get_rdf_graph()
        dest = StringIO()
        self.serialize(g, destination=dest, format=self.format)

        return [{'name':self.get_filename(), 'outputfile': dest}]

    def get_rdf_graph(self):

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
                    'rootedges': [],
                    'subgraphs': {}
                }
                graph = models.GraphModel.objects.get(pk=graphid)
                nodegroups = set()
                for node in graph.node_set.all():
                    if node.nodegroup:
                        nodegroups.add(node.nodegroup)
                    if node.istopnode:
                        for edge in get_nodegroup_edges_by_collector_node(node):
                            if edge.rangenode.nodegroup is None:
                                graph_cache[graphid]['rootedges'].append(edge)
                for nodegroup in nodegroups:
                    graph_cache[graphid]['subgraphs'][nodegroup] = {
                        'edges': [],
                        'inedge': None,
                        'parentnode_nodegroup': None
                    }
                    graph_cache[graphid]['subgraphs'][nodegroup]['inedge'] = models.Edge.objects.get(rangenode_id=nodegroup.pk)
                    graph_cache[graphid]['subgraphs'][nodegroup]['parentnode_nodegroup'] = graph_cache[graphid]['subgraphs'][nodegroup]['inedge'].domainnode.nodegroup
                    graph_cache[graphid]['subgraphs'][nodegroup]['edges'] = get_nodegroup_edges_by_collector_node(models.Node.objects.get(pk=nodegroup.pk))

            return graph_cache[graphid]


        def add_edge_to_graph(graph, domainnode, rangenode, edge):
            graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))
            graph.add((rangenode, RDF.type, URIRef(edge.rangenode.ontologyclass)))
            graph.add((domainnode, URIRef(edge.ontologyproperty), rangenode))


        archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
        g = Graph()
        g.bind('archesproject', archesproject, False)

        for resourceinstanceid, tiles in self.resourceinstances.iteritems():
            graphid = tiles[0].resourceinstance.graph_id
            graph_info = get_graph_parts(graphid)

            # add the edges for the group of nodes that include the root (this group of nodes has no nodegroup)
            for edge in graph_cache[graphid]['rootedges']:
                domainnode = archesproject[str(edge.domainnode.pk)]
                rangenode = archesproject[str(edge.rangenode.pk)]
                add_edge_to_graph(g, domainnode, rangenode, edge)

            for tile in tiles:
                # add all the edges for a given tile/nodegroup
                for edge in graph_info['subgraphs'][tile.nodegroup]['edges']:
                    domainnode = archesproject["tile/%s/node/%s" % (str(tile.pk), str(edge.domainnode.pk))]
                    rangenode = archesproject["tile/%s/node/%s" % (str(tile.pk), str(edge.rangenode.pk))]
                    add_edge_to_graph(g, domainnode, rangenode, edge)

                    try:
                        g.add((domainnode, RDF.value, Literal(tile.data[str(edge.domainnode_id)]))) 
                    except:
                        pass    
                    try:
                        g.add((rangenode, RDF.value, Literal(tile.data[str(edge.rangenode_id)]))) 
                    except:
                        pass 

                # add the edge from the parent node to this tile's root node
                # tile has no parent tile, which means the domain node has no tile_id
                if graph_info['subgraphs'][tile.nodegroup]['parentnode_nodegroup'] == None:
                    edge = graph_info['subgraphs'][tile.nodegroup]['inedge']
                    if edge.domainnode.istopnode:
                        domainnode = archesproject['resource/%s' % resourceinstanceid]
                    else:
                        domainnode = archesproject[str(edge.domainnode.pk)]
                    rangenode = archesproject["tile/%s/node/%s" % (str(tile.pk), str(edge.rangenode.pk))]
                    add_edge_to_graph(g, domainnode, rangenode, edge)

                # add the edge from the parent node to this tile's root node
                # tile has a parent tile
                if graph_info['subgraphs'][tile.nodegroup]['parentnode_nodegroup'] != None:
                    edge = graph_info['subgraphs'][tile.nodegroup]['inedge']
                    domainnode = archesproject["tile/%s/node/%s" % (str(tile.parenttile.pk), str(edge.domainnode.pk))]
                    rangenode = archesproject["tile/%s/node/%s" % (str(tile.pk), str(edge.rangenode.pk))]
                    add_edge_to_graph(g, domainnode, rangenode, edge)

        return g

    def get_filename(self):
        iso_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = os.path.join('{0}_{1}.{2}'.format(self.file_prefix, iso_date, 'rdf'))
        return file_name
    
    def serialize(self, g, **kwargs):
        g.serialize(**kwargs)


class JsonLdWriter(RdfWriter):

    def serialize(self, g, **kwargs):
        g.serialize(context=settings.JSON_LD_CONTEXT, **kwargs)