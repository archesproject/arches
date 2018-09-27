import os
import re
import json
import uuid
import datetime
from django.core.urlresolvers import reverse
from format import Writer, Reader
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.graph import Graph as GraphProxy
from arches.app.models.tile import Tile
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
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
        return [{'name': full_file_name, 'outputfile': dest}]

    def get_rdf_graph(self):
        archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
        graph_uri = URIRef(archesproject[reverse('graph', args=[self.graph_id]).lstrip('/')])

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
                    graph_cache[graphid]['subgraphs'][nodegroup][
                        'inedge'] = models.Edge.objects.get(rangenode_id=nodegroup.pk)
                    graph_cache[graphid]['subgraphs'][nodegroup]['parentnode_nodegroup'] = graph_cache[
                        graphid]['subgraphs'][nodegroup]['inedge'].domainnode.nodegroup
                    graph_cache[graphid]['subgraphs'][nodegroup][
                        'edges'] = get_nodegroup_edges_by_collector_node(models.Node.objects.get(pk=nodegroup.pk))

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
                g.add((domainnode, RDF.value, Literal(JSONSerializer().serialize(tile.data[str(edge.domainnode_id)]))))
            except:
                pass
            try:
                g.add((rangenode, RDF.value, Literal(JSONSerializer().serialize(tile.data[str(edge.rangenode_id)]))))
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
                        domainnode = archesproject[reverse('resources', args=[resourceinstanceid]).lstrip('/')]
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
        js = from_rdf(str(value), options={format: 'application/nquads'})

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
        return [{'name': full_file_name, 'outputfile': dest}]


class JsonLdReader(Reader):

    def __init__(self):
        self.tiles = {}
        self.errors = {}
        self.resources = []
        self.use_ids = False
        self.ontologyproperties = models.Edge.objects.values_list('ontologyproperty', flat=True).distinct()

    def get_graph_id(self, strs_to_test):
        if not isinstance(strs_to_test, list):
            strs_to_test = [strs_to_test]
        for str_to_test in strs_to_test:
            match = re.match(r'.*?%sgraph/(?P<graphid>%s)' %
                             (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, settings.UUID_REGEX), str_to_test)
            if match:
                return match.group('graphid')
        return None

    def get_resource_id(self, strs_to_test):
        if not isinstance(strs_to_test, list):
            strs_to_test = [strs_to_test]
        for str_to_test in strs_to_test:
            match = re.match(r'.*?%sresources/(?P<resourceid>%s)' %
                             (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, settings.UUID_REGEX), str_to_test)
            if match:
                return match.group('resourceid')
        return None

    def read_resource(self, data, use_ids=False):
        self.use_ids = use_ids
        if not isinstance(data, list):
            data = [data]

        for jsonld in data:
            self.errors = {}
            graphid = self.get_graph_id(jsonld["@type"])
            if graphid:
                graph = GraphProxy.objects.get(graphid=graphid)
                graphtree = graph.get_tree()
                if use_ids == True:
                    resourceinstanceid = self.get_resource_id(jsonld["@id"])
                    if resourceinstanceid is None:
                        raise Exception(
                            'The @id of the resource was not supplied, or was null, or the URI was not correctly formatted')
                    resource = Resource.objects.get(pk=resourceinstanceid)
                else:
                    resource = Resource()
                    resource.graph_id = graphid
                self.resolve_node_ids(jsonld, graph=graphtree, resource=resource)
                self.resources.append(resource)

        return data

    class AmbiguousGraphException(Exception):

        def __init__(self):
            # self.expression = expression
            self.message = 'The target graph is ambiguous, please supply node ids in the jsonld to disabmiguate.'

    class DataDoesNotMatchGraphException(Exception):

        def __init__(self):
            # self.expression = expression
            self.message = 'A node in the supplied data does not match any node in the target graph. '

            # check that the current json-ld @type is unique among nodes within the graph at that level of depth
            # if it's unique apply the node id from the graph to the json-ld value
            # if it's not unique then:
            #     check the children @types and compare to teh graphs children, repeat until you find a match

    def findOntologyProperties(self, o):
        keys = []
        try:
            for key in o.keys():
                if key in self.ontologyproperties:
                    keys.append(key)
        except:
            pass

        return keys

    def findBranch(self, nodes, ontology_property, jsonld):
        """
            EXAMPLE JSONLD GRAPH:
            --------------------
            {
                "@id": "http://localhost:8000/tile/eed92cf9-b9cd-4e99-9e88-8fb34a0be257/node/e456023d-fa36-11e6-9e3e-026d961c88e6",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E12_Production",
                "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as": [
                    {
                        "@id": "http://localhost:8000/tile/9fcd9141-930c-4303-b176-78480efbd3d9/node/e4560237-fa36-11e6-9e3e-026d961c88e6",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E17_Type_Assignment",
                        "http://www.cidoc-crm.org/cidoc-crm/P42_assigned": [
                            {
                                "@id": "http://localhost:8000/tile/9fcd9141-930c-4303-b176-78480efbd3d9/node/e456024f-fa36-11e6-9e3e-026d961c88e6",
                                "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                                "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "[u'dfc1fa9b-e3c8-459d-a3fa-d65e1443b9e7']"
                            },
                            {
                                "@id": "http://localhost:8000/tile/9fcd9141-930c-4303-b176-78480efbd3d9/node/e4560246-fa36-11e6-9e3e-026d961c88e6",
                                "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                                "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "a18ed9a3-4924-4cf0-a9a7-82d8c3aefbe0"
                            }
                        ],
                    }
                ]
            }
        """
        if not isinstance(jsonld, list):
            jsonld = [jsonld]

        for jsonld_graph in jsonld:
            # print ""
            # print ""
            # print "searching for branch %s --> %s" %
            # (ontology_property.split('/')[-1], jsonld_graph['@type'].split('/')[-1])
            found = []
            nodes_copy = set()
            invalid_nodes = set()

            # print jsonld_graph
            # try:
            #     nodeid = jsonld_graph['@archesNodeId']
            #     print "-------"
            #     print nodeid
            #     # import ipdb
            #     # ipdb.set_trace()
            #     for node in nodes:
            #         print str(node['node'].pk)
            #         if str(node['node'].pk) == nodeid:
            #             valid_nodes = set([(node['node'].name, node['node'].pk)])
            #             print 'made it'

            # except KeyError:

            # try to find a node in the graph among a bunch of sibling nodes that has the same incoming edge (propertyclass) as
            # the edge/node combination we're searching for from the json-ld graph
            for node in nodes:
                if node['parent_edge'].ontologyproperty == ontology_property and node['node'].ontologyclass == jsonld_graph['@type']:
                    # print "found %s" % node['node'].name
                    nodes_copy.add((node['node'].name, node['node'].pk))
                    found.append(node)
                else:
                    invalid_nodes.add((node['node'].name, node['node'].pk))
                    pass

            # print 'found %s branches' % len(found)
            if len(found) == 0:
                # print 'branch not found'
                raise self.DataDoesNotMatchGraphException()

            # if len(self.findOntologyProperties(jsonld_graph)) == 0:
                # print 'at a leaf -- unwinding'

            for ontology_prop in self.findOntologyProperties(jsonld_graph):
                for found_node in found:
                    try:
                        # print 'now searching children of %s node' % found_node['node'].name
                        branch = self.findBranch(found_node['children'], ontology_prop, jsonld_graph[ontology_prop])
                    except self.DataDoesNotMatchGraphException as e:
                        found_node['remove'] = True
                        invalid_nodes.add((found_node['node'].name, found_node['node'].pk))
                    except self.AmbiguousGraphException as e:
                        # print 'threw AmbiguousGraphException'
                        # print nodes_copy
                        pass

            valid_nodes = nodes_copy.difference(invalid_nodes)

            if len(valid_nodes) == 1:
                # print 'branch found'
                # print valid_nodes
                valid_node = valid_nodes.pop()
                for node in nodes:
                    if node['node'].pk == valid_node[1]:
                        return node
            elif len(valid_nodes) > 1:
                raise self.AmbiguousGraphException()
            else:
                raise self.DataDoesNotMatchGraphException()

    def resolve_node_ids(self, jsonld, ontology_prop=None, graph=None, parent_node=None, tileid=None, parent_tileid=None, resource=None):
        # print "-------------------"
        if not isinstance(jsonld, list):
            jsonld = [jsonld]
        # print len(jsonld)

        parent_tileid = tileid
        for jsonld_node in jsonld:
            if parent_node is not None:
                try:
                    # print 'find branch'
                    # print jsonld_node

                    branch = None
                    if self.use_ids:
                        try:
                            match = re.match(r'.*?/tile/(?P<tileid>%s)/node/(?P<nodeid>%s)' %
                                             (settings.UUID_REGEX, settings.UUID_REGEX), str(jsonld_node['@id']))
                            if match:
                                tileid = match.group('tileid')
                                for node in parent_node['children']:
                                    if str(node['node'].pk) == match.group('nodeid'):
                                        branch = node
                        except:
                            pass

                    if branch is None:
                        branch = self.findBranch(parent_node['children'], ontology_prop, jsonld_node)
                        if branch['node'].nodegroup != parent_node['node'].nodegroup:
                            tileid = uuid.uuid4()

                except self.DataDoesNotMatchGraphException as e:
                    # print 'DataDoesNotMatchGraphException'
                    self.errors['DataDoesNotMatchGraphException'] = e
                    branch = None

                except self.AmbiguousGraphException as e:
                    # print 'AmbiguousGraphException'
                    self.errors['AmbiguousGraphException'] = e
                    branch = None
            else:
                branch = graph

            ontology_properties = self.findOntologyProperties(jsonld_node)

            if branch is not None:
                if branch != graph:
                    # jsonld_node['@archesid'] = '%stile/%s/node/%s' % (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, tileid, branch['node'].nodeid)

                    if tileid not in self.tiles:
                        self.tiles[tileid] = Tile(tileid=tileid, parenttile_id=parent_tileid,
                                                  nodegroup_id=branch['node'].nodegroup_id, data={})
                        if parent_tileid is None:
                            resource.tiles.append(self.tiles[tileid])
                        else:
                            self.tiles[parent_tileid].tiles.append(self.tiles[tileid])

                    if str(RDF.value) in jsonld_node:
                        value = jsonld_node[str(RDF.value)]
                        try:
                            value = JSONDeserializer().deserialize(value)
                        except:
                            pass
                        self.tiles[tileid].data[str(branch['node'].nodeid)] = value

                if len(ontology_properties) > 0:
                    for ontology_property in ontology_properties:
                        # print jsonld_node['@type']
                        # print ontology_property
                        self.resolve_node_ids(jsonld_node[ontology_property], ontology_prop=ontology_property,
                                              graph=None, parent_node=branch, tileid=tileid, parent_tileid=parent_tileid, resource=resource)
        return jsonld
