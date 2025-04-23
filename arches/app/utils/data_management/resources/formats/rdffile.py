import os
import re
import json
import uuid
import requests
import datetime
import logging
from io import StringIO
from django.urls import reverse
from django.utils.translation import gettext as _
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
from pyld.jsonld import compact, frame, from_rdf, to_rdf, expand, set_document_loader

# Stop code from looking up the contexts online for every operation
docCache = {}


class ValueErrorWithNodeInfo(ValueError):
    def __init__(
        self, *args, value=None, datatype=None, node_id=None, nodegroup_id=None
    ):
        super().__init__(*args)
        self.value = value
        self.datatype = datatype
        self.node_id = node_id
        self.nodegroup_id = nodegroup_id


def fetch(url):
    resp = requests.get(url)
    return resp.json()


def use_cache(url):
    if (
        docCache[url]["expires"] is not None
        and docCache[url]["expires"] < datetime.datetime.now()
    ):
        return False
    else:
        return True


# PyLD 2.0 / JSON-LD 1.1 passes two params, we don't need the second
def load_document_and_cache(url, cache=None):
    if url in docCache and use_cache(url):
        return docCache[url]

    doc = {"expires": None, "contextUrl": None, "documentUrl": None, "document": ""}
    data = fetch(url)
    doc["document"] = data
    doc["expires"] = datetime.datetime.now() + datetime.timedelta(
        minutes=settings.JSONLD_CONTEXT_CACHE_TIMEOUT
    )
    docCache[url] = doc
    return doc


set_document_loader(load_document_and_cache)


class RdfWriter(Writer):
    def __init__(self, **kwargs):
        self.format = kwargs.pop("format", "xml")
        self.logger = logging.getLogger(__name__)
        super(RdfWriter, self).__init__(**kwargs)

    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        super(RdfWriter, self).write_resources(
            graph_id=graph_id, resourceinstanceids=resourceinstanceids, **kwargs
        )

        dest = StringIO()
        g = self.get_rdf_graph()
        g.serialize(destination=dest, format=self.format)

        full_file_name = os.path.join("{0}.{1}".format(self.file_name, "rdf"))
        return [{"name": full_file_name, "outputfile": dest}]

    def get_rdf_graph(self):
        archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
        graph_uri = URIRef(
            archesproject[reverse("graph", args=[self.graph_id]).lstrip("/")]
        )
        self.logger.debug(
            "Using `{0}` for Arches URI namespace".format(
                settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT
            )
        )
        self.logger.debug("Using `{0}` for Graph URI".format(graph_uri))

        g = Graph()
        g.bind("archesproject", archesproject, False)
        graph_cache = {}

        def get_nodegroup_edges_by_collector_node(node):
            edges = []
            nodegroup = node.nodegroup

            def getchildedges(node):
                for edge in models.Edge.objects.filter(domainnode=node).select_related(
                    "rangenode__nodegroup", "domainnode"
                ):
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
                graph = (
                    models.GraphModel.objects.filter(pk=graphid)
                    .prefetch_related("node_set__nodegroup")
                    .get()
                )
                nodegroups = set()
                for node in graph.node_set.all():
                    graph_cache[graphid]["nodedatatypes"][
                        str(node.nodeid)
                    ] = node.datatype
                    if node.nodegroup:
                        nodegroups.add(node.nodegroup)
                    if node.istopnode:
                        for edge in get_nodegroup_edges_by_collector_node(node):
                            if edge.rangenode.nodegroup is None:
                                graph_cache[graphid]["rootedges"].append(edge)
                for nodegroup in nodegroups:
                    graph_cache[graphid]["subgraphs"][nodegroup] = {
                        "edges": [],
                        "inedge": None,
                        "parentnode_nodegroup": None,
                    }
                    graph_cache[graphid]["subgraphs"][nodegroup]["inedge"] = (
                        models.Edge.objects.filter(rangenode_id=nodegroup.pk)
                        .select_related("domainnode__nodegroup")
                        .get()
                    )
                    graph_cache[graphid]["subgraphs"][nodegroup][
                        "parentnode_nodegroup"
                    ] = graph_cache[graphid]["subgraphs"][nodegroup][
                        "inedge"
                    ].domainnode.nodegroup
                    graph_cache[graphid]["subgraphs"][nodegroup]["edges"] = (
                        get_nodegroup_edges_by_collector_node(
                            models.Node.objects.filter(pk=nodegroup.pk)
                            .select_related("nodegroup")
                            .get()
                        )
                    )

            return graph_cache[graphid]

        def add_edge_to_graph(graph, domainnode, rangenode, edge, tile, graph_info):
            pkg = {}
            pkg["d_datatype"] = graph_info["nodedatatypes"].get(str(edge.domainnode_id))
            dom_dt = self.datatype_factory.get_instance(pkg["d_datatype"])
            # Don't process any further if the domain datatype is a literal
            if dom_dt.is_a_literal_in_rdf():
                return

            pkg["r_datatype"] = graph_info["nodedatatypes"].get(str(edge.rangenode_id))
            pkg["range_tile_data"] = None
            pkg["domain_tile_data"] = None
            if str(edge.rangenode_id) in tile.data:
                pkg["range_tile_data"] = tile.data[str(edge.rangenode_id)]
            if str(edge.domainnode_id) in tile.data:
                pkg["domain_tile_data"] = tile.data[str(edge.domainnode_id)]
            elif (
                tile.parenttile is not None
                and str(edge.domainnode_id) in tile.parenttile.data
            ):
                pkg["domain_tile_data"] = tile.parenttile.data[str(edge.domainnode_id)]

            rng_dt = self.datatype_factory.get_instance(pkg["r_datatype"])
            pkg["d_uri"] = dom_dt.get_rdf_uri(domainnode, pkg["domain_tile_data"], "d")
            if rng_dt.collects_multiple_values():
                # If the range datatype collects multiple values, then there is no get
                # the RDF URI for the range node as it unused or looked up later.
                # This saved db queries. re #11572
                pkg["r_uri"] = None
            else:
                pkg["r_uri"] = rng_dt.get_rdf_uri(
                    rangenode, pkg["range_tile_data"], "r"
                )

            # Concept on a node that is not required, but not present
            # Nothing to do here
            if pkg["r_uri"] is None and pkg["range_tile_data"] is None:
                return

            # JSON-LD fails assert if domain node empty while range node has data.
            # Unknown!=Undefined, but reasonable substitution to omit edge from null domain.
            if pkg["d_uri"] is None and pkg["range_tile_data"]:
                self.logger.warning(
                    _(
                        "Unable to return range value because domain is None, re https://github.com/archesproject/arches/pull/9783/files"
                    )
                )
                return

            # FIXME:  Why is this not in datatype.to_rdf()

            # Domain node is NOT a literal value in the RDF representation, so will have a type:
            if type(pkg["d_uri"]) == list:
                for duri in pkg["d_uri"]:
                    graph.add((duri, RDF.type, URIRef(edge.domainnode.ontologyclass)))
            else:
                graph.add(
                    (pkg["d_uri"], RDF.type, URIRef(edge.domainnode.ontologyclass))
                )

            # Use the range node's datatype.to_rdf() method to generate an RDF representation of it
            # and add its triples to the core graph

            # FIXME: some datatypes have their URI calculated from _tile_data (e.g. concept)
            # ... if there is a list of these, then all of the permutations will happen
            # ... as the matrix below re-processes all URIs against all _tile_data entries :(
            if type(pkg["d_uri"]) == list:
                mpkg = pkg.copy()
                for d in pkg["d_uri"]:
                    mpkg["d_uri"] = d
                    if (
                        type(pkg["r_uri"]) == list
                        and not rng_dt.collects_multiple_values()
                    ):
                        npkg = mpkg.copy()
                        for r in pkg["r_uri"]:
                            # compute matrix of n * m
                            npkg["r_uri"] = r
                            graph += rng_dt.to_rdf(npkg, edge)
                    else:
                        # iterate loop on m * 1
                        graph += rng_dt.to_rdf(mpkg, edge)
            elif type(pkg["r_uri"]) == list and not rng_dt.collects_multiple_values():
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
                domainnode = archesproject[str(edge.domainnode_id)]
                rangenode = archesproject[str(edge.rangenode_id)]
                add_edge_to_graph(g, domainnode, rangenode, edge, None, graph_info)

            for tile in tiles:
                # add all the edges for a given tile/nodegroup
                for edge in graph_info["subgraphs"][tile.nodegroup]["edges"]:
                    domainnode = archesproject[
                        "tile/%s/node/%s" % (str(tile.pk), str(edge.domainnode_id))
                    ]
                    rangenode = archesproject[
                        "tile/%s/node/%s" % (str(tile.pk), str(edge.rangenode_id))
                    ]
                    add_edge_to_graph(g, domainnode, rangenode, edge, tile, graph_info)

                # add the edge from the parent node to this tile's root node
                # where the tile has no parent tile, which means the domain node has no tile_id
                if (
                    graph_info["subgraphs"][tile.nodegroup]["parentnode_nodegroup"]
                    is None
                ):
                    edge = graph_info["subgraphs"][tile.nodegroup]["inedge"]
                    if edge.domainnode.istopnode:
                        domainnode = archesproject[
                            reverse("resources", args=[resourceinstanceid]).lstrip("/")
                        ]
                    else:
                        domainnode = archesproject[str(edge.domainnode_id)]
                    rangenode = archesproject[
                        "tile/%s/node/%s" % (str(tile.pk), str(edge.rangenode_id))
                    ]
                    add_edge_to_graph(g, domainnode, rangenode, edge, tile, graph_info)

                # add the edge from the parent node to this tile's root node
                # where the tile has a parent tile
                if (
                    graph_info["subgraphs"][tile.nodegroup]["parentnode_nodegroup"]
                    is not None
                ):
                    edge = graph_info["subgraphs"][tile.nodegroup]["inedge"]
                    domainnode = archesproject[
                        "tile/%s/node/%s"
                        % (str(tile.parenttile_id), str(edge.domainnode_id))
                    ]
                    rangenode = archesproject[
                        "tile/%s/node/%s" % (str(tile.pk), str(edge.rangenode_id))
                    ]
                    add_edge_to_graph(g, domainnode, rangenode, edge, tile, graph_info)
        return g


class JsonLdWriter(RdfWriter):
    def build_json(self, graph_id=None, resourceinstanceids=None, **kwargs):
        # Build the JSON separately serializing it, so we can use internally
        super(RdfWriter, self).write_resources(
            graph_id=graph_id, resourceinstanceids=resourceinstanceids, **kwargs
        )
        g = self.get_rdf_graph()
        value = g.serialize(format="nquads").decode("utf-8")

        js = from_rdf(value, {"format": "application/nquads", "useNativeTypes": True})

        assert (
            len(resourceinstanceids) == 1
        )  # currently, this should be limited to a single top resource

        archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
        resource_inst_uri = archesproject[
            reverse("resources", args=[resourceinstanceids[0]]).lstrip("/")
        ]

        context = self.graph_model.jsonldcontext
        framing = {
            "@omitDefault": True,
            "@omitGraph": False,
            "@id": str(resource_inst_uri),
        }

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
            for k, v in list(js["@graph"][0].items()):
                js[k] = v
            del js["@graph"]
        return js

    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        js = self.build_json(graph_id, resourceinstanceids, **kwargs)
        out = json.dumps(js, indent=kwargs.get("indent", None), sort_keys=True)
        dest = StringIO(out)
        full_file_name = os.path.join("{0}.{1}".format(self.file_name, "jsonld"))
        return [{"name": full_file_name, "outputfile": dest}]


