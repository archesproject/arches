import json, urllib
from django.urls import reverse
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.search.elasticsearch_dsl_builder import Dsl, Bool, Terms, Exists, Nested
from django.utils.translation import gettext as _
import logging

logger = logging.getLogger(__name__)


class BaseDataType(object):
    def __init__(self, model=None):
        self.datatype_model = model
        self.datatype_name = model.datatype if model else None

    def validate(
        self,
        value,
        row_number=None,
        source=None,
        node=None,
        nodeid=None,
        strict=False,
        **kwargs,
    ):
        """
        Used to validate data in a node of given datatype

        Arguments:
        value -- (required) the value of the node being validated

        Keyword Arguments:
        row_number -- (optional) this is specific to csv import and should be removed
        source -- (optional) this is specific to csv import and should be removed
        node -- (optional) the node instance being validated
        node -- (optional) the node id of the instance begin validated
        strict -- False (default), set to True to force the datatype to perform a more complete check
            (eg: check for the existance of a referenced resoure on the resource-instance datatype)
        """

        return []

    def create_error_message(self, value, source, row_number, message, title=None):
        source_info = "{0} {1}".format(source, row_number) if row_number else ""
        error_message = {
            "type": "ERROR",
            "message": _("{0} error, {1} {2} - {3}. Unable to save.").format(
                self.datatype_name, value, source_info, message
            ),
            "title": title,
        }
        return error_message

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        """
        Assigns a given node value to the corresponding key in a document in
        in preparation to index the document
        """
        pass

    def after_update_all(self, tile=None):
        """
        Refreshes geojson_geometries table after save.
        """
        pass

    def values_match(self, value1, value2):
        return value1 == value2

    def transform_value_for_tile(self, value, **kwargs):
        """
        Transforms values from probably string/wkt representation to specified
        datatype in arches
        """
        return value

    def update(self, tile, data, nodeid, action):
        """
        Updates the tile.data value of a given datatype and returns the updated
        value
        """
        pass

    def transform_export_values(self, value, *args, **kwargs):
        """
        Transforms values from probably string/wkt representation to specified
        datatype in arches
        """
        return value

    def get_bounds(self, tile, node):
        """
        Gets the bounds of a geometry if the datatype is spatial
        """
        return None

    def get_map_layer(self, node=None):
        """
        Gets the array of map layers to add to the map for a given node
        should be a dictionary including (as in map_layers table):
        nodeid, name, layerdefinitions, isoverlay, icon
        """
        return None

    def clean(self, tile, nodeid):
        """
        Converts '' values to null when saving a tile.
        """
        if tile.data[nodeid] == "":
            tile.data[nodeid] = None

    def get_map_source(self, node=None, preview=False):
        """
        Gets the map source definition to add to the map for a given node
        should be a dictionary including (as in map_sources table):
        name, source (json)
        """
        tileserver_url = urllib.parse.unquote(
            reverse("mvt", args=(node.nodeid, "{z}", "{x}", "{y}"))
        )
        if node is None:
            return None
        source_config = {"type": "vector", "tiles": [tileserver_url]}
        node_config = json.loads(node.config.value)
        for prop in ("minzoom", "maxzoom"):
            if prop in node_config:
                source_config[prop] = node_config[prop]

        count = None
        if preview == True:
            count = models.TileModel.objects.filter(
                nodegroup_id=node.nodegroup_id, data__has_key=str(node.nodeid)
            ).count()
            if count == 0:
                source_config = {
                    "type": "geojson",
                    "data": {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "properties": {"total": 1},
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [
                                        -122.4810791015625,
                                        37.93553306183642,
                                    ],
                                },
                            },
                            {
                                "type": "Feature",
                                "properties": {"total": 100},
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [-58.30078125, -18.075412438417395],
                                },
                            },
                            {
                                "type": "Feature",
                                "properties": {"total": 1},
                                "geometry": {
                                    "type": "LineString",
                                    "coordinates": [
                                        [-179.82421875, 44.213709909702054],
                                        [-154.16015625, 32.69486597787505],
                                        [-171.5625, 18.812717856407776],
                                        [-145.72265625, 2.986927393334876],
                                        [-158.37890625, -30.145127183376115],
                                    ],
                                },
                            },
                            {
                                "type": "Feature",
                                "properties": {"total": 1},
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [
                                            [-50.9765625, 22.59372606392931],
                                            [-23.37890625, 22.59372606392931],
                                            [-23.37890625, 42.94033923363181],
                                            [-50.9765625, 42.94033923363181],
                                            [-50.9765625, 22.59372606392931],
                                        ]
                                    ],
                                },
                            },
                            {
                                "type": "Feature",
                                "properties": {"total": 1},
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [
                                            [-27.59765625, -14.434680215297268],
                                            [-24.43359375, -32.10118973232094],
                                            [0.87890625, -31.653381399663985],
                                            [2.28515625, -12.554563528593656],
                                            [-14.23828125, -0.3515602939922709],
                                            [-27.59765625, -14.434680215297268],
                                        ]
                                    ],
                                },
                            },
                        ],
                    },
                }
        return {
            "nodeid": node.nodeid,
            "name": "resources-%s" % node.nodeid,
            "source": json.dumps(source_config),
            "count": count,
        }

    def get_pref_label(self, nodevalue):
        """
        Gets the prefLabel of a concept value
        """
        return None

    def get_tile_data(self, tile):
        try:
            data = tile.data
            provisionaledits = tile.provisionaledits
        except:
            data = tile["data"]
            provisionaledits = tile["provisionaledits"]
        if data is not None and any(val is not None for val in data.values()):
            return data
        elif provisionaledits is not None and len(list(provisionaledits.keys())) > 0:
            if len(list(provisionaledits.keys())) > 1:
                logger.warning(_("Multiple provisional edits. Returning first edit"))
            userid = list(provisionaledits.keys())[0]
            return provisionaledits[userid]["value"]
        elif not data:
            logger.exception(_("Tile has no authoritative or provisional data"))
        else:
            return data

    def get_display_value(self, tile, node, **kwargs):
        """
        Returns a list of concept values for a given node
        """
        data = self.get_tile_data(tile)

        if data:
            display_value = data.get(str(node.nodeid))

            if display_value:
                return str(display_value)

    def get_search_terms(self, nodevalue, nodeid=None):
        """
        Returns an array of arches.app.search_term.SearchTerm objects
        """
        return []

    def append_search_filters(self, value, node, query, request):
        """
        Allows for modification of an elasticsearch bool query for use in
        advanced search
        """
        pass

    def append_null_search_filters(self, value, node, query, request):
        """
        Appends the search query dsl to search for fields that have not been populated
        """

        query.filter(Terms(field="graph_id", terms=[str(node.graph_id)]))

        data_exists_query = Exists(field=f"tiles.data.{str(node.pk)}")
        tiles_w_node_exists = Nested(path="tiles", query=data_exists_query)
        if value["op"] == "not_null":
            query.must(tiles_w_node_exists)
        elif value["op"] == "null":
            # search for tiles that don't exist
            null_query = Bool()
            null_query.must_not(tiles_w_node_exists)
            query.should(null_query)

            # search for tiles that do exist, but that have null or [] as values
            exists_query = Bool()
            exists_query.must(tiles_w_node_exists)
            exists_query.must(Terms(field="graph_id", terms=[str(node.graph_id)]))
            func_query = Dsl()
            func_query.dsl = {
                "function_score": {
                    "min_score": 1,
                    "query": exists_query.dsl,
                    "functions": [
                        {
                            "script_score": {
                                "script": {
                                    "source": """
                                    int null_docs = 0;
                                    for(tile in params._source.tiles){
                                        if(tile.nodegroup_id == params.nodegroup_id ){
                                            def val = tile.data.get(params.node_id);
                                            if (val == null || val == "" || (val instanceof List && val.length==0)) {
                                                null_docs++;
                                                break;
                                            }
                                        }
                                    }
                                    return null_docs;
                                """,
                                    "lang": "painless",
                                    "params": {
                                        "node_id": f"{str(node.pk)}",
                                        "nodegroup_id": f"{str(node.nodegroup_id)}",
                                    },
                                }
                            }
                        }
                    ],
                    "score_mode": "max",
                    "boost": 1,
                    "boost_mode": "replace",
                }
            }
            query.should(func_query)

    def pre_tile_save(self, tile, nodeid):
        """
        Called during tile.save operation but before the tile is actually saved to the database

        """
        pass

    def get_default_language_value_from_localized_node(self, tile, nodeid):
        """
        If value is internationalized, return only the first value in the i18n object
        """
        return tile.data[str(nodeid)]

    def post_tile_save(self, tile, nodeid, request):
        """
        Called after the tile is saved to the database

        """
        pass

    def post_tile_delete(self, tile, nodeid, index=True):
        """
        Called following the tile.delete operation

        """
        pass

    def is_multilingual_rdf(self, rdf):
        """
        Determines if the rdf snippet contains multiple languages that can be processed by a given datatype
        """
        return False

    def is_a_literal_in_rdf(self):
        """
        Convenience method to determine whether or not this datatype's `to_rdf` method will express
        its data as an RDF Literal value or as a more complex graph of nodes.
        :return:

        True: `to_rdf()` turns the range node tile data into a suitable Literal value
        False:  `to_rdf()` uses the data to construct something more complex.
        """
        return False

    def accepts_rdf_uri(self, uri):
        return False

    def get_rdf_uri(self, node, data, which="r"):
        if self.is_a_literal_in_rdf():
            return None
        return node

    def to_rdf(self, edge_info, edge):
        """
        Outputs an in-memory graph, converting the range tile data JSON into
        an appropriate RDF representation using rdflib
        """

        # default implementation that encodes the JSON serialisation
        # as a literal string, linked by 'RDF.value' to the source node
        # for this tile data
        from rdflib import Namespace, URIRef, Literal, Graph, BNode
        from rdflib.namespace import RDF, RDFS, XSD, DC, DCTERMS
        from arches.app.utils.betterJSONSerializer import JSONSerializer

        g = Graph()

        g.add((edge_info["r_uri"], RDF.type, URIRef(edge.rangenode.ontologyclass)))

        g.add((edge_info["d_uri"], URIRef(edge.ontologyproperty), edge_info["r_uri"]))
        g.add((edge_info["d_uri"], RDF.type, URIRef(edge.domainnode.ontologyclass)))

        if edge_info["domain_tile_data"] is not None:
            g.add(
                (
                    edge_info["d_uri"],
                    RDF.value,
                    Literal(JSONSerializer().serialize(edge_info["domain_tile_data"])),
                )
            )

        if edge_info["range_tile_data"] is not None:
            g.add(
                (
                    edge_info["r_uri"],
                    RDF.value,
                    Literal(JSONSerializer().serialize(edge_info["range_tile_data"])),
                )
            )

        return g

    def from_rdf(self, json_ld_node):
        raise NotImplementedError

    def validate_from_rdf(self, value):
        return self.validate(value)

    def collects_multiple_values(self):
        """
        Data type that can collect multiple values at once like DomainListDataType, etc...
        """

        return False

    def get_nodevalues(self, nodevalue):
        if nodevalue is None:
            return []
        elif not isinstance(nodevalue, (list, tuple)):
            return [nodevalue]
        return nodevalue

    def ignore_keys(self):
        """
        Each entry returned in the array is a string, consisting of the combination of two full URIs
        separated by a space -- the first is the URI of the property in the ontology,
        and the second is the class of the value of the property.
        When this key is encountered in incoming data, it will be ignored.
        This is useful for either when the data is handled internally by the datatype,
        or when the incoming data has annotations that should not be persisted.
        """

        return []

    def references_resource_type(self):
        """
        This resource references another resource type (eg resource-instance-datatype, etc...)
        """

        return False

    def default_es_mapping(self):
        """
        Default mapping if not specified is a text field
        """

        text_mapping = {
            "type": "text",
            "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}},
        }
        return text_mapping

    def get_es_mapping(self, nodeid):
        """
        Gets the es mapping associoated with the datatype
        """

        ret = None
        default_mapping = self.default_es_mapping()
        if default_mapping:
            ret = {
                "properties": {
                    "tiles": {
                        "type": "nested",
                        "properties": {
                            "data": {"properties": {str(nodeid): default_mapping}}
                        },
                    }
                }
            }
        return ret

    def to_json(self, tile, node):
        """
        Returns a value for display in a json object
        """
        return self.compile_json(tile, node)

    def compile_json(self, tile, node, **kwargs):
        """
        Compiles an object for presentation for use in the to_json method
        Arguments:
        tile -- (required) the tile model for the datatype
        node -- (required) the node model related to the tile

        Keyword Arguments:
        optional number of arguments to add to the opject
        """

        ret = {"@display_value": self.get_display_value(tile, node)}
        ret.update(kwargs)
        return ret

    def has_multicolumn_data(self):
        """
        Used primarily for csv exports - true if data
        for a node can span multiple columns
        """
        return False

    def get_column_header(self, node, **kwargs):
        """
        Returns a CSV column header or headers for a given node ID of this type
        """
        return node["file_field_name"]

    def pre_structure_tile_data(self, tile, nodeid, **kwargs):
        """
        Adds properties to a tile necessary for some clients, but not essential to the tile
        """
        pass

    def validate_node(self, node):
        """
        Confirms a node is properly configured to collect data.
        If improperly configured, this method should raise
        a GraphValidationError
        """
        pass
