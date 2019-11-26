import os
import re
import json
import uuid
import datetime
import logging
from io import StringIO
from django.urls import reverse
from .format import Writer, Reader
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.graph import Graph as GraphProxy
from arches.app.models.tile import Tile
from arches.app.models.concept import Concept
from arches.app.models.system_settings import settings
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from rdflib import Namespace
from rdflib import URIRef, Literal
from rdflib import ConjunctiveGraph as Graph
from rdflib.namespace import RDF, RDFS
from pyld.jsonld import compact, frame, from_rdf, to_rdf, expand


class RdfWriter(Writer):
    def __init__(self, **kwargs):
        self.format = kwargs.pop("format", "xml")
        self.logger = logging.getLogger(__name__)
        super(RdfWriter, self).__init__(**kwargs)

    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        super(RdfWriter, self).write_resources(graph_id=graph_id, resourceinstanceids=resourceinstanceids, **kwargs)

        dest = StringIO()
        g = self.get_rdf_graph()
        g.serialize(destination=dest, format=self.format)

        full_file_name = os.path.join("{0}.{1}".format(self.file_name, "rdf"))
        return [{"name": full_file_name, "outputfile": dest}]

    def get_rdf_graph(self):
        archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
        graph_uri = URIRef(archesproject[reverse("graph", args=[self.graph_id]).lstrip("/")])
        self.logger.debug("Using `{0}` for Arches URI namespace".format(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT))
        self.logger.debug("Using `{0}` for Graph URI".format(graph_uri))

        g = Graph()
        g.bind("archesproject", archesproject, False)
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
                    "rootedges": [],
                    "subgraphs": {},
                    "nodedatatypes": {},
                }
                graph = models.GraphModel.objects.get(pk=graphid)
                nodegroups = set()
                for node in graph.node_set.all():
                    graph_cache[graphid]["nodedatatypes"][str(node.nodeid)] = node.datatype
                    if node.nodegroup:
                        nodegroups.add(node.nodegroup)
                    if node.istopnode:
                        for edge in get_nodegroup_edges_by_collector_node(node):
                            if edge.rangenode.nodegroup is None:
                                graph_cache[graphid]["rootedges"].append(edge)
                for nodegroup in nodegroups:
                    graph_cache[graphid]["subgraphs"][nodegroup] = {"edges": [], "inedge": None, "parentnode_nodegroup": None}
                    graph_cache[graphid]["subgraphs"][nodegroup]["inedge"] = models.Edge.objects.get(rangenode_id=nodegroup.pk)
                    graph_cache[graphid]["subgraphs"][nodegroup]["parentnode_nodegroup"] = graph_cache[graphid]["subgraphs"][nodegroup][
                        "inedge"
                    ].domainnode.nodegroup
                    graph_cache[graphid]["subgraphs"][nodegroup]["edges"] = get_nodegroup_edges_by_collector_node(
                        models.Node.objects.get(pk=nodegroup.pk)
                    )

            return graph_cache[graphid]

        def add_edge_to_graph(graph, domainnode, rangenode, edge, tile, graph_info):
            pkg = {}
            pkg["d_datatype"] = graph_info["nodedatatypes"].get(str(edge.domainnode.pk))
            dom_dt = self.datatype_factory.get_instance(pkg["d_datatype"])
            # Don't process any further if the domain datatype is a literal
            if dom_dt.is_a_literal_in_rdf():
                return

            pkg["r_datatype"] = graph_info["nodedatatypes"].get(str(edge.rangenode.pk))
            pkg["range_tile_data"] = None
            pkg["domain_tile_data"] = None
            if str(edge.rangenode_id) in tile.data:
                pkg["range_tile_data"] = tile.data[str(edge.rangenode_id)]
            if str(edge.domainnode_id) in tile.data:
                pkg["domain_tile_data"] = tile.data[str(edge.domainnode_id)]

            rng_dt = self.datatype_factory.get_instance(pkg["r_datatype"])
            pkg["d_uri"] = dom_dt.get_rdf_uri(domainnode, pkg["domain_tile_data"], "d")
            pkg["r_uri"] = rng_dt.get_rdf_uri(rangenode, pkg["range_tile_data"], "r")

            # Domain node is NOT a literal value in the RDF representation, so will have a type:
            if type(pkg["d_uri"]) == list:
                for duri in pkg["d_uri"]:
                    graph.add((duri, RDF.type, URIRef(edge.domainnode.ontologyclass)))
            else:
                graph.add((pkg["d_uri"], RDF.type, URIRef(edge.domainnode.ontologyclass)))

            # Use the range node's datatype.to_rdf() method to generate an RDF representation of it
            # and add its triples to the core graph

            # FIXME: some datatypes have their URI calculated from _tile_data (e.g. concept)
            # ... if there is a list of these, then all of the permutations will happen
            # ... as the matrix below re-processes all URIs against all _tile_data entries :(
            if type(pkg["d_uri"]) == list:
                mpkg = pkg.copy()
                for d in pkg["d_uri"]:
                    mpkg["d_uri"] = d
                    if type(pkg["r_uri"]) == list:
                        npkg = mpkg.copy()
                        for r in pkg["r_uri"]:
                            # compute matrix of n * m
                            npkg["r_uri"] = r
                            graph += rng_dt.to_rdf(npkg, edge)
                    else:
                        # iterate loop on m * 1
                        graph += rng_dt.to_rdf(mpkg, edge)
            elif type(pkg["r_uri"]) == list:
                npkg = pkg.copy()
                for r in pkg["r_uri"]:
                    # compute matrix of 1 * m
                    npkg["r_uri"] = r
                    graph += rng_dt.to_rdf(npkg, edge)
            else:
                # both are single, 1 * 1
                graph += rng_dt.to_rdf(pkg, edge)

        for resourceinstanceid, tiles in self.resourceinstances.items():
            graph_info = get_graph_parts(self.graph_id)

            # add the edges for the group of nodes that include the root (this group of nodes has no nodegroup)
            for edge in graph_cache[self.graph_id]["rootedges"]:
                domainnode = archesproject[str(edge.domainnode.pk)]
                rangenode = archesproject[str(edge.rangenode.pk)]
                add_edge_to_graph(g, domainnode, rangenode, edge, None, graph_info)

            for tile in tiles:
                # add all the edges for a given tile/nodegroup
                for edge in graph_info["subgraphs"][tile.nodegroup]["edges"]:
                    domainnode = archesproject["tile/%s/node/%s" % (str(tile.pk), str(edge.domainnode.pk))]
                    rangenode = archesproject["tile/%s/node/%s" % (str(tile.pk), str(edge.rangenode.pk))]
                    add_edge_to_graph(g, domainnode, rangenode, edge, tile, graph_info)

                # add the edge from the parent node to this tile's root node
                # where the tile has no parent tile, which means the domain node has no tile_id
                if graph_info["subgraphs"][tile.nodegroup]["parentnode_nodegroup"] is None:
                    edge = graph_info["subgraphs"][tile.nodegroup]["inedge"]
                    if edge.domainnode.istopnode:
                        domainnode = archesproject[reverse("resources", args=[resourceinstanceid]).lstrip("/")]
                    else:
                        domainnode = archesproject[str(edge.domainnode.pk)]
                    rangenode = archesproject["tile/%s/node/%s" % (str(tile.pk), str(edge.rangenode.pk))]
                    add_edge_to_graph(g, domainnode, rangenode, edge, tile, graph_info)

                # add the edge from the parent node to this tile's root node
                # where the tile has a parent tile
                if graph_info["subgraphs"][tile.nodegroup]["parentnode_nodegroup"] is not None:
                    edge = graph_info["subgraphs"][tile.nodegroup]["inedge"]
                    domainnode = archesproject["tile/%s/node/%s" % (str(tile.parenttile.pk), str(edge.domainnode.pk))]
                    rangenode = archesproject["tile/%s/node/%s" % (str(tile.pk), str(edge.rangenode.pk))]
                    add_edge_to_graph(g, domainnode, rangenode, edge, tile, graph_info)
        return g


