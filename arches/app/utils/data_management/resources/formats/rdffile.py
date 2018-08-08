import os
import re
import json
import datetime
from format import Writer, Reader
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from rdflib import Namespace
from rdflib import URIRef, Literal
from rdflib import Graph
from rdflib.namespace import RDF, RDFS
from pyld.jsonld import compact, frame, from_rdf, to_rdf

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class RdfWriter(Writer):

    def __init__(self, **kwargs):
        self.format = kwargs.pop('format', 'xml')
        super(RdfWriter, self).__init__(**kwargs)

    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        super(RdfWriter, self).write_resources(graph_id=graph_id, resourceinstanceids=resourceinstanceids, **kwargs)

        dest = StringIO()
        g = self.get_rdf_graph()
        g.serialize(destination=dest, format=self.format)

        full_file_name = os.path.join('{0}.{1}'.format(self.file_name, 'rdf'))
        return [{'name':full_file_name, 'outputfile': dest}]

    def get_rdf_graph(self):
        archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
        graph_uri = URIRef(archesproject["graph/%s" % self.graph_id])

        g = Graph()
        g.bind('archesproject', archesproject, False)
        graph_cache = {}

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

        def add_edge_to_graph(graph, domainnode, rangenode, edge, tile):
            graph.add((rangenode, RDF.type, URIRef(edge.rangenode.ontologyclass)))
            graph.add((domainnode, URIRef(edge.ontologyproperty), rangenode))

            if edge.domainnode.istopnode:
                graph.add((domainnode, RDF.type, graph_uri))
                graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))
            else:
                graph.add((domainnode, RDF.type, URIRef(edge.domainnode.ontologyclass)))

            try:
                g.add((domainnode, RDF.value, Literal(tile.data[str(edge.domainnode_id)]))) 
            except:
                pass    
            try:
                g.add((rangenode, RDF.value, Literal(tile.data[str(edge.rangenode_id)]))) 
            except:
                pass 

        for resourceinstanceid, tiles in self.resourceinstances.iteritems():
            graph_info = get_graph_parts(self.graph_id)

            # add the edges for the group of nodes that include the root (this group of nodes has no nodegroup)
            for edge in graph_cache[self.graph_id]['rootedges']:
                domainnode = archesproject[str(edge.domainnode.pk)]
                rangenode = archesproject[str(edge.rangenode.pk)]
                add_edge_to_graph(g, domainnode, rangenode, edge, None)

            for tile in tiles:
                # add all the edges for a given tile/nodegroup
                for edge in graph_info['subgraphs'][tile.nodegroup]['edges']:
                    domainnode = archesproject["tile/%s/node/%s" % (str(tile.pk), str(edge.domainnode.pk))]
                    rangenode = archesproject["tile/%s/node/%s" % (str(tile.pk), str(edge.rangenode.pk))]
                    add_edge_to_graph(g, domainnode, rangenode, edge, tile)

                # add the edge from the parent node to this tile's root node
                # where the tile has no parent tile, which means the domain node has no tile_id
                if graph_info['subgraphs'][tile.nodegroup]['parentnode_nodegroup'] == None:
                    edge = graph_info['subgraphs'][tile.nodegroup]['inedge']
                    if edge.domainnode.istopnode:
                        domainnode = archesproject['resource/%s' % resourceinstanceid]
                    else:
                        domainnode = archesproject[str(edge.domainnode.pk)]
                    rangenode = archesproject["tile/%s/node/%s" % (str(tile.pk), str(edge.rangenode.pk))]
                    add_edge_to_graph(g, domainnode, rangenode, edge, tile)

                # add the edge from the parent node to this tile's root node
                # where the tile has a parent tile
                if graph_info['subgraphs'][tile.nodegroup]['parentnode_nodegroup'] != None:
                    edge = graph_info['subgraphs'][tile.nodegroup]['inedge']
                    domainnode = archesproject["tile/%s/node/%s" % (str(tile.parenttile.pk), str(edge.domainnode.pk))]
                    rangenode = archesproject["tile/%s/node/%s" % (str(tile.pk), str(edge.rangenode.pk))]
                    add_edge_to_graph(g, domainnode, rangenode, edge, tile)


        return g


class JsonLdWriter(RdfWriter):

    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        super(RdfWriter, self).write_resources(graph_id=graph_id, resourceinstanceids=resourceinstanceids, **kwargs)
        g = self.get_rdf_graph()
        value = g.serialize(format='nt')
        js = from_rdf(str(value), options={format:'application/nquads'})

        framing = {
            "@omitDefault": True,
            "@type": "%sgraph/%s" % (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, self.graph_id)
        }

        js = frame(js, framing)

        context = self.graph_model.jsonldcontext
        try:
            context = JSONDeserializer().deserialize(context)
        except ValueError:
            if context == '':
                context = {}
            context = {
                "@context": context
            }
        except AttributeError:
            context = {
                "@context": {}
            }

        out = compact(js, context)
        out = json.dumps(out, indent=kwargs.get('indent', None), sort_keys=True)
        dest = StringIO(out)

        full_file_name = os.path.join('{0}.{1}'.format(self.file_name, 'jsonld'))
        return [{'name':full_file_name, 'outputfile': dest}]


class JsonLdReader(Reader):
    def read_resource(self, data):
        rdf = to_rdf(data, {'format': 'application/n-quads'})
        g = Graph().parse(format='nquads', data=rdf)
        tiles = {}

        for su,p,ob in g.triples( (None,  RDF.value, None) ):
            print "%s is a %s"%(su,ob)
            match = re.match(r'.*?/tile/(?P<tileid>%s)/node/(?P<nodeid>%s)' % (settings.UUID_REGEX, settings.UUID_REGEX), str(su))
            if match:
                if match.group('tileid') not in tiles:
                    tiles[match.group('tileid')] = {} 

                tiles[match.group('tileid')][match.group('nodeid')] = str(ob)

        for tileid, tile_data in tiles.iteritems():
            Tile.objects.filter(pk=tileid).update(data=tile_data)
            # tile, created = Tile.objects.update_or_create(
            #     tileid = tileid,
            #     defaults = {
            #         'data': tile_data
            #     }
            # )

        print tiles