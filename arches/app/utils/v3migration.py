import os
import csv
import json
import uuid
import psycopg2
from lxml import etree
from mimetypes import MimeTypes
from rdflib import Graph as RDFGraph
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import MakeValid
from arches.app.models.graph import Graph
from arches.app.models.models import Node, File, NodeGroup
from arches.app.models.tile import Tile
from arches.app.utils import v3utils
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.models.system_settings import settings


def fix_v3_value(value, datatype):
    """in some cases, the v3 data must be modified before it can be saved
    into a v4 tile. this conversion is based on the v4 node datatype."""

    # convert the WKT geometry representation from v3 to a geojson feature
    # collection which is what is needed in v4
    if datatype == "geojson-feature-collection":

        # assume that if a dictionary is passed in, it is already geojson
        if not isinstance(value, dict):
            geom = json.loads(GEOSGeometry(value).geojson)
            value = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "id": str(uuid.uuid4()),
                        "geometry": geom,
                        "properties": {}
                    }
                ]
            }

    # sanitize number input
    elif datatype == "number":
        value = value.replace(",", "")
        try:
            value = int(value)
        except ValueError:
            value = float(value)

    elif datatype == "date":
        # kinda hacky but need to remove the T00:00:00 from the end of the
        # date string, and datetime doesn't handle dates before 1900 so just
        # use basic string slicing, as all v3 dates will end with T00:00:00.
        value = value[:-9]

    elif datatype == "file-list":

        filename = os.path.basename(value)
        fullpath = os.path.join(settings.MEDIA_ROOT, 'uploadedfiles', filename)

        # handle the fact that file names could be too long, > 100 characters.
        # a bit more complicated that you would expect, in order to accommodate
        # iterative development.
        shortenedpath = ""
        if len(filename) > 100:
            shortname = os.path.splitext(filename)[0][:96]+os.path.splitext(filename)[1]
            shortenedpath = fullpath.replace(filename, shortname)

        if not os.path.isfile(fullpath) and not os.path.isfile(shortenedpath):
            print "expected file doesn't exist: {}".format(fullpath)
            print "all files must be transferred before migration can continue"
            exit()

        if shortenedpath != "":
            if not os.path.isfile(shortenedpath):
                os.rename(fullpath, shortenedpath)
            fullpath = shortenedpath
            filename = shortname

        # create ORM file object
        file_obj = File()
        file_obj.path = filename

        try:
            file_obj.save()
        except Exception as e:
            print "Error saving file: {}".format(fullpath)
            print e
            exit()

        # construct the full json needed to define a file-list node in a tile
        stats = os.stat(fullpath)
        type = MimeTypes().guess_type(fullpath)[0]
        value = [{
            "name": filename,
            "file_id": str(file_obj.pk),
            "url": str(file_obj.path.url).replace("files/", "files/uploadedfiles/"),
            "status": 'uploaded',
            "index": 0,
            "lastModified": stats.st_mtime,
            "height": None,
            "width": None,
            "type": type,
            "size": stats.st_size,
            # "content":"blob:http://localhost:8000/24dd8daa-da29-49ec-805a-3dd8a683162c",
            "accepted": True
        }]

    return value


def get_empty_feature_collection():
    """ returns a dictionary representing an empty geojson feature collection. """

    collection = {
        "type": "FeatureCollection",
        "features": []
    }

    return collection


def add_wkt_to_geojson_collection(wkt, collection):
    """ takes an input WKT value, converts to geojson (with some built-in
    validation operations) and then adds it to the input collection. return
    the collection. """

    # connect to the database in order to use it for postgis functions
    db = settings.DATABASES['default']
    db_conn = "dbname = {} user = {} host = {} password = {} port = {}".format(
        db['NAME'], db['USER'], db['HOST'], db['PASSWORD'], db['PORT'])
    conn = psycopg2.connect(db_conn)
    cur = conn.cursor()

    # create and execute SQL statement to force a valid direction on
    # coordinates in polygons
    sql = '''
    SELECT ST_AsGeoJSON(ST_Reverse(ST_ForceRHR('{0}')));
    '''.format(wkt)
    cur.execute(sql)
    rows = cur.fetchall()

    try:
        geo_json = json.loads(rows[0][0])

        # iterate coords in polygons to remove duplicate coordinates
        if geo_json['type'] == "Polygon":
            lastcoord = None
            for index, coord in enumerate(geo_json['coordinates'][0]):
                if coord == lastcoord:
                    geo_json['coordinates'][0].pop(index)
                lastcoord = coord

        # create feature json
        feature = {
            "type": "Feature",
            "id": str(uuid.uuid4()),
            "geometry": geo_json,
            "properties": {}
        }
    except Exception as e:
        print "Error parsing this WKT: {}".format(wkt)
        print e
        feature = False

    if feature:
        collection['features'].append(feature)

    return collection


def flatten_geometries(resource_data, node_lookup):
    """ take the full input list of v3 nodes, find all geometries and combine
    them. this is necessary, as WKTs come separately from v3, but should be
    stored as a single geojson feature collection in v4. """

    geom_found = False
    to_remove = []

    # create empty collection
    collection = get_empty_feature_collection()

    # iterate nodes, create geometry from spatial nodes, add to collection,
    # and remove all spatial nodes besides the first one.
    for index, dp in enumerate(resource_data):
        dt = node_lookup[dp[0]]['v4_datatype']

        if dt == "geojson-feature-collection":
            collection = add_wkt_to_geojson_collection(dp[1], collection)
            if geom_found:
                to_remove.append(dp)
            else:
                geom = index
                geom_found = True

    # if geometry has been found, insert the full collection at the position
    # of the first spatial node (which has not been removed)
    if geom_found:
        resource_data[geom] = (resource_data[geom][0], collection)
    resource_data = [i for i in resource_data if i not in to_remove]

    return resource_data


def duplicate_tile_json(tilejson):
    """returns a duplicate of the tilejson that is passed in, but
    with all data values set to None."""

    newtile = {
        "resourceinstance_id": tilejson['resourceinstance_id'],
        "provisionaledits": tilejson['provisionaledits'],
        "parenttile_id": tilejson['parenttile_id'],
        "nodegroup_id": tilejson['nodegroup_id'],
        "sortorder": tilejson['sortorder'],
        "data": {},
        "tileid": uuid.uuid4(),
    }
    for k in tilejson['data'].keys():
        newtile['data'][k] = None

    return newtile


def get_nodegroup_tilegroup(v4_node_name, nodes, resource_id, verbose=False):

    # get the corresponding v4 node and then get the tile for its nodegroup
    v4_node = nodes.get(name=v4_node_name)
    ng_tile = Tile().get_blank_tile(v4_node.nodegroup_id, resourceid=resource_id)

    if verbose:
        print "  ", ng_tile.data
        print "  ", ng_tile.tiles

    # if there are child tiles, then the ng_tile.tileid needs to be set
    # (not sure why this is the case, but it is)
    if ng_tile.tileid is None:
        ng_tile.tileid = uuid.uuid4()

    # create a raw json representation of the node group tile and its children
    # and put these into a flat list of tiles that is returned
    tile_json = {
        "resourceinstance_id": resource_id,
        "provisionaledits": None,
        "parenttile_id": ng_tile.parenttile_id,
        "nodegroup_id": ng_tile.nodegroup_id,
        "sortorder": 0,
        "data": ng_tile.data,
        "tileid": ng_tile.tileid,
    }
    output_tiles = [tile_json]
    for tile in ng_tile.tiles:
        child_tile_json = {
            "tileid": tile.tileid,
            "resourceinstance_id": resource_id,
            "nodegroup_id": tile.nodegroup_id,
            "sortorder": 0,
            "provisionaledits": None,
            "parenttile_id": ng_tile.tileid,
            "data": tile.data,
        }
        output_tiles.append(child_tile_json)

    return output_tiles


class v3PreparedResource:
    """ Used to convert data for a single v3 resource into corresponding set
    of v4 json. """

    def __init__(self, resource_id, graph_id, data):

        self.resourceid = str(resource_id)
        self.graphid = str(graph_id)
        self.v3_json = data

        def process_children(children, processed=[]):
            """ recursively process the nested contents of v3 json and convert
            to a flat list of tuples: [(v3 node name, v3 node value)]"""

            # iterate all children of this entity
            for child in children:

                # get the nested child entities
                grandchildren = child['child_entities']

                # if there are nested chilren, process each one
                if len(grandchildren) > 0:
                    process_children(grandchildren, processed)

                # don't attempt to migrate semantic nodes
                if child['businesstablename'] == "":
                    continue

                # don't attempt to migrate empty nodes
                if child['value'].rstrip() == "":
                    continue

                # append this entityid and value to the output
                processed.append((child['entitytypeid'], child['value']))

            return processed

        self.node_list = process_children(self.v3_json['child_entities'])

        # this attribute is populated during self.process(), but is
        # left empty upon object instantiation
        self.tiles = []

    def get_empty_resource(self):
        """ returns the skeleton of v4 json for this resource. """

        res = {
            "resourceinstance": {
                "graph_id": self.graphid,
                "resourceinstanceid": self.resourceid,
                "legacyid": self.resourceid
            },
            "tiles": []
        }

        return res

    def strip_empty_tile_values(self):
        """ iterate all tiles and remove any data in the tile['data'] that does
        not have a value """

        for tile in self.tiles:
            data = dict([(k, v) for k, v in tile['data'].items() if v is not None])
            tile['data'] = data

    def put_primary_name_last(self):
        """ this method ensures that the Primary name is placed at the end of
        the tile list. this is necessary to ensure that the Primary name is
        used for the "get resource descriptors" function."""

        p_name_index = None
        for index, tile in enumerate(self.tiles):
            try:
                # currently, these hard-coded uuids work for hku models, but
                # should be refactored way back to the rm_configs.json file
                name_type = tile['data']["185b9091-943d-11e8-8c9e-94659cf754d0"]
                if name_type == "a4c88313-52c5-4b6a-9579-3fc5aad17335":
                    p_name_index = index
                    break
            except KeyError:
                continue

        if p_name_index is not None:
            self.tiles += [self.tiles.pop(index)]

    def process(self, v4_nodes, node_lookup, verbose=False):
        """ this method processes the v3 node list and turns it into a series of
        tiles that are appended to self.tiles. the full list of v4 nodes must be
        passed in (nodes attached to the resource model that this resource is an
        instance of), as well as the node lookup that links v3 node names with
        v4 node names. """

        # duplicate what is stored in self.node_list.
        resource_data = list(self.node_list)
        ct_total = len(resource_data)

        # first combine all of the geometries into a single value
        resource_data = flatten_geometries(resource_data, node_lookup)
        ct_geom = len(resource_data)

        if verbose:
            if not ct_total == ct_geom:
                print "{} {} - (total) (geom flattened) - {}".format(ct_total,
                                                                     ct_geom, self.resourceid)
            for i in resource_data:
                print i
            print "resource_data full length", len(resource_data)

        # begin looping though the v3 resource data list
        while len(resource_data):
            if verbose:
                print "\nSTARTING WHILE LOOP ---"
                print "resource_data current length", len(resource_data)
                print "first in line:", resource_data[0][0], node_lookup[resource_data[0][0]]['v4_uuid']

            # get the v4 name of the first node in the resource list
            v4_name = node_lookup[resource_data[0][0]]['v4_name']

            # obtain a blank tile for the nodegroup that contains the corresponding
            tilegroup_json = get_nodegroup_tilegroup(v4_name, v4_nodes, self.resourceid,
                                                     verbose=verbose)

            # get a list of all the node UUIDs in this tile and its children
            all_node_options = []
            for t in tilegroup_json:
                all_node_options += t['data'].keys()

            # begin iterating resource_data, and trying to fill tile['data'] values
            # in the current tile group. if a node in the iteration doesn't fit
            # in any of the tiles, assume this is a new branch, break the for loop,
            # and restart the while loop to get the next tile group. remove any
            # nodes from resource_data whose value has been placed in a tile.
            if verbose:
                print "number of tiles in tilegroup:", len(tilegroup_json)
                print "\nSTARTING FOR LOOP ---"
            used = []
            for index, dp in enumerate(resource_data):

                if verbose:
                    print dp[0]
                dt = node_lookup[dp[0]]['v4_datatype']

                # first fix the data value
                value = fix_v3_value(dp[1], dt)

                # now get the UUID of the v4 target node
                v4_uuid = node_lookup[dp[0]]['v4_uuid']

                # break the for loop (and subsequently, restart the while loop)
                # if this node is not in the current tile group
                if v4_uuid not in all_node_options:
                    if verbose:
                        print "<< breaking the loop because this node is not in the current tilegroup >>"
                    break

                # first check if the node for this data has already been
                # populated, in which case a new ng tilegroup is needed
                if verbose:
                    print "    is this node already filled? >",
                skip = False
                if v4_uuid in all_node_options:
                    for tile in tilegroup_json:
                        if v4_uuid in tile['data'].keys():
                            if not tile['data'][v4_uuid] is None and not dt == "concept-list":
                                ng = NodeGroup.objects.get(nodegroupid=tile['nodegroup_id'])
                                if ng.parentnodegroup_id is None and ng.cardinality != "n":
                                    skip = True

                if skip:
                    if verbose:
                        print "yes"
                        print "<< breaking the loop because this node already has data in the current tilegroup >>"
                    break
                else:
                    if verbose:
                        print "no"

                # find the tile that will hold the value
                for tile in tilegroup_json:

                    # skip if the node is not in this tile
                    if v4_uuid not in tile['data'].keys():
                        continue

                    # if this is a concept-list node, assume the value should
                    # be appended to the existing concept-list value, if extant
                    if dt == "concept-list":
                        if verbose:
                            print tile['data'][v4_uuid], "="*60
                        # set value
                        if isinstance(tile['data'][v4_uuid], list):
                            tile['data'][v4_uuid].append(value)
                        else:
                            tile['data'][v4_uuid] = [value]
                        tileid_used = tile['tileid']
                    else:
                        # this implicitly catches the situation where earlier logic
                        # has determined that the cardinality will allow multiple
                        # of this tile. therefore a new tile is made, the value is
                        # set in the new tile (ignoring the currently iterated tile)
                        # and then the new tile is placed at the beginning of the
                        # current tilegroup_json list.
                        if tile['data'][v4_uuid] is not None:
                            newtile = duplicate_tile_json(tile)
                            newtile['data'][v4_uuid] = value
                            tilegroup_json.insert(0, newtile)
                            tileid_used = newtile['tileid']

                        # otherwise, this is the place where the majority of values
                        # are set.
                        else:
                            tile['data'][v4_uuid] = value
                            tileid_used = tile['tileid']
                    used.append(index)
                    if verbose:
                        print "    placing value into tile:", tileid_used, 'nodeid -->',
                        print v4_uuid, node_lookup[dp[0]]['v4_name']
                    break

            if verbose:
                print "removing used nodes:", used
                print "resource_data len before:", len(resource_data)
            resource_data = [v for i, v in enumerate(resource_data) if i not in used]
            if verbose:
                print "resource_data len after:", len(resource_data)

            # append the tile group to self.tiles
            self.tiles += tilegroup_json

        # final processing, now that self.tiles is fully populated
        self.strip_empty_tile_values()
        self.put_primary_name_last()

    def get_json(self):
        """ returns the full v4 json for this resource. note that self.process()
        must be run before this method is called, otherwise self.tiles will be
        empty. """

        v4_json = self.get_empty_resource()
        v4_json['tiles'] = self.tiles

        return v4_json


class v3Importer:
    """ This class is used at the Resource Model-level to support v3 migration.

    It must be instantiated with the v3_data_dir (a structured subdirectory in
    a standard v4 package), the name of the resource model this class will
    represent, and the v3 json export file (though in the future this could be
    inferred from the v3_data_dir, or, better, v3_data_dir should be replaced
    with the rm_configs content itself). An optional truncate argument can be
    used to limit the number of resources that are loaded from the v3 json. """

    def __init__(self, v3_data_dir, v4_graph_name, v3_json_file, truncate=None, exclude=[], only=[]):

        if not os.path.isfile(v3_json_file):
            raise Exception("v3 business data file {} does not exist".format(
                v3_json_file))

        self.source_file = v3_json_file

        self.v4_graph = Graph.objects.get(name=v4_graph_name)
        self.v4_graph_name = v4_graph_name
        self.v4_nodes = Node.objects.filter(graph=self.v4_graph)

        # use this method to acquire the v3 configs, and full lookup paths
        v3_config = v3utils.get_v3_config_info(v3_data_dir, v4_graph_name=v4_graph_name)

        # load the info stored in the rm_configs file
        self.v3_graph_name = v3_config["v3_entitytypeid"]
        self.v3_nodes_csv = v3_config["v3_nodes_csv"]
        self.v3_v4_node_lookup = v3_config["v3_v4_node_lookup"]

        # create better node_lookup that holds more information
        self.node_lookup = self.augment_node_lookup()

        # finally, do the actual loading of the v3 data into this class
        self.v3_resources = self.load_v3_data(truncate=truncate, exclude=exclude, only=only)

    def augment_node_lookup(self):
        """takes the node lookup csv and converts to a dictionary
        with more information added to it for each node."""

        lookup_path = self.v3_v4_node_lookup
        new_and_improved = {}
        with open(lookup_path, 'rb') as openfile:
            reader = csv.DictReader(openfile)

            for row in reader:
                try:
                    n = self.v4_nodes.get(name=row['v4_node'])
                except Node.DoesNotExist:
                    raise Exception("{} in {} lookup csv is not matched "
                                    "with a valid v4 node.".format(row['v3_node'],
                                                                   lookup_path))
                new_and_improved[row['v3_node']] = {
                    'v4_name': row['v4_node'],
                    'v4_uuid': str(n.nodeid),
                    'v4_datatype': n.datatype,
                }

        return new_and_improved

    def load_v3_data(self, truncate=None, exclude=[], only=[]):
        """ loads the data that is in the v3 export file. limits to the number
        in truncate, if truncate is not none."""

        with open(self.source_file, 'rb') as openfile:
            v3_json = json.loads(openfile.read())

        # get all the resources matching this resource graph name
        v3_resources = [r for r in v3_json['resources'] if r['entitytypeid'] == self.v3_graph_name]

        # filter out any empty resources
        v3_resources = [r for r in v3_resources if len(r['child_entities']) != 0]

        # filter out any that are explicitly excluded
        self.v3_resources = [r for r in v3_resources if r['entityid'] not in exclude]

        # filter out all but the ones specified in the only argument
        if len(only) > 0:
            self.v3_resources = [r for r in self.v3_resources if r['entityid'] in only]

        # if the list should be truncated, only take that many resources from the front of the list
        if truncate:
            self.v3_resources = self.v3_resources[:truncate]

        return self.v3_resources

    def convert_v3_data(self, verbose=False):
        """ creates v4 resources from all the loaded v3 resources in
        self.v3_resources. returns these resources. """

        resources = []
        for res in self.v3_resources:

            v3_resource = v3PreparedResource(res['entityid'], self.v4_graph.graphid, res)
            v3_resource.process(self.v4_nodes, self.node_lookup, verbose=verbose)
            v4_json = v3_resource.get_json()

            resources.append(v4_json)

        return resources

    def get_v4_json(self, verbose=False):

        resources = self.convert_v3_data(verbose=verbose)
        v4_json = {'business_data': {'resources': resources}}

        return v4_json

    def write_v4_json(self, dest_path, verbose=False):

        out_json = self.get_v4_json(verbose=verbose)
        with open(dest_path, 'wb') as openfile:
            openfile.write(JSONSerializer().serialize(out_json, indent=4))

        return dest_path