class JsonLdWriter(RdfWriter):
    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        super(RdfWriter, self).write_resources(graph_id=graph_id, resourceinstanceids=resourceinstanceids, **kwargs)
        g = self.get_rdf_graph()
        value = g.serialize(format="nquads").decode("utf-8")

        # print(f"Got graph: {value}")
        js = from_rdf(value, {"format": "application/nquads", "useNativeTypes": True})

        assert len(resourceinstanceids) == 1  # currently, this should be limited to a single top resource

        archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
        resource_inst_uri = archesproject[reverse("resources", args=[resourceinstanceids[0]]).lstrip("/")]

        context = self.graph_model.jsonldcontext
        framing = {"@omitDefault": True, "@omitGraph": False, "@id": str(resource_inst_uri)}

        if context:
            framing["@context"] = context

        js = frame(js, framing)

        try:
            context = JSONDeserializer().deserialize(context)
        except ValueError:
            if context == "":
                context = {}
            context = {"@context": context}
        except AttributeError:
            context = {"@context": {}}

        # Currently omitGraph is not processed by pyLd, but data is compacted
        # simulate omitGraph:
        if "@graph" in js and len(js["@graph"]) == 1:
            # merge up
            for (k, v) in list(js["@graph"][0].items()):
                js[k] = v
            del js["@graph"]

        out = json.dumps(js, indent=kwargs.get("indent", None), sort_keys=True)
        dest = StringIO(out)

        full_file_name = os.path.join("{0}.{1}".format(self.file_name, "jsonld"))
        return [{"name": full_file_name, "outputfile": dest}]