class JsonLdReader(Reader):
    def __init__(self, *args, **kwargs):
        super(JsonLdReader, self).__init__(*args, **kwargs)
        self.tiles = {}
        self.resources = []
        self.resource = None
        self.use_ids = False
        self.root_ontologyclass_lookup = {}
        self.graphtree = None
        self.print_buf = []
        self.verbosity = kwargs.get("verbosity", 1)
        self.ignore_errors = kwargs.get("ignore_errors", False)
        self.default_timezone = kwargs.get("default_timezone")
        self.logger = logging.getLogger(__name__)
        for graph in models.GraphModel.objects.filter(isresource=True):
            node = models.Node.objects.get(graph_id=graph.pk, istopnode=True)
            self.root_ontologyclass_lookup[str(graph.pk)] = node.ontologyclass
        self.logger.info("Initialized JsonLdReader")

    def validate_concept_in_collection(self, value, collection):
        cdata = Concept().get_child_collections(collection, columns="conceptidto")
        ids = [str(x[0]) for x in cdata]
        for c in cdata:
            cids = [
                x.value
                for x in models.Value.objects.all().filter(
                    concept_id__exact=c[0], valuetype__category="identifiers"
                )
            ]
            ids.extend(cids)
        if value.startswith(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT):
            value = value.rsplit("/", 1)[-1]
        return str(value) in ids

    def process_graph(self, graphid):
        root_node = None
        nodes = {}
        graph = GraphProxy.objects.get(graphid=graphid)
        for nodeid, n in graph.nodes.items():
            node = {}
            if n.istopnode:
                root_node = node
            node["datatype"] = self.datatype_factory.get_instance(n.datatype)
            node["datatype_type"] = n.datatype
            node["parent_nodegroup"] = (
                str(n.nodegroup.parentnodegroup_id) if n.nodegroup is not None else None
            )
            node["extra_class"] = []
            if node["datatype"].references_resource_type():
                if "graphs" in n.config and n.config["graphs"]:
                    for gid in [x["graphid"] for x in n.config["graphs"]]:
                        node["extra_class"].append(self.root_ontologyclass_lookup[gid])

            node["config"] = {}
            if n.config and "rdmCollection" in n.config:
                node["config"]["collection_id"] = str(n.config["rdmCollection"])
            elif n.config and "graphs" in n.config:
                for entry in n.config["graphs"]:
                    entry["rootclass"] = self.root_ontologyclass_lookup[
                        entry["graphid"]
                    ]
                node["config"]["graphs"] = n.config["graphs"]
            node["required"] = n.isrequired
            node["node_id"] = str(n.nodeid)
            node["name"] = n.name
            node["class"] = n.ontologyclass
            node["nodegroup_id"] = str(n.nodegroup_id)
            node["cardinality"] = n.nodegroup.cardinality if n.nodegroup else None
            node["out_edges"] = []
            node["children"] = {}
            nodes[str(n.nodeid)] = node

        for edegid, e in graph.edges.items():
            dn = e.domainnode_id
            rng = e.rangenode_id
            prop = e.ontologyproperty
            nodes[str(dn)]["out_edges"].append({"range": str(rng), "prop": str(prop)})

        def model_walk(node, nodes):
            for e in node["out_edges"]:
                rng = nodes[e["range"]]
                for oclass in set([rng["class"], *rng["extra_class"]]):
                    key = f"{e['prop']} {oclass}"
                    if key in node["children"]:
                        node["children"][key].append(rng)
                    else:
                        node["children"][key] = [rng]
                model_walk(rng, nodes)
            del node["out_edges"]

        model_walk(root_node, nodes)

        return root_node

    def get_resource_id(self, value):
        # Allow local URI or urn:uuid:UUID
        match = re.match(
            r".*?%sresources/(?P<resourceid>%s)"
            % (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, settings.UUID_REGEX),
            value,
        )
        if match:
            return match.group("resourceid")
        else:
            match = re.match(r"urn:uuid:(%s)" % settings.UUID_REGEX, value)
            if match:
                return match.groups()[0]
            else:
                self.logger.debug(
                    "Valid resourceid not found within `{0}`".format(value)
                )
        return None

    def read_resource(
        self, data, use_ids=False, resourceid=None, graphid=None, expand_data=True
    ):
        if graphid is None and self.graphtree is None:
            raise Exception("No graphid supplied to read_resource")
        elif self.graphtree is None:
            self.graphtree = self.process_graph(graphid)

        # Ensure we've reset from any previous call
        self.errors = {}
        self.idcache = {}
        self.resources = []
        self.resource = None
        self.use_ids = use_ids
        self.jsonld_doc_node_to_tile_lookup = {}
        self.tiles_wo_required_node_data = []

        if not isinstance(data, list):
            data = [data]
        # Force use_ids if there is more than one record being passed in
        if len(data) > 1:
            self.use_ids = True

        # Maybe calculate sort order for this node's tiles
        try:
            self.shouldSortTiles = settings.JSON_LD_SORT
        except:
            self.shouldSortTiles = False

        for jsonld_document in data:
            if (
                expand_data
            ):  # this should always be true, we set this to false just for some unit tests
                jsonld_document = expand(jsonld_document)[0]

            # Possibly bail very early
            if jsonld_document["@type"][0] != self.graphtree["class"]:
                raise ValueError("Instance does not have same top level class as model")

            if self.use_ids:
                resourceinstanceid = self.get_resource_id(jsonld_document["@id"])
                if resourceinstanceid is None:
                    self.logger.error(
                        "The @id of the resource was not supplied, was null or URI was not correctly formatted"
                    )
                    raise Exception(
                        "The @id of the resource was not supplied, was null or URI was not correctly formatted"
                    )
                self.logger.debug(
                    "Using resource instance ID found: {0}".format(resourceinstanceid)
                )
            else:
                self.logger.debug(
                    "`use_ids` setting is set to False, ignoring @id from the data if any"
                )

            self.resource = Resource()
            if resourceid is not None:
                self.resource.pk = uuid.UUID(resourceid)
            self.resource.graph_id = graphid
            self.resources.append(self.resource)

            ### --- Process Instance ---
            # now walk the instance and align to the tree
            if "@id" in jsonld_document:
                result = {"data": [jsonld_document["@id"]]}
            else:
                result = {"data": [None]}
            self.root_json_document = jsonld_document
            try:
                self.data_walk(jsonld_document, self.graphtree, result)

                def find_parent_tile(searchedtile):
                    for jsonld_node in self.jsonld_doc_node_to_tile_lookup.values():
                        for tile in jsonld_node["tiles"]:
                            if str(tile.tileid) == str(searchedtile.parenttile_id):
                                # if the parent tile is associated with a json-ld node
                                # that has no other tiles, then the searched tile
                                # is where multiple node matches were found
                                if len(jsonld_node["tiles"]) == 1:
                                    return searchedtile
                                else:
                                    return find_parent_tile(tile)

                # the data_walk method along with the json-ld doc can create multiple matched paths to the
                # graph that result in extra tiles being created.  There is the possibility to remove those
                # extra tiles based on if a node in one of those tiles is required.  If it is required,
                # but not supplied in the incomming json-ld data, then that data can't match that branch
                # in the graph and those tiles need to be removed.  If there are still multiple matches
                # for a given json-ld node the we need to reject the json-ld file as being ambiguous.

                tiles_to_remove = []
                if len(self.tiles_wo_required_node_data) > 0:
                    # build tile heirarchy
                    tile_dict = {}
                    for jsonld_node in self.jsonld_doc_node_to_tile_lookup.values():
                        for tile in jsonld_node["tiles"]:
                            tile_dict[str(tile.tileid)] = tile
                    for tileid, tile in tile_dict.items():
                        if tile.parenttile_id:
                            parenttile = tile_dict[str(tile.parenttile_id)]
                            parenttile.tiles.append(tile)

                    def gather_child_tiles(tile, tilelist):
                        tilelist.append(tile)
                        for childtile in tile.tiles:
                            gather_child_tiles(childtile, tilelist)

                    # gather all the tiles that need to be removed from the resource
                    for tile in self.tiles_wo_required_node_data:
                        parenttile = find_parent_tile(tile)
                        parenttile = tile if parenttile is None else parenttile
                        gather_child_tiles(parenttile, tiles_to_remove)

                    for tile in tiles_to_remove:
                        self.resource.tiles.remove(tile)

                    # if we don't remove all child tiles then those will get
                    # saved too and it will include tiles we just deleted above
                    for tile in self.resource.tiles:
                        tile.tiles = []

                # do a final check, once we've removed any extra tiles,
                # that we only have 1 tile per json-ld node, any more than one
                # means that we have multiple branches per node and so the match
                # was ambiguous
                for jsonld_node in self.jsonld_doc_node_to_tile_lookup.values():
                    if len(set(jsonld_node["tiles"]) - set(tiles_to_remove)) > 1:
                        raise ValueError(
                            f"""Even after considering child branches, at least one of the 
                            incoming json-ld nodes still matches more than one branch 
                            in the graph: {jsonld_node}"""
                        )

            except Exception as e:
                err_msg_fail = (
                    f"FAILED to completely load resource with id: {self.resource.pk}\n"
                )
                self.logger.debug(err_msg_fail)
                print(err_msg_fail)
                if self.verbosity > 1:
                    for line in self.print_buf:
                        # print(line) # uncomment this line to print errors directly to the screen
                        self.logger.debug(line)
                    err_msg_fail_detail = f"DETAILED ERROR MESSAGE\n{str(e)}"
                    self.logger.debug(err_msg_fail_detail)
                    print(err_msg_fail_detail)
                if not self.ignore_errors:
                    raise

    def is_semantic_node(self, graph_node):
        return (
            self.datatype_factory.datatypes[graph_node["datatype_type"]].defaultwidget
            is None
        )

    def is_concept_node(self, uri):
        pcs = settings.PREFERRED_CONCEPT_SCHEMES[:]
        pcs.append(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT + "concepts/")
        for p in pcs:
            if uri.startswith(p):
                return True
        return False

    def build_reference_cache(self, jsonld_document):
        if "@id" in jsonld_document and "@type" in jsonld_document:
            dataType = (
                jsonld_document["@type"][0]
                if isinstance(jsonld_document["@type"], list)
                else jsonld_document["@type"]
            )
            self.idcache[jsonld_document["@id"]] = dataType
        for key, value in jsonld_document.items():
            if key in ["@id", "@type"]:
                continue
            if isinstance(value, list):
                for item in value:
                    self.build_reference_cache(item)
            elif isinstance(value, dict):
                self.build_reference_cache(value)

    def get_cached_reference(self, lookup):
        try:
            return self.idcache[lookup]
        except:
            self.build_reference_cache(self.root_json_document)
            try:
                return self.idcache[lookup]
            except:
                raise ("Local reference not found")

    def printline(self, text, indent=0, newline=False):
        prefix = ""
        if newline:
            prefix = "\n"
        if indent and indent > 0:
            prefix = prefix + "   " * int(indent)
        self.print_buf.append(prefix + text)
        if self.verbosity > 2:
            print(prefix + text)

    def find_matching_branch(self, k, v, tree_node, result, tile=None, indent=0):
        branch = None
        self.printline(
            "Walk down non-literal branches in the data", indent, newline=True
        )
        self.printline(f"---" * 20, indent)
        # self.printline(tree_node["name"], indent)
        # self.printline(f"tile={tile}", indent)

        if k in ["@id", "@type"]:
            return

        # extract all @values for the current node
        values = [
            {
                "value": vi["@value"],
                "clss": vi.get("@type", "http://www.w3.org/2000/01/rdf-schema#Literal"),
                "language": vi.get("@language", None),
            }
            for vi in v
            if "@value" in vi
            and vi.get("@type", "http://www.w3.org/2000/01/rdf-schema#Literal")
            == "http://www.w3.org/2000/01/rdf-schema#Literal"
        ]

        # always a list
        for vi in v:
            if "@value" in vi:
                value = vi["@value"]
                uri = None
                clss = vi.get("@type", "http://www.w3.org/2000/01/rdf-schema#Literal")
                is_literal = True
            else:
                # We're an entity
                uri = vi.get("@id", "")
                try:
                    clss = vi["@type"][0]
                except:
                    # {"@id": "http://something/.../"}
                    # with no @type. This is typically an external concept URI reference to a resource instance
                    # Look for it in the children of current node or in the entire document itself (if it's a resource instance ref)
                    possible_cls = []
                    for tn in tree_node["children"]:
                        if tn.startswith(k):
                            possible_cls.append(tn.replace(k, "")[1:])
                    if len(possible_cls) == 1:
                        clss = possible_cls[0]
                    else:
                        try:
                            # this may be a reference to an entity already defined elsewhere in the json document
                            # this can happen when there are more than 1 reference to the same resource instance
                            clss = self.get_cached_reference(uri)
                            vi["@type"] = clss
                        except:
                            raise ValueErrorWithNodeInfo(
                                f"Multiple possible branches and no @type given: {vi}",
                                value=uri,
                                datatype=tree_node["datatype_type"],
                                node_id=tree_node["node_id"],
                                nodegroup_id=(
                                    None
                                    if tree_node["nodegroup_id"] == "None"
                                    else tree_node["nodegroup_id"]
                                ),
                            )

                value = None
                is_literal = False

            # Here we try and find a possible match between the node_tree and data_tree
            # we're matching "key" which equals the concatentaion of property and class
            # at the same level in the trees
            # Find precomputed possible branches by prop/class combination
            key = f"{k} {clss}"
            if key in tree_node["datatype"].ignore_keys():
                # these are handled by the datatype itself
                continue
            elif not key in tree_node["children"] and is_literal:
                # grumble grumble
                # model has xsd:string, default is rdfs:Literal
                key = f"{k} http://www.w3.org/2001/XMLSchema#string"
                if not key in tree_node["children"]:
                    raise ValueErrorWithNodeInfo(
                        f"property/class combination does not exist in model: {k} {clss}\nWhile processing: {vi}",
                        value=value or uri,
                        datatype=tree_node["datatype_type"],
                        node_id=tree_node["node_id"],
                        nodegroup_id=(
                            None
                            if tree_node["nodegroup_id"] == "None"
                            else tree_node["nodegroup_id"]
                        ),
                    )
            elif not key in tree_node["children"]:
                raise ValueErrorWithNodeInfo(
                    f"property/class combination does not exist in model: {k} {clss}\nWhile processing: {vi}",
                    value=value or uri,
                    datatype=tree_node["datatype_type"],
                    node_id=tree_node["node_id"],
                    nodegroup_id=(
                        None
                        if tree_node["nodegroup_id"] == "None"
                        else tree_node["nodegroup_id"]
                    ),
                )

            # if we made it this far then it means that we've found at least 1 match
            # options is a list of potential matches in the graph tree
            # based on property/class combination
            options = tree_node["children"][key]
            possible = []

            self.printline(
                f"Trying to match data value:  '{value or uri}'", indent, newline=True
            )
            self.printline(f"That has type:  '{k}'", indent)
            for o in options:
                self.printline(
                    f"Considering match to graph node: '{o['name']}'",
                    indent + 1,
                    newline=True,
                )
                self.printline(
                    f"New Nodegroup = {o['nodegroup_id'] == o['node_id']}", indent + 1
                )
                self.printline(
                    f"Parent tile id = {result['tile'].tileid if 'tile' in result else None}",
                    indent + 1,
                )

                if is_literal and o["datatype"].is_a_literal_in_rdf():
                    # import each value separately if there are no languages in the values and this is card n string
                    if o["datatype"].is_multilingual_rdf(values):
                        if len(o["datatype"].validate_from_rdf(values)) == 0:
                            possible.append([o, values])
                        else:
                            self.printline(
                                f"Could not validate {values} as a {o['datatype']}",
                                indent + 1,
                            )
                    else:
                        if (
                            o["datatype"].datatype_name == "date"
                            and self.default_timezone
                        ):
                            tz_formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]
                            for tz_format in tz_formats:
                                try:
                                    datetime.datetime.strptime(value, tz_format)
                                    value = value + self.default_timezone
                                    vi["@value"] = value
                                except:
                                    pass
                        if len(o["datatype"].validate_from_rdf(value)) == 0:
                            possible.append([o, value])
                        else:
                            self.printline(
                                f"Could not validate {value} as a {o['datatype']}",
                                indent + 1,
                            )
                elif not is_literal and not o["datatype"].is_a_literal_in_rdf():
                    if self.is_concept_node(uri):
                        self.printline(
                            "This is a concept node, so we'll test if the incoming data can fit here",
                            indent + 1,
                        )
                        collid = o["config"]["collection_id"]
                        try:
                            if self.validate_concept_in_collection(uri, collid):
                                possible.append([o, uri])
                                self.printline(f"POSSIBLE match found.", indent + 1)
                            else:
                                self.printline(
                                    f"Match REJECTED!! Incoming concept URI {uri} not found in the nodes Collection {collid}",
                                    indent + 1,
                                )
                        except:
                            self.printline(
                                f"Errored testing concept {uri} in collection {collid}",
                                indent + 1,
                            )
                    elif o["datatype"].accepts_rdf_uri(uri):
                        # self.printline(f"datatype for {o['name']} accepts uri", indent+1)
                        possible.append([o, uri])
                    elif self.is_semantic_node(o):
                        # it would be great if we could understand if the incoming json-ld node
                        # was semantic and or coledted an actual value
                        # I don't think semantic nodes should have @id values
                        # if uri == "" or uri.startswith("_:"):
                        possible.append([o, ""])
                    else:
                        # This is when the current option doesn't match, but could be
                        # non-ambiguous resource-instance vs semantic node
                        continue

            if not possible:
                # self.printline(f"Tried: {options}")
                raise ValueErrorWithNodeInfo(
                    f"Data does not match any actual node, despite prop/class combination {k} {clss}:\n{vi}",
                    value=value or uri,
                    datatype=options[-1]["datatype"].datatype_name,
                    node_id=options[-1]["node_id"],
                    nodegroup_id=options[-1]["nodegroup_id"],
                )
            elif len(possible) > 1:
                # descend into data to check if there are further clarifying features
                possible2 = []
                for p in possible:
                    # self.printline(f"\n---SECOND TIER: {p[0]['name']}", indent + 1)
                    try:
                        self.printline("Found multiple matches!", indent)
                        # if this doesn't throw an error then keep the possible branch "p"
                        for k, v in vi.items():
                            matched_branch = self.find_matching_branch(
                                k, v, p[0], {}, tile, indent + 1
                            )
                        possible2.append(p)
                    except Exception as e:
                        self.printline(f"Failed due to {e}", indent + 1)
                        pass
                if not possible2:
                    raise ValueErrorWithNodeInfo(
                        "Considering branches, data does not match any node, despite a prop/class combination",
                        value=value or uri,
                        datatype=possible[-1]["datatype"].datatype_name,
                        node_id=possible[-1]["node_id"] if options else None,
                        nodegroup_id=possible[-1]["nodegroup_id"] if options else None,
                    )
                else:
                    branch = possible2
            else:
                branch = possible

        return branch

    def data_walk(self, data_node, tree_node, result, tile=None, indent=0):
        my_tiles = []

        # pre-seed as much of the cache as we can during the data-walk
        if "@id" in data_node and "@type" in data_node:
            dataType = (
                data_node["@type"][0]
                if isinstance(data_node["@type"], list)
                else data_node["@type"]
            )
            self.idcache[data_node["@id"]] = dataType

        for k, v in data_node.items():
            # self.printline(f"k: {k}", indent + 1)
            # self.printline(f"v: {v}", indent + 1)
            # k is a ontology property like
            # "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by"
            # or "http://www.w3.org/2000/01/rdf-schema#label"
            if k in ["@id", "@type"]:
                continue

            # extract all @values for the current node
            values = [
                {
                    "value": vi["@value"],
                    "clss": vi.get(
                        "@type", "http://www.w3.org/2000/01/rdf-schema#Literal"
                    ),
                    "language": vi.get("@language", None),
                }
                for vi in v
                if "@value" in vi
                and vi.get("@type", "http://www.w3.org/2000/01/rdf-schema#Literal")
                == "http://www.w3.org/2000/01/rdf-schema#Literal"
            ]

            # always a list
            for vi in v:
                if id(vi) not in self.jsonld_doc_node_to_tile_lookup:
                    self.jsonld_doc_node_to_tile_lookup[id(vi)] = {
                        "vi": vi,
                        "tiles": [],
                    }
                if "@value" in vi:
                    value = vi["@value"]
                    uri = None
                    clss = vi.get(
                        "@type", "http://www.w3.org/2000/01/rdf-schema#Literal"
                    )
                    is_literal = True
                else:
                    # We're an entity
                    uri = vi.get("@id", "")
                    try:
                        clss = vi["@type"][0]
                    except:
                        # {"@id": "http://something/.../"}
                        # with no @type. This is typically an external concept URI reference to a resource instance
                        # Look for it in the children of current node or in the entire document itself (if it's a resource instance ref)
                        possible_cls = []
                        for tn in tree_node["children"]:
                            if tn.startswith(k):
                                possible_cls.append(tn.replace(k, "")[1:])
                        if len(possible_cls) == 1:
                            clss = possible_cls[0]
                        else:
                            try:
                                # this may be a reference to an entity already defined elsewhere in the json document
                                # this can happen when there are more than 1 reference to the same resource instance
                                clss = self.get_cached_reference(uri)
                                vi["@type"] = clss
                            except:
                                raise ValueError(
                                    f"Multiple possible branches and no @type given: {vi}"
                                )

                    value = None
                    is_literal = False

                branches = self.find_matching_branch(
                    k, [vi], tree_node, result, None, indent=0
                )

                if (
                    k == "http://www.w3.org/2000/01/rdf-schema#label"
                    and branches is None
                ):
                    continue

                x = result.copy()
                for branch in branches:
                    result = x.copy()

                    if not self.is_semantic_node(branch[0]):
                        graph_node = branch[0]
                        if graph_node["datatype"].is_multilingual_rdf(values):
                            node_value = graph_node["datatype"].from_rdf(values)
                        else:
                            node_value = graph_node["datatype"].from_rdf(vi)
                        # node_value might be None if the validation of the datatype fails
                        # XXX Should we check this here, or raise in the datatype?

                        # For resource-instances, the datatype doesn't know the ontology prop config
                        if graph_node["datatype"].references_resource_type():
                            if "graphs" in branch[0]["config"]:
                                gs = branch[0]["config"]["graphs"]
                                if len(gs) == 1:
                                    # just select it
                                    if "ontologyProperty" in gs[0]:
                                        node_value[0]["ontologyProperty"] = gs[0][
                                            "ontologyProperty"
                                        ]
                                    if "inverseOntologyProperty" in gs[0]:
                                        node_value[0]["inverseOntologyProperty"] = gs[
                                            0
                                        ]["inverseOntologyProperty"]
                                else:
                                    for g in gs:
                                        # Now test current node's class against graph's class
                                        # This isn't a guarantee, but close enough
                                        if vi["@type"][0] == g["rootclass"]:
                                            if "ontologyProperty" in g:
                                                node_value[0]["ontologyProperty"] = g[
                                                    "ontologyProperty"
                                                ]
                                            if "inverseOntologyProperty" in g:
                                                node_value[0][
                                                    "inverseOntologyProperty"
                                                ] = g["inverseOntologyProperty"]
                                            break
                    else:
                        # Might get checked in a cardinality n branch that shouldn't be repeated
                        node_value = None

                    self.printline(
                        f"A matching branch has been found and the value can be saved.",
                        indent + 1,
                    )

                    # We know now that it can go into the branch
                    # Determine if we can collapse the data into a -list or not
                    bnodeid = branch[0]["node_id"]

                    # This is going to be the result passed down if we recurse
                    bnode = {
                        "data": [],
                        "nodegroup_id": branch[0]["nodegroup_id"],
                        "cardinality": branch[0]["cardinality"],
                    }

                    if (
                        branch[0]["datatype"].collects_multiple_values()
                        and tile
                        and str(tile.nodegroup.pk) == branch[0]["nodegroup_id"]
                    ):
                        # iterating through a root node *-list type
                        pass
                    elif bnodeid == branch[0]["nodegroup_id"] and not (
                        branch[0]["datatype"].is_multilingual_rdf(values)
                        and bnodeid in result
                    ):
                        # Used to pick the previous tile in loop which MIGHT be the parent (but might not)
                        parenttile_id = (
                            result["tile"].tileid if "tile" in result else None
                        )
                        if (
                            parenttile_id == None
                            and branch[0]["parent_nodegroup"] != "None"
                        ):
                            continue
                        tile = Tile(
                            tileid=uuid.uuid4(),
                            resourceinstance_id=self.resource.pk,
                            parenttile_id=parenttile_id,
                            nodegroup_id=branch[0]["nodegroup_id"],
                            data={},
                        )
                        self.resource.tiles.append(tile)
                        my_tiles.append(tile)
                        self.jsonld_doc_node_to_tile_lookup[id(vi)]["tiles"].append(
                            tile
                        )
                    elif "tile" in result and result["tile"]:
                        tile = result["tile"]

                    if not hasattr(tile, "_json_ld"):
                        tile._json_ld = vi

                    bnode["tile"] = tile
                    if bnodeid in result:
                        if branch[0]["datatype"].collects_multiple_values():
                            # append to previous tile
                            if type(node_value) != list:
                                node_value = [node_value]
                            bnode = result[bnodeid][0]
                            bnode["data"].append(branch[1])
                            if not self.is_semantic_node(branch[0]):
                                try:
                                    n = bnode["tile"].data[bnodeid]
                                except:
                                    n = []
                                    bnode["tile"].data[bnodeid] = n
                                if type(n) != list:
                                    bnode["tile"].data[bnodeid] = [n]
                                bnode["tile"].data[bnodeid].extend(node_value)
                        elif branch[0]["cardinality"] != "n":
                            bnode = result[bnodeid][0]
                            if (
                                bnodeid in bnode["tile"].data
                                and node_value == bnode["tile"].data[bnodeid]
                            ):
                                # No-op, attempt to readd same value
                                pass
                            else:
                                raise ValueError(
                                    f"Attempt to add a value to cardinality 1, non-list node {k} {clss}:\n {vi}"
                                )
                        else:
                            bnode["data"].append(branch[1])
                            if not self.is_semantic_node(branch[0]):
                                tile.data[bnodeid] = node_value
                            result[bnodeid].append(bnode)
                    else:
                        if not self.is_semantic_node(branch[0]):
                            tile.data[bnodeid] = node_value
                        bnode["data"].append(branch[1])
                        result[bnodeid] = [bnode]

                    self.printline(f"Tile.data = {tile.data}", indent + 1)

                    if not is_literal:
                        self.data_walk(vi, branch[0], bnode, tile, indent + 1)

        if self.shouldSortTiles:
            sortfuncs = settings.JSON_LD_SORT_FUNCTIONS
            if my_tiles:
                tile_ng_hash = {}
                for t in my_tiles:
                    try:
                        tile_ng_hash[t.nodegroup_id].append(t)
                    except KeyError:
                        tile_ng_hash[t.nodegroup_id] = [t]
                for k, v in tile_ng_hash.items():
                    if len(v) > 1:
                        for func in sortfuncs:
                            v.sort(key=func)
                        for t, i in zip(v, range(len(v))):
                            t.sortorder = i

        # Finally, after processing all of the branches for this node, check required nodes are present
        for path in tree_node["children"].values():
            for kid in path:
                if kid["required"] and not f"{kid['node_id']}" in result:
                    self.tiles_wo_required_node_data.append(result["tile"])