class v3SkosConverter:
    """
    This utility converts an Arches 3 SKOS-formatted scheme file into
    an Arches 4 thesaurus file and collections file for import
    """

    def __init__(self, skos_file, name_space="http://localhost:8000/"):

        with open(skos_file, "rb") as incoming_skos:
            skos = incoming_skos.read()
            skos = skos.replace("http://www.archesproject.org/", name_space)

        self.v3_skos = skos
        self.uuid_lookup = {}

    def prepare_export(self, namespaces, nodes):
        """
        return a graph with the desired node type for writing out to XML,
        with cleaned-up namespaces
        """

        output_graph = RDFGraph()
        [output_graph.bind(k, v) for k, v in namespaces.items()]

        [output_graph.parse(
            data=etree.tostring(node),
            nsmap=namespaces)
         for node in nodes]

        return output_graph

    def export(self, file_path, content):

        with open(file_path, 'w') as fh:
            fh.write(content)
            fh.close

    def write_skos(self, directory, uuid_collection_file=None):

        def new_or_existing_uuid(preflabel, uuid_lookup={}):
            """
            take a topConcept's prefLabel node, parse the JSON within, and
            return a new or existing UUID for the collection based on
            whether we already have one for the JSON's `value` key
            """
            preflabel_val = json.loads(preflabel.text)['value']

            if preflabel_val in uuid_lookup:
                return uuid_lookup[preflabel_val]
            else:
                new_uuid = str(uuid.uuid4())
                uuid_lookup[preflabel_val] = new_uuid
                return new_uuid

        def new_preflabel_uuid(preflabel):
            """
            Concept Values in Arches have a UUID (stored in the embedded JSON)
            and a 1-1 mapping with their Concept; if a Collection shares a
            prefLabel with a Concept, it needs a new ID to avoid
            clobbering the same attribute on the existing Concept
            """
            working = json.loads(preflabel.text)
            working['id'] = unicode(uuid.uuid4())
            preflabel.text = json.dumps(working)

        if uuid_collection_file:
            with open(uuid_collection_file, "rb") as openfile:
                uuid_lookup = json.loads(openfile.read())
        else:
            uuid_lookup = {}

        skos_xml = etree.fromstring(self.v3_skos)
        namespaces = skos_xml.nsmap

        # retrieve concepts and collections from skos with regular ol' xpath
        concepts = skos_xml.xpath("./skos:Concept", namespaces=namespaces)
        collections = skos_xml.xpath("./skos:Collection", namespaces=namespaces)
        top_concepts = skos_xml.xpath(".//skos:hasTopConcept", namespaces=namespaces)

        top_concept_uris = [
            concept.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource")
            for concept in top_concepts]

        for concept in concepts:
            uri = concept.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about")
            if uri in top_concept_uris:
                # create a new top level Collection based on the topConcept
                collection = etree.Element(
                    "{http://www.w3.org/2004/02/skos/core#}Collection",
                    nsmap=namespaces)

                # migrate nested concepts and attributes into new
                # Collection
                #################################################

                # hacky-deepcopy the TopConcept to avoid mutating original
                # (still needed for thesaurus export)
                working_concept = etree.fromstring(etree.tostring(concept))

                # give the collection a UUID based on the prefLabel
                col_preflabel = working_concept.find('./skos:prefLabel',
                                                     namespaces=namespaces)

                new_preflabel_uuid(col_preflabel)

                col_uuid = new_or_existing_uuid(col_preflabel, uuid_lookup=uuid_lookup)
                fq_uuid = namespaces['arches'] + col_uuid
                collection.set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about",
                               fq_uuid)

                # change skos:narrower into valid skos:member tags in the
                # Concept's first-level children
                for narrower in working_concept.xpath("skos:narrower",
                                                      namespaces=namespaces):
                    narrower.tag = "{http://www.w3.org/2004/02/skos/core#}member"

                # Append the child concepts to the new Collection
                [collection.append(child) for child in
                 working_concept.getchildren()]

                collections.append(collection)

        # prepare raw XML
        thesaurus_skos = self.prepare_export(namespaces,
                                             concepts).serialize(format='pretty-xml')
        collections_skos = self.prepare_export(namespaces,
                                               collections).serialize(format='pretty-xml')

        # export files
        self.export(os.path.join(directory, 'concepts', 'thesaurus.xml'), thesaurus_skos)
        self.export(os.path.join(directory, 'collections', 'collections.xml'), collections_skos)

        # update this class' uuid_lookup
        self.uuid_lookup = uuid_lookup

    def write_uuid_lookup(self, filepath):

        with open(filepath, 'wb') as uuid_store:
            uuid_store.write(json.dumps(self.uuid_lookup, indent=4, sort_keys=True))
            uuid_store.close()