class JsonLdReader(Reader):
    def __init__(self):
        super(JsonLdReader, self).__init__()
        self.tiles = {}
        self.errors = {}
        self.resources = []
        self.use_ids = False
        self.resource_model_root_classes = set()
        self.non_unique_classes = set()
        self.graph_id_lookup = {}
        self.root_ontologyclass_lookup = {}
        self.jsonld_doc = None
        self.graphtree = None
        self.logger = logging.getLogger(__name__)
        for graph in models.GraphModel.objects.filter(isresource=True):
            node = models.Node.objects.get(graph_id=graph.pk, istopnode=True)
            self.graph_id_lookup[node.ontologyclass] = graph.pk
            self.root_ontologyclass_lookup[str(graph.pk)] = node.ontologyclass
            if node.ontologyclass in self.resource_model_root_classes:
                # make a note of non-unique root classes
                self.non_unique_classes.add(node.ontologyclass)
            else:
                self.resource_model_root_classes.add(node.ontologyclass)
        self.resource_model_root_classes = self.resource_model_root_classes - self.non_unique_classes
        self.ontologyproperties = models.Edge.objects.values_list("ontologyproperty", flat=True).distinct()
        self.logger.info("Initialized JsonLdReader")
        self.logger.debug("Found {0} Non-unique root classes".format(len(self.non_unique_classes)))
        self.logger.debug("Found {0} Resource Model Root classes".format(len(self.resource_model_root_classes)))
        self.logger.debug("Resource Model Root classes: {0}".format("\n".join(list(map(str, self.resource_model_root_classes)))))

    def get_graph_id(self, root_ontologyclass):
        if root_ontologyclass in self.resource_model_root_classes:
            return self.graph_id_lookup[root_ontologyclass]
        else:
            self.logger.info(
                "Incoming Root Ontology class `{0}` not found within the list of Resource Model Root Classes".format(root_ontologyclass)
            )
        return None

    def get_resource_id(self, strs_to_test):
        if not isinstance(strs_to_test, list):
            strs_to_test = [strs_to_test]
        for str_to_test in strs_to_test:
            match = re.match(
                r".*?%sresources/(?P<resourceid>%s)" % (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, settings.UUID_REGEX), str_to_test
            )
            if match:
                return match.group("resourceid")
            else:
                self.logger.debug("Valid resourceid not found within `{0}`".format(str_to_test))
        return None

    def read_resource(self, data, use_ids=False, resourceid=None, graphid=None):
        self.use_ids = use_ids
        if not isinstance(data, list):
            data = [data]

        for jsonld in data:
            self.errors = {}
            # FIXME: This should use a cache of the context
            jsonld = expand(jsonld)[0]
            print(jsonld)
            self.jsonld_doc = jsonld
            if graphid is None:
                graphid = self.get_graph_id(jsonld["@type"][0])
                self.logger.debug("graphid is not set. Using the @type value instead: {0}".format(jsonld["@type"][0]))
            if graphid:
                graph = GraphProxy.objects.get(graphid=graphid)
                self.graphtree = graph.get_tree()
                if use_ids == True:
                    resourceinstanceid = self.get_resource_id(jsonld["@id"])
                    if resourceinstanceid is None:
                        self.logger.error("The @id of the resource was not supplied, was null or URI was not correctly formatted")
                        raise Exception("The @id of the resource was not supplied, was null or URI was not correctly formatted")
                    self.logger.debug("Resource instance ID found: {0}".format(resourceinstanceid))
                    resource = Resource.objects.get(pk=resourceinstanceid)
                else:
                    self.logger.debug("`use_ids` setting is set to False, creating new Resource Instance IDs on import")
                    resource = Resource()
                    resource.graph_id = graphid
                    resource.pk = resourceid

                self.add_node_ids(jsonld)
                print(jsonld)
                # print(self.get_paths(self.graphtree))
                # print(self.get_jsonld_paths(jsonld))
                # self.find_node(self.graphtree, jsonld)
                self.resolve_jsonld_doc(resource)
                # self.resolve_node_ids(jsonld, graph=self.graphtree, resource=resource)
                self.resources.append(resource)

        return data

    class AmbiguousGraphException(Exception):
        def __init__(self):
            self.message = "The target graph is ambiguous, please supply node ids in the jsonld to disabmiguate."

    class DataDoesNotMatchGraphException(Exception):
        def __init__(self):
            self.message = "A node in the supplied data does not match any node in the target graph. "

    def findOntologyProperties(self, o):
        keys = []
        try:
            for key in list(o.keys()):
                if key in self.ontologyproperties:
                    keys.append(key)
        except:
            pass
        # self.logger.debug("    findOntologyProperties -> {0}".format("\n".join(map(str, keys))))
        return keys

    # def findBranch(self, nodes, ontology_property, jsonld):
    #     """
    #         EXAMPLE JSONLD GRAPH:
    #         --------------------
    #         {
    #             "@id": "http://localhost:8000/tile/eed92cf9-b9cd-4e99-9e88-8fb34a0be257/node/e456023d-fa36-11e6-9e3e-026d961c88e6",
    #             "@type": "http://www.cidoc-crm.org/cidoc-crm/E12_Production",
    #             "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as": [
    #                 {
    #                     "@id": "http://localhost:8000/tile/9fcd9141-930c-4303-b176-78480efbd3d9/node/e4560237-fa36-11e6-9e3e-026d961c88e6",
    #                     "@type": "http://www.cidoc-crm.org/cidoc-crm/E17_Type_Assignment",
    #                     "http://www.cidoc-crm.org/cidoc-crm/P42_assigned": [
    #                         {
    #                             "@id": "http://localhost:8000/tile/9fcd9141-930c-4303-b176-78480efbd3d9/node/e456024f-fa36-11e6-9e3e-026d961c88e6",
    #                             "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
    #                             "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "[u'dfc1fa9b-e3c8-459d-a3fa-d65e1443b9e7']"
    #                         },
    #                         {
    #                             "@id": "http://localhost:8000/tile/9fcd9141-930c-4303-b176-78480efbd3d9/node/e4560246-fa36-11e6-9e3e-026d961c88e6",
    #                             "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
    #                             "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "a18ed9a3-4924-4cf0-a9a7-82d8c3aefbe0"
    #                         }
    #                     ],
    #                 }
    #             ]
    #         }
    #     """

    #     self.logger.debug(
    #         "entered 'findBranch' with {0} nodes, ontology_property='{1}' and jsonld_fragment:".format(len(nodes), str(ontology_property))
    #     )
    #     self.logger.debug("    " + str(jsonld))

    #     if not isinstance(jsonld, list):
    #         jsonld = [jsonld]

    #     for jsonld_graph in jsonld:
    #         if "@type" in jsonld_graph:
    #             self.logger.debug(
    #                 "searching for branch %s --> %s" % (ontology_property.split("/")[-1], jsonld_graph["@type"][0].split("/")[-1])
    #             )
    #         found = []
    #         nodes_copy = set()
    #         invalid_nodes = set()

    #         # print jsonld_graph
    #         # try:
    #         #     nodeid = jsonld_graph['@archesNodeId']
    #         #     for node in nodes:
    #         #         print(str(node['node'].pk))
    #         #         if str(node['node'].pk) == nodeid:
    #         #             valid_nodes = set([(node['node'].name, node['node'].pk)])
    #         # except KeyError as e:
    #         # try to find a node in the graph among a bunch of sibling nodes that has the same incoming edge (propertyclass) as
    #         # the edge/node combination we're searching for from the json-ld graph

    #         self.logger.info("Trying to match jsonld_graph fragment:")
    #         self.logger.debug(str(jsonld_graph))
    #         for node in nodes:
    #             self.logger.debug("Checking model class {0}".format(node["node"].ontologyclass))
    #             if "@type" in jsonld_graph:
    #                 self.logger.debug("  node['parent_edge'].ontologyproperty: %r" % node["parent_edge"].ontologyproperty)
    #                 self.logger.debug(
    #                     "node['parent_edge'].ontologyproperty == ontology_property: %r" % node["parent_edge"].ontologyproperty
    #                     == ontology_property
    #                 )
    #                 self.logger.debug("node['node'].ontologyclass: %r" % node["node"].ontologyclass)
    #                 self.logger.debug(
    #                     "node['node'].ontologyclass == jsonld_graph['@type'][0]: %r" % node["node"].ontologyclass
    #                     == jsonld_graph["@type"][0]
    #                 )

    #             if "@type" in jsonld_graph:
    #                 if node["parent_edge"].ontologyproperty == ontology_property and (
    #                     (type(jsonld_graph["@type"]) == list and node["node"].ontologyclass == jsonld_graph["@type"][0])
    #                     or node["node"].ontologyclass == jsonld_graph["@type"]
    #                 ):
    #                     self.logger.debug("found {0}".format(node["node"].name))
    #                     nodes_copy.add((node["node"].name, node["node"].pk))
    #                     found.append(node)
    #                 else:
    #                     self.logger.debug(
    #                         "Node type ontologyclass and property {0}, {1} is not a match".format(
    #                             node["node"].ontologyclass, node["parent_edge"].ontologyproperty
    #                         )
    #                     )
    #                     invalid_nodes.add((node["node"].name, node["node"].pk))

    #             if "@value" in jsonld_graph:
    #                 if node["parent_edge"].ontologyproperty == ontology_property:
    #                     # print node['parent_edge'].ontologyproperty == ontology_property and node['node'].ontologyclass == str(RDFS.Literal)
    #                     # print node['node'].name
    #                     # print node['node'].ontologyclass
    #                     # print node['parent_edge'].ontologyproperty
    #                     # print ontology_property
    #                     # print "found %s" % node['node'].name
    #                     nodes_copy.add((node["node"].name, node["node"].pk))
    #                     found.append(node)

    #         # see https://github.com/archesproject/arches/issues/5126
    #         # check to see if the found graph nodes are concepts
    #         # if all the found graph nodes are concepts then remove any nodes from found where the value
    #         # being saved isn't in the nodes concept collection
    #         if len(found) > 1:
    #             found_nodes_are_concepts = True
    #             for found_node in found:
    #                 if not (found_node["node"].datatype == "concept" or found_node["node"].datatype == "concept-list"):
    #                     found_nodes_are_concepts = False

    #             if found_nodes_are_concepts:
    #                 new_found = []
    #                 nodes_copy = set()
    #                 concept_val = jsonld_graph["http://www.w3.org/2000/01/rdf-schema#label"]
    #                 if concept_val:
    #                     if isinstance(concept_val, list):
    #                         concept_val = concept_val[0]["@value"]
    #                     else:
    #                         concept_val = concept_val["@value"]
    #                 for node in found:
    #                     collection = node["node"].config["rdmCollection"]
    #                     # NOTE: these collections might be cached for better performance?
    #                     edges = Concept().get_child_collections(collection, columns="valueto")
    #                     concept_labels = [item[0] for item in edges]
    #                     if concept_val in concept_labels:
    #                         nodes_copy.add((node["node"].name, node["node"].pk))
    #                         new_found.append(node)

    #                 found = new_found

    #         self.logger.debug("found {0} branches".format(len(found)))
    #         if len(found) == 0:
    #             self.logger.error(" *** branch not found for {0}".format(str(jsonld_graph)))
    #             raise self.DataDoesNotMatchGraphException()

    #         if len(self.findOntologyProperties(jsonld_graph)) == 0:
    #             # print('at a leaf -- unwinding')
    #             self.logger.debug("No further ontology properties found in this fragment; leaf of tree. Unwinding")

    #         def json_data_is_valid(node, json_ld_node):
    #             datatype = self.datatype_factory.get_instance(node.datatype)
    #             value = datatype.from_rdf(json_ld_node)
    #             return len(datatype.validate(value)) == 0

    #         if len(found) > 1:
    #             self.logger.info("Iterating through the matched nodes")
    #             for found_node in found:
    #                 # here we follow the algorithm supplied by the Getty
    #                 # If the range in the model is a domain-value, and the incoming data is of the right format and part of the domain-value's enumeration, then accept that node.
    #                 # If the range in the model is a number, string, or date, and the incoming data is of the right format, then accept that node.
    #                 # If the range in the model is a file-list, and the referenced file already exists, then accept that node.
    #                 # If the range in the model is a concept, then consider if the incoming data is a concept that is part of the collection for the node. If it is, then accept that node. If it is a concept, and not part of the collection, then fail. If it is not a concept, then continue.
    #                 self.logger.debug("Checking to see if the node is in a literal datatype:")
    #                 node_dt = self.datatype_factory.get_instance(found_node["node"].datatype)
    #                 if node_dt.is_a_literal_in_rdf() and json_data_is_valid(found_node["node"], jsonld_graph):
    #                     self.logger.debug("    Matched {0} and the json fragment is valid".format(found_node["node"].datatype))
    #                     return found_node

    #                 # If the range is semantic, then check the class of the incoming node is the same
    #                 # class as the model's node. If it does, then recursively test the edges of the
    #                 # semantic node to determine if it is a candidate (peek-ahead). Remove from the
    #                 # candidate list if it is not.
    #                 self.logger.debug("Checking to see if the node is a semantic node?")
    #                 if found_node["node"].datatype == "semantic":
    #                     self.logger.debug(
    #                         "Node is semantic node. \
    #                         Recursively search for the children of this node and match to branch."
    #                     )
    #                     self.logger.debug(
    #                         "now searching children of {0} node UUID {1}".format(found_node["node"].name, found_node["node"].pk)
    #                     )
    #                     for ontology_prop in self.findOntologyProperties(jsonld_graph):
    #                         try:
    #                             self.logger.debug("Matches {0}?".format(ontology_prop))
    #                             branch = self.findBranch(found_node["children"], ontology_prop, jsonld_graph[ontology_prop])
    #                         except self.DataDoesNotMatchGraphException as e:
    #                             self.logger.error("Data supplied does not match")
    #                             found_node["remove"] = True
    #                             invalid_nodes.add((found_node["node"].name, found_node["node"].pk))
    #                         except self.AmbiguousGraphException as e:
    #                             # Not sure this will be called, given the structure of this code
    #                             # Adding a debug logger just in case it might
    #                             self.logger.debug("AmbiguousGraphException thrown while iterating through semantic node children.")
    #                             pass

    #                 # If the range in the model is a resource-instance, then check that the incoming
    #                 # node has the same class as the top node of any of the referenced models. If more
    #                 # than one model has the same top level class, then fail as the model is ambiguous.
    #                 # If there is exactly one possible model, then accept that node.
    #                 if found_node["node"].datatype == "resource-instance":
    #                     self.logger.debug("Resource Instance datatype, check for model in Arches that matches:")
    #                     if found_node["node"].ontologyclass in self.resource_model_root_classes:
    #                         self.logger.debug("Resource instance <=> Model match found")
    #                         return found_node
    #                     else:
    #                         self.logger.error("Incoming node class for resource instance datatype != match Model")
    #                         self.logger.debug(found_node["node"].ontologyclass)

    #         # ORIGINAL CODE - this is probably more flexible to have this here as this allows for non-semantic nodes to have child nodes
    #         # for ontology_prop in self.findOntologyProperties(jsonld_graph):
    #         #     for found_node in found:
    #         #         try:
    #         #             # print 'now searching children of %s node' % found_node['node'].name
    #         #             branch = self.findBranch(found_node['children'], ontology_prop, jsonld_graph[ontology_prop])
    #         #         except self.DataDoesNotMatchGraphException as e:
    #         #             found_node['remove'] = True
    #         #             invalid_nodes.add((found_node['node'].name, found_node['node'].pk))
    #         #         except self.AmbiguousGraphException as e:
    #         #             # print 'threw AmbiguousGraphException'
    #         #             # print nodes_copy
    #         #             pass

    #         valid_nodes = nodes_copy.difference(invalid_nodes)
    #         self.logger.debug(
    #             "After walking the node tree, {0} valid nodes found, {1} invalid discarded".format(len(valid_nodes), len(invalid_nodes))
    #         )
    #         self.logger.debug("Valid Node names/pk: {0}".format(valid_nodes))
    #         if len(valid_nodes) == 1:
    #             valid_node = valid_nodes.pop()
    #             for node in nodes:
    #                 if node["node"].pk == valid_node[1]:
    #                     self.logger.info("Matching Branch found: {0}".format(node["node"].name))
    #                     return node
    #         elif len(valid_nodes) > 1:
    #             raise self.AmbiguousGraphException()
    #         else:
    #             raise self.DataDoesNotMatchGraphException()

    def resolve_jsonld_doc(self, resource):
        # 1. find all the json ld paths that contain the given json ld node
        # 2. for each of the found json ld paths find corresponding graph path matches (if there are none then retrun DataDoesNotMatchGraphException)
        # 3. take the depth of the json ld node and traverse down the path of each graph path to that depth
        #    if the sequence of nodes down to that depth is the same for each graph path, then that node in the graph path is the node to return, if it's not the same return AmbiguousGraphException

        def path_to_string(pathlists):
            ret = []
            for pathlist in pathlists:
                pathstr = []
                for path in pathlist:
                    pathstr.append(path["label"].split("/")[-1])
                ret.append(",".join(pathstr))
            return ret

        # import ipdb

        # ipdb.sset_trace()
        graph_paths = self.get_paths(self.graphtree)
        print(path_to_string(graph_paths))

        jsonld_paths = self.get_jsonld_paths(self.jsonld_doc)
        print(path_to_string(jsonld_paths))
        # print(f"IN FIND NODE -------- {jsonld}")

        depth = None  # how deeply nested is the jsonld node in jsonld document
        found_jsonld_paths = []
        for jsonld_path in jsonld_paths:

            found_graph_paths = []
            # here we find the graph paths that share the same pattern as the jsonld paths identified above
            # the found graph path don't take into consideration the node ids (only ontologyclass and ontologyproperty sequence)
            for jsonld_path_str in path_to_string([jsonld_path]):
                for graph_path in graph_paths:
                    if path_to_string([graph_path])[0].startswith(jsonld_path_str):
                        found_graph_paths.append(graph_path)

            if len(found_graph_paths) > 1:
                new_found_graph_paths = []
                for i, jsonld_node in enumerate(jsonld_path):
                    if i % 2 == 0:
                        if str(RDFS.label) in jsonld_node["jsonld_node"] and "@value" in jsonld_node["jsonld_node"][str(RDFS.label)][0]:
                            new_found_graph_paths = []
                            for found_graph_path in found_graph_paths:
                                if (
                                    found_graph_path[i]["node"]["node"].datatype == "concept"
                                    or found_graph_path[i]["node"]["node"].datatype == "concept-list"
                                ):
                                    concept_node = found_graph_path[i]["node"]
                                    collection = concept_node["node"].config["rdmCollection"]
                                    edges = Concept().get_child_collections(collection, columns="valueto")
                                    concept_labels = [item[0] for item in edges]

                                    all_values_found = True
                                    for concept_val in jsonld_node["jsonld_node"][str(RDFS.label)]:
                                        if concept_val["@value"] not in concept_labels:
                                            all_values_found = False

                                    if all_values_found:
                                        new_found_graph_paths.append(found_graph_path)

                found_graph_paths = new_found_graph_paths

            if len(found_graph_paths) == 0:
                raise self.DataDoesNotMatchGraphException()

            if len(found_graph_paths) == 1:
                # we've found our path in the graph, now we just need to populate the tiles
                self.assign_tiles(found_graph_paths[0], jsonld_path, resource)

            if len(found_graph_paths) > 1:
                raise self.AmbiguousGraphException()

        print("-" * 200)
        # print(jsonld_paths)
        print(JSONSerializer().serialize(self.tiles))
        print("-" * 200)

        # if the nodes found at this depth are the same nodes then we're done
        # if they are not the same nodes but are all concept nodes then can they be
        # differentiated by the supplied concept being saved?
        # if they can't be differentiated then we neet to raise an AmbiguousGraphException
        # make sure we check node ids

        return None

    # def resolve_node_ids(self, jsonld, ontology_prop=None, graph=None, parent_node=None, tileid=None, parent_tileid=None, resource=None):
    #     # print "-------------------"
    #     self.logger.debug("-------------: %r" % jsonld)
    #     if not isinstance(jsonld, list):
    #         jsonld = [jsonld]

    #     self.logger.debug("INCOMING TO resolve_node_ids: %r" % jsonld)
    #     parent_tileid = tileid
    #     for jsonld_node in jsonld:
    #         if parent_node is not None:
    #             try:
    #                 # print(jsonld_node)
    #                 branch = None
    #                 if self.use_ids:
    #                     try:
    #                         match = re.match(
    #                             r".*?/tile/(?P<tileid>%s)/node/(?P<nodeid>%s)" % (settings.UUID_REGEX, settings.UUID_REGEX),
    #                             str(jsonld_node["@id"]),
    #                         )
    #                         if match:
    #                             tileid = match.group("tileid")
    #                             self.logger.debug("Found matching tile id `{0}` from the tile/node URI".format(tileid))
    #                             for node in parent_node["children"]:
    #                                 if str(node["node"].pk) == match.group("nodeid"):
    #                                     branch = node
    #                     except:
    #                         pass

    #                 if branch is None:
    #                     found_node = self.find_node(jsonld_node)
    #                     branch = self.findBranch(parent_node["children"], ontology_prop, jsonld_node)
    #                     print(f"FOUND NODE = {found_node}")
    #                     print(f"BRANCH = {branch}")
    #                     print(f"----------- NODE MATCH: {found_node==branch} --------")
    #                     if branch["node"].nodegroup != parent_node["node"].nodegroup:
    #                         tileid = uuid.uuid4()

    #             except self.DataDoesNotMatchGraphException as e:
    #                 self.logger.error("Mismatch when trying to match the JSON LD section with a relevant Arches Branch")
    #                 self.logger.debug(jsonld_node)
    #                 self.errors["DataDoesNotMatchGraphException"] = e
    #                 branch = None

    #             except self.AmbiguousGraphException as e:
    #                 self.logger.error("Ambiguous Graph exception thrown")
    #                 self.logger.debug(e.message)
    #                 self.logger.debug(jsonld_node)
    #                 self.errors["AmbiguousGraphException"] = e
    #                 branch = None
    #         else:
    #             branch = graph

    #         ontology_properties = self.findOntologyProperties(jsonld_node)

    #         if branch is not None:
    #             if branch != graph:
    #                 # jsonld_node['@archesid'] = '%stile/%s/node/%s' % (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, tileid, branch['node'].nodeid)

    #                 if tileid not in self.tiles:
    #                     self.logger.debug("Target tileid does not exist - creating {0}".format(tileid))
    #                     self.tiles[tileid] = Tile(
    #                         tileid=tileid, parenttile_id=parent_tileid, nodegroup_id=branch["node"].nodegroup_id, data={}
    #                     )
    #                     if parent_tileid is None:
    #                         self.logger.debug("Tile does not have a parent_tileid - adding to resource.tiles list")
    #                         resource.tiles.append(self.tiles[tileid])
    #                     else:
    #                         self.logger.debug("Tile does has {0} as parent_tileid".format(parent_tileid))
    #                         self.tiles[parent_tileid].tiles.append(self.tiles[tileid])

    #                 if branch["node"].datatype != "semantic":
    #                     self.logger.debug("Assigning value to datatype ({0}) from a non-semantic node:".format(branch["node"].datatype))
    #                     # import ipdb
    #                     # ipdb.sset_trace()
    #                     datatype = self.datatype_factory.get_instance(branch["node"].datatype)

    #                     # print branch['node'].datatype
    #                     if len(jsonld) == 1:
    #                         value = datatype.from_rdf(jsonld_node)
    #                     else:
    #                         value = []
    #                         # this is not very efficient but does fix the problem for ticket #5098
    #                         # what we should do is prevent subsequent loops through "jsonld" on line 565 above
    #                         for jldnode in jsonld:
    #                             self.logger.debug(f"datatype: {datatype}")
    #                             raw_val = datatype.from_rdf(jldnode)
    #                             if isinstance(raw_val, list):
    #                                 value = value + raw_val
    #                             else:
    #                                 value.append(raw_val)
    #                     # print("finding value")
    #                     # print (jsonld_node)
    #                     self.logger.debug("value found! : {0}".format(value))
    #                     self.tiles[tileid].data[str(branch["node"].nodeid)] = value
    #                     # ontology_properties = self.findOntologyProperties(jsonld_node)

    #                     if len(jsonld) > 1:
    #                         break

    #             if len(ontology_properties) > 0:
    #                 for ontology_property in ontology_properties:
    #                     self.logger.debug("Recursing on %s -> %s" % (ontology_property, jsonld_node["@type"]))
    #                     self.resolve_node_ids(
    #                         jsonld_node[ontology_property],
    #                         ontology_prop=ontology_property,
    #                         graph=None,
    #                         parent_node=branch,
    #                         tileid=tileid,
    #                         parent_tileid=parent_tileid,
    #                         resource=resource,
    #                     )
    #     return jsonld

    def add_node_ids(self, jsonld_graph):
        from random import random

        def graph_to_paths(jsonld_node):
            jsonld_node["_id"] = random()
            property_nodes = self.findOntologyProperties(jsonld_node)
            if len(property_nodes) > 0:
                for property_node in property_nodes:
                    if isinstance(jsonld_node[property_node], list):
                        for node in jsonld_node[property_node]:
                            ret = graph_to_paths(node)
            return

        return graph_to_paths(jsonld_graph)

    def assign_tiles(self, graph_path, jsonld_path, resource):
        # we've found our path in the graph, now we just need to populate the tiles
        for i, jsonld_node in enumerate(jsonld_path):
            if i % 2 == 0:
                # jsonld_node["node"] = graph_path[i]["node"]["node"].name
                parent_node = None if i < 2 else graph_path[i - 2]["node"]
                if parent_node is not None:
                    self.add_tile(jsonld_node, graph_path[i]["node"], parent_node, resource)

    def add_tile(self, jsonld_node, current_node, parent_node, resource):
        tileid = current_node.get("tileid", None)
        if self.use_ids:
            try:
                match = re.match(
                    r".*?/tile/(?P<tileid>%s)/node/(?P<nodeid>%s)" % (settings.UUID_REGEX, settings.UUID_REGEX), str(jsonld_node["@id"]),
                )
                if match:
                    tileid = match.group("tileid")
                    self.logger.debug("Found matching tile id `{0}` from the tile/node URI".format(tileid))
            except:
                pass

        else:
            if tileid is None:
                if current_node["node"].nodegroup != parent_node["node"].nodegroup:
                    tileid = uuid.uuid4()
                else:
                    tileid = parent_node["tileid"]

        if tileid is None:
            raise Exception("A tileid couldn't be derived.  That's a problem.")

        current_node["tileid"] = tileid

        if tileid not in self.tiles:
            self.logger.debug("Target tileid does not exist - creating {0}".format(tileid))
            self.tiles[tileid] = Tile(
                tileid=tileid, parenttile_id=parent_node["tileid"], nodegroup_id=current_node["node"].nodegroup_id, data={}
            )
            if parent_node["tileid"] is None:
                self.logger.debug("Tile does not have a parent tileid - adding to resource.tiles list")
                resource.tiles.append(self.tiles[tileid])
            else:
                self.logger.debug("Tile does has {0} as parent tileid".format(parent_node["tileid"]))
                self.tiles[parent_node["tileid"]].tiles.append(self.tiles[tileid])

        if self.datatype_factory.datatypes[current_node["node"].datatype].defaultwidget is not None:
            self.logger.debug("Assigning value to datatype ({0}) from a non-semantic node:".format(current_node["node"].datatype))
            datatype = self.datatype_factory.get_instance(current_node["node"].datatype)
            value = datatype.from_rdf(jsonld_node["jsonld_node"])

            self.logger.debug("value found! : {0}".format(value))
            if str(current_node["node"].nodeid) in self.tiles[tileid].data:
                existing_value = self.tiles[tileid].data[str(current_node["node"].nodeid)]
                if not isinstance(existing_value, list):
                    existing_value = [existing_value]
                if not isinstance(value, list):
                    value = [value]
                value = value + existing_value

            self.tiles[tileid].data[str(current_node["node"].nodeid)] = value

        return tileid

    def get_paths(self, graphtree):
        def graph_to_paths(current_node, path=[], path_list=[], _cache=[]):
            if len(path) == 0:
                current_path = []
            else:
                current_path = path[:]

            current_node["tileid"] = None
            if current_node["parent_edge"] is not None:
                current_path.append({"label": current_node["parent_edge"].ontologyproperty, "node": current_node},)
                current_path.append({"label": current_node["node"].ontologyclass, "node": current_node},)
            else:
                current_path.append({"label": current_node["node"].ontologyclass, "node": current_node},)

            if len(current_node["children"]) == 0 or current_node["node"].nodeid in _cache:
                path_list.append(current_path[:])
            else:
                _cache.append(current_node["node"].nodeid)
                for node in current_node["children"]:
                    if node["node"].datatype == "resource-instance":
                        for graphid in node["node"].config["graphid"]:
                            node["node"].ontologyclass = self.root_ontologyclass_lookup[graphid]
                            ret = graph_to_paths(node, current_path, path_list, _cache)
                    else:
                        ret = graph_to_paths(node, current_path, path_list, _cache)

            return path_list

        return graph_to_paths(graphtree)

    def get_jsonld_paths(self, jsonld):
        def path_to_string(pathlists):
            ret = []
            for pathlist in pathlists:
                pathstr = []
                for path in pathlist:
                    pathstr.append(path["label"])
                ret.append(",".join(pathstr))
            return ret

        path_list = []

        # import ipdb

        # ipdb.sset_trace()

        def graph_to_paths(jsonld_node, path=[], ontologyclass=None, property_class=None, previous_node=None, depth=0):
            # print(len(path))

            # if len(path) == 0:
            #     print(" HERE ------------------------------------------------")
            #     current_path = []
            # else:
            current_path = path[:]
            if ontologyclass is not None:
                current_path.append({"label": ontologyclass, "_id": previous_node["_id"], "jsonld_node": previous_node},)
            if property_class is not None:
                current_path.append({"label": property_class},)

            # print(path_to_string([current_path]))

            property_classes = self.findOntologyProperties(jsonld_node)
            if "@type" in jsonld_node:
                ontologyclass = jsonld_node["@type"][0] if isinstance(jsonld_node["@type"], list) else jsonld_node["@type"]
            else:
                ontologyclass = str(RDFS.Literal)

            # print(len(property_classes))
            if len(property_classes) > 0:
                for property_class in property_classes:
                    # print(f"{depth*'-'}{property_class}")
                    if isinstance(jsonld_node[property_class], list):
                        for node in jsonld_node[property_class]:
                            # print("heres----")
                            ret = graph_to_paths(node, current_path, ontologyclass, property_class, jsonld_node, depth + 2)
                        # if isinstance(jsonld_node[property_class], dict):
                        #     for node in [jsonld_node[property_class]]:
                        #         ret = graph_to_paths(node, current_path, path_list, _cache)
                        # if isinstance(jsonld_node[property_class], str):
                        #     pass
            else:
                current_path.append({"label": ontologyclass, "_id": jsonld_node["_id"], "jsonld_node": jsonld_node},)
                path_list.append(current_path[:])

            return path_list

        return graph_to_paths(jsonld)
