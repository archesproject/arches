import os
import csv
import json
import uuid
import psycopg2
from mimetypes import MimeTypes
from rdflib import Graph as RDFGraph, Namespace, RDF, URIRef, Literal
from rdflib.namespace import DCTERMS, SKOS, FOAF, NamespaceManager
from django.db.utils import OperationalError
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import MakeValid
from arches.app.models.graph import Graph
from arches.app.models.models import Node, File, NodeGroup
from arches.app.models.tile import Tile
from arches.app.utils import v3utils
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.models.system_settings import settings

ARCHES = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)


class DataValueConverter:
    def __init__(self, skip_file_check=False):

        self.skip_file_check = skip_file_check
        db = settings.DATABASES["default"]
        db_conn = "dbname = {} user = {} host = {} password = {} port = {}".format(
            db["POSTGIS_TEMPLATE"], db["USER"], db["HOST"], db["PASSWORD"], db["PORT"]
        )
        conn = psycopg2.connect(db_conn)
        self.dbcursor = conn.cursor()

    def fix_v3_value(self, value, v4nodeinfo):
        """in some cases, the v3 data must be modified before it can be saved
        into a v4 tile. this conversion is based on the v4 node datatype."""

        datatype = v4nodeinfo["v4_datatype"]

        # replace the bad characters here
        if datatype == "string":
            value = value

        # convert the WKT geometry representation from v3 to a geojson feature
        # collection which is what is needed in v4. do some sanitation as well.
        if datatype == "geojson-feature-collection":

            # create and execute SQL statement to force a valid direction on
            # coordinates in polygons and remove any repeated points
            sql = """
            SELECT ST_AsGeoJSON(ST_RemoveRepeatedPoints(ST_Reverse(ST_ForceRHR('{0}'))));
            """.format(
                value
            )
            self.dbcursor.execute(sql)
            rows = self.dbcursor.fetchall()

            # convert the validated geometry to a geojson FeatureCollection
            geojson = json.loads(rows[0][0])
            value = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "id": str(uuid.uuid4()),
                        "geometry": geojson,
                        "properties": {},
                    }
                ],
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
            fullpath = os.path.join(settings.MEDIA_ROOT, "uploadedfiles", filename)

            # handle the fact that file names could be too long, > 100 characters.
            # a bit more complicated that you would expect, in order to accommodate
            # iterative development.
            shortenedpath = ""
            if len(filename) > 100:
                shortname = (
                    os.path.splitext(filename)[0][:96] + os.path.splitext(filename)[1]
                )
                shortenedpath = fullpath.replace(filename, shortname)

            if not self.skip_file_check:
                if not os.path.isfile(fullpath) and not os.path.isfile(shortenedpath):
                    print("expected file doesn't exist: {}".format(fullpath))
                    print("all files must be transferred before migration can continue")
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
                print("Error saving file: {}".format(fullpath))
                print(e)
                exit()

            # construct the full json needed to define a file-list node in a tile
            try:
                stats = os.stat(fullpath)
                lastModified = stats.st_mtime
                size = stats.st_size
            except Exception as e:
                lastModified = None
                size = None
            ftype = MimeTypes().guess_type(fullpath)[0]
            value = [
                {
                    "name": filename,
                    "file_id": str(file_obj.pk),
                    "url": str(file_obj.path.url).replace(
                        "files/", "files/uploadedfiles/"
                    ),
                    "status": "uploaded",
                    "index": 0,
                    "lastModified": lastModified,
                    "height": None,
                    "width": None,
                    "type": ftype,
                    "size": size,
                    # "content":"blob:http://localhost:8000/24dd8daa-da29-49ec-805a-3dd8a683162c",
                    "accepted": True,
                }
            ]

        return value


class v3PreparedResource:
    """Used to convert data for a single v3 resource into corresponding set
    of v4 json."""

    def __init__(
        self,
        data,
        graph_id,
        node_lookup,
        mergenodes,
        verbose=False,
        dt_converter=DataValueConverter(),
    ):

        self.resourceid = str(data["entityid"])
        self.graphid = str(graph_id)
        self.v3_json = data
        self.mergenodes = mergenodes
        self.node_lookup = node_lookup
        self.verbose = verbose
        self.geom_ct = 0
        self.dt_converter = dt_converter
        self.node_list = self.prepare_node_list()

        # this attribute is populated during self.process(), but is
        # left empty upon object instantiation
        self.tiles = []

    def prepare_node_list(self):
        """turns the input v3 json into a flat node list, which is
        basically the same as a v3 .arches file"""

        def process_group(entity, processed=[]):
            """recursively process the contents of  a v3 json branch
            and convert to a flat list of tuples: [(v3 node name, v3 node value)]"""

            # disregard semantic and empty nodes
            if entity["businesstablename"] != "" and entity["value"].rstrip() != "":
                processed.append((entity["entitytypeid"], entity["value"]))

            # iterate and process all children of this entity
            for child in entity["child_entities"]:
                process_group(child, processed)

            return processed

        def get_group_branches(entity, outgroups=[]):
            """get the group branches from the entity based on v3 mergenodes"""

            look_further = any(
                [
                    child["entitytypeid"] in self.mergenodes
                    for child in entity["child_entities"]
                ]
            )

            if look_further or entity["entitytypeid"] in self.mergenodes:
                for child in entity["child_entities"]:
                    get_group_branches(child, outgroups=outgroups)
            else:
                outgroups.append(entity)

            return outgroups

        groups = get_group_branches(self.v3_json)
        if self.verbose:
            print("\nv3 MERGENODES")
            print("################")
            print(self.mergenodes)
            print("\nGROUPING SUMMARY")
            print("################")
            print("number of groups: {}".format(len(groups)))

        outlist = []
        for branch_num, group in enumerate(groups):
            branch_data = process_group(group, processed=[])

            if self.verbose:
                print(
                    "{} - datapoints: {}".format(
                        group["entitytypeid"], len(branch_data)
                    )
                )
            for node in branch_data:
                outlist.append(node + (branch_num,))

        # The following code block can be very helpful while developing and debugging
        # the way v3 json is parsed.

        # with open(self.v3_json['entityid']+"-v3.json", "wb") as f:
        # json.dump(self.v3_json, f, indent=1)

        # with open(self.v3_json['entityid']+"-nodelist.csv", "wb") as f:
        # writer = csv.writer(f)
        # writer.writerow(["entitytypeid", "value", "branch_num"])
        # for i in outlist:
        # writer.writerow(i)

        # exit()

        return outlist

    def get_empty_resource(self):
        """returns the skeleton of v4 json for this resource."""

        res = {
            "resourceinstance": {
                "graph_id": self.graphid,
                "resourceinstanceid": self.resourceid,
                "legacyid": self.resourceid,
            },
            "tiles": [],
        }

        return res

    def strip_empty_tile_values(self):
        """iterate all tiles and remove any data in the tile['data'] that does
        not have a value"""

        for tile in self.tiles:
            data = dict(
                [(k, v) for k, v in list(tile["data"].items()) if v is not None]
            )
            tile["data"] = data

    def reorder_tiles_by_value(self, nodeid=None, valueid=None):
        """this method can ensure that the Primary name is placed at the end of
        the tile list. this is necessary to ensure that the Primary name is
        used for the "get resource descriptors" function."""

        p_name_index = None
        for index, tile in enumerate(self.tiles):
            try:
                node_value = tile["data"][nodeid]
                if node_value == valueid:
                    p_name_index = index
                    break
            except KeyError:
                continue

        if p_name_index is not None:
            self.tiles += [self.tiles.pop(index)]

    def process(self, v4_nodes):
        """this method processes the v3 node list and turns it into a series of
        tiles that are appended to self.tiles. the full list of v4 nodes must be
        passed in (nodes attached to the resource model that this resource is an
        instance of), as well as the node lookup that links v3 node names with
        v4 node names."""

        # duplicate what is stored in self.node_list.
        resource_data = list(self.node_list)
        ct_total = len(resource_data)

        if self.verbose:
            print("\nFULL RESOURCE DATA")
            print("##################")
            for i in resource_data:
                print(i)
            print("resource data full length: {}".format(len(resource_data)))

        # begin looping though the v3 resource data list
        last_group = resource_data[0][2]
        while len(resource_data):

            if self.verbose:
                fp = resource_data[0][0]
                print("\nSTARTING WHILE LOOP")
                print("###################")
                print("resource_data current length: {}".format(len(resource_data)))
                print(
                    "first in line: {} {}".format(fp, self.node_lookup[fp]["v4_uuid"])
                )
                print("group number of first in line: {}".format(resource_data[0][2]))

            # get the v4 name of the first node in the resource list
            v4_name = self.node_lookup[resource_data[0][0]]["v4_name"]

            # obtain a blank tile for the nodegroup that contains the corresponding
            tilegroup_json = v3utils.get_nodegroup_tilegroup(
                v4_name, v4_nodes, self.resourceid, verbose=self.verbose
            )

            # get a list of all the node UUIDs in this tile and its children
            all_node_options = []
            for t in tilegroup_json:
                all_node_options += list(t["data"].keys())

            if self.verbose:
                print("number of tiles in tilegroup: {}".format(len(tilegroup_json)))

            # begin iterating resource_data, and trying to fill tile['data'] values
            # in the current tile group. if a node in the iteration doesn't fit
            # in any of the tiles, assume this is a new branch, break the for loop,
            # and restart the while loop to get the next tile group. at the end, remove any
            # nodes from resource_data whose values have been placed in a tile.
            if self.verbose:
                print("\nSTARTING FOR LOOP")
                print("=================")
            used = []
            for index, dp in enumerate(resource_data):

                group_num = dp[2]
                if self.verbose:
                    print("\n-- {} group {} --".format(dp[0], group_num))

                v4nodeinfo = self.node_lookup[dp[0]]
                dt = self.node_lookup[dp[0]]["v4_datatype"]

                # first fix the data value
                value = self.dt_converter.fix_v3_value(dp[1], v4nodeinfo)

                # now get the UUID of the v4 target node
                v4_uuid = self.node_lookup[dp[0]]["v4_uuid"]

                # break the for loop (and subsequently, restart the while loop)
                # if this node is not in the current tile group
                if v4_uuid not in all_node_options:
                    last_group = group_num
                    if self.verbose:
                        print(
                            "<< breaking the loop because this node is not in the current tilegroup >>"
                        )
                    break

                # if this node is part of a new group, break the for loop and start the while loop over
                # but not if the parent node group has a cardinality of 1 in which case this node should
                # be coerced into the previous group
                if group_num != last_group:

                    # figure out if the parent of this tilegroup has cardinality of 1.
                    # use the last tile in line to find the parent nodegroup, this is because
                    # in some (but not all) cases the first tile in line represents the parent
                    # (and therefore has no parent itself).
                    single_parent = False
                    last_ng = NodeGroup.objects.get(
                        nodegroupid=tilegroup_json[-1]["nodegroup_id"]
                    )
                    if last_ng.parentnodegroup_id is not None:
                        parent_ng = NodeGroup.objects.get(
                            nodegroupid=last_ng.parentnodegroup_id
                        )
                        if parent_ng.cardinality == "1":
                            single_parent = True

                    if single_parent is False:
                        if self.verbose:
                            print(
                                "<< breaking the loop because this node has a new group number >>"
                            )
                        last_group = group_num
                        break
                    else:
                        if self.verbose:
                            print(
                                "-- coercing to previous group because parent cardinality is 1 --"
                            )

                if self.verbose:
                    try:
                        print("v3 value: {}".format(dp[1]))
                        print("v4 value: {}".format(value))
                    except UnicodeEncodeError:
                        print(
                            "v3/v4 value: error encoding to ascii for print statement"
                        )

                # find the tile that will hold the value
                for tile in tilegroup_json:

                    # skip if the node is not in this tile
                    if v4_uuid not in list(tile["data"].keys()):
                        continue

                    if self.verbose:
                        print(
                            "matched to: {} {}".format(
                                self.node_lookup[dp[0]]["v4_name"], v4_uuid
                            )
                        )

                    tileid_used = tile["tileid"]
                    make_duplicate = False

                    # if there is no data in the tile where this new value should be placed,
                    # then enter the value. this is where the majority of the action takes place
                    if tile["data"][v4_uuid] is None:
                        v3utils.set_tile_data(tile, v4_uuid, dt, value)
                        if self.verbose:
                            print("action: placing value in empty tile")

                    # if there is already a value in the tile where this new value should be
                    # placed, then we need to do a little more investigation
                    else:

                        # first check to see if this value was in the same v3 group as the last value
                        if last_group == group_num:

                            # if it's a concept-list, just append the value to the existing list
                            if dt == "concept-list":
                                tile = v3utils.set_tile_data(tile, v4_uuid, dt, value)
                                if self.verbose:
                                    print(
                                        "action: appending value to existing concept-list"
                                    )

                            # otherwise, duplicate the tile if cardinality allows
                            else:

                                ng = NodeGroup.objects.get(
                                    nodegroupid=tile["nodegroup_id"]
                                )
                                if ng.cardinality == "n":
                                    make_duplicate = True

                                # In this case, a non-concept-list node exists but the v4 graph does not allow
                                # a duplicate of the tile to be made. Print a warning message.
                                else:
                                    print(self.resourceid)
                                    print(dp[0])
                                    print(
                                        "WARNING: A new tile should be added here, but the cardinality of 1 "
                                        "does not allow it. This data will be lost. You may want to review "
                                        "your v4 graph."
                                    )

                        # if this was in a different group in v3 (but has passed the single parent test above)
                        # then a new tile should be made and appended to this group.
                        elif last_group != group_num:
                            make_duplicate = True

                    if make_duplicate is True:
                        newtile = v3utils.duplicate_tile_json(tile)
                        newtile = v3utils.set_tile_data(newtile, v4_uuid, dt, value)
                        tilegroup_json.insert(0, newtile)
                        tileid_used = newtile["tileid"]
                        if self.verbose:
                            print(
                                "action: adding a new tile to the same group (cardinality = n)"
                            )

                    if self.verbose:
                        print("tileid: {}".format(tileid_used))
                    used.append(index)

                    break
                last_group = group_num

            if self.verbose:
                print("\nCLEAN-UP AFTER FOR LOOP")
                print("-----------------------")
                print(
                    "final number of tiles in tile_group: {}".format(
                        len(tilegroup_json)
                    )
                )
                print("removing used nodes: {}".format(used))
                print("resource_data len before: {}".format(len(resource_data)))
            resource_data = [v for i, v in enumerate(resource_data) if i not in used]
            if self.verbose:
                print("resource_data len after: {}".format(len(resource_data)))

            # append the tile group to self.tiles
            self.tiles += tilegroup_json

        if self.verbose:
            print("\nTOTAL TILES IN RESOURCE: {}".format(len(self.tiles)))
        # final processing, now that self.tiles is fully populated
        self.strip_empty_tile_values()

        # reorder tiles so that the correct name and/or description are first in line
        # and therefore used by the display resource descriptors function.
        # THIS IS NOT CURRENTLY IMPLEMENTED
        # the reason being that the Value uuid for "primary" is RDM-specific, and the
        # Name Type nodeid is resource model-specific. All of the plumbing is not yet
        # in place to pass those uuids to this function at this time.
        if True is False:
            self.reorder_tiles_by_value()

    def get_resource_json(self):
        """returns the full v4 json for this resource. note that self.process()
        must be run before this method is called, otherwise self.tiles will be
        empty."""

        v4_json = self.get_empty_resource()
        v4_json["tiles"] = self.tiles

        return v4_json


class v3Importer:
    """This class is used at the Resource Model-level to support v3 migration.

    It must be instantiated with the v3_data_dir (a structured subdirectory in
    a standard v4 package), the name of the resource model this class will
    represent, and the v3 json export file (though in the future this could be
    inferred from the v3_data_dir, or, better, v3_data_dir should be replaced
    with the rm_configs content itself). An optional truncate argument can be
    used to limit the number of resources that are loaded from the v3 json."""

    def __init__(
        self,
        v3_data_dir,
        v4_graph_name,
        v3_resource_file=None,
        truncate=None,
        exclude=[],
        only=[],
        verbose=False,
        dt_converter=DataValueConverter(),
    ):

        if v3_resource_file is not None and not os.path.isfile(v3_resource_file):
            raise Exception(
                "v3 business data file {} does not exist".format(v3_resource_file)
            )

        self.source_file = v3_resource_file

        self.dt_converter = dt_converter

        self.v4_graph = Graph.objects.get(name=v4_graph_name)
        self.v4_graph_name = v4_graph_name
        self.v4_nodes = Node.objects.filter(graph=self.v4_graph)

        # load the info stored in the rm_configs file
        v3_config = v3utils.get_v3_config_info(v3_data_dir, v4_graph_name)
        self.v3_graph_name = v3_config["v3_entitytypeid"]

        def augment_node_lookup(v3_config):
            """takes the node lookup csv and converts to a dictionary
            with more information added to it for each node."""

            lookup_path = v3_config["v3_v4_node_lookup"]

            new_and_improved = {}
            with open(lookup_path, "r") as openfile:
                reader = csv.DictReader(openfile)

                for row in reader:
                    try:
                        n = self.v4_nodes.get(name=row["v4_node"])
                    except Node.DoesNotExist:
                        raise Exception(
                            "{} in {} lookup csv is not matched "
                            "with a valid v4 node.".format(row["v3_node"], lookup_path)
                        )
                    new_and_improved[row["v3_node"]] = {
                        "v4_name": row["v4_node"],
                        "v4_uuid": str(n.nodeid),
                        "v4_datatype": n.datatype,
                    }

            return new_and_improved

        # create better node_lookup that holds more information
        self.node_lookup = augment_node_lookup(v3_config)

        def get_mergenodes(v3_config):

            mergenodes_dict = {}
            with open(v3_config["v3_nodes_csv"], "r") as openfile:
                reader = csv.DictReader(openfile)
                for row in reader:
                    mergenodes_dict[row["Label"]] = row["mergenode"]
            return list(set(mergenodes_dict.values()))

        # gather mergenode information for all v3 node names.
        self.v3_mergenodes = get_mergenodes(v3_config)

        # these properties have to do with how many/which resources to convert
        self.truncate = truncate
        self.exclude = exclude
        self.only = only

        # set verbose for this entire class, which is passed on to the v3PreparedResource
        self.verbose = verbose

        # finally, do the actual loading of the v3 data into this class
        if v3_resource_file.endswith(".jsonl"):
            self.v3_resources = []
        else:
            self.v3_resources = self.load_v3_data()

    def load_v3_data(self):
        """loads the data that is in the v3 export file. limits to the number
        in truncate, if truncate is not none."""

        with open(self.source_file, "rb") as openfile:
            v3_json = json.loads(openfile.read())

        # get all the resources matching this resource graph name
        v3_resources = [
            r for r in v3_json["resources"] if r["entitytypeid"] == self.v3_graph_name
        ]

        # filter out any empty resources
        v3_resources = [r for r in v3_resources if len(r["child_entities"]) != 0]

        # filter out any that are explicitly excluded
        self.v3_resources = [
            r for r in v3_resources if r["entityid"] not in self.exclude
        ]

        # filter out all but the ones specified in the only argument
        if len(self.only) > 0:
            self.v3_resources = [r for r in self.v3_resources if r["entityid"] in only]

        # if the list should be truncated, only take that many resources from the front of the list
        if self.truncate:
            self.v3_resources = self.v3_resources[: self.truncate]

        return self.v3_resources

    def process_one_resource(self, v3_json):
        """changes a single v3 json resource into a v4 json resource"""

        v3_resource = v3PreparedResource(
            v3_json,
            self.v4_graph.graphid,
            self.node_lookup,
            self.v3_mergenodes,
            verbose=self.verbose,
            dt_converter=self.dt_converter,
        )

        v3_resource.process(self.v4_nodes)
        return v3_resource.get_resource_json()

    def convert_v3_data(self):
        """creates v4 resources from all the loaded v3 resources in
        self.v3_resources. returns these resources."""

        resources = []
        for res in self.v3_resources:

            v4_json = self.process_one_resource(res)
            resources.append(v4_json)

        return resources

    def get_v4_json(self):

        resources = self.convert_v3_data()
        v4_json = {"business_data": {"resources": resources}}

        return v4_json

    def write_v4_json(self, dest_path):

        out_json = self.get_v4_json()
        with open(dest_path, "w") as openfile:
            openfile.write(JSONSerializer().serialize(out_json, indent=4))

        return dest_path

    def write_v4_jsonl(self, dest_path):

        ct = 0
        with open(self.source_file, "rb") as openv3:

            lines = openv3.readlines()
            with open(dest_path, "wb") as openv4:
                for n, line in enumerate(lines):
                    v3_json = json.loads(line)

                    # set of checks that basically mimicks what happens
                    # in the load_v3_data method that is used for JSON.
                    if v3_json["entitytypeid"] != self.v3_graph_name:
                        continue
                    if len(v3_json["child_entities"]) == 0:
                        continue
                    resid = v3_json["entityid"]
                    if self.truncate:
                        if n - 2 == self.truncate:
                            break
                    if len(self.only) > 0:
                        if resid not in self.only:
                            continue
                    if resid in self.exclude:
                        continue

                    v4_json = self.process_one_resource(v3_json)
                    v4_line = JSONSerializer().serialize(v4_json)

                    openv4.write(v4_line + "\n")
                    ct += 1

                    # simple progress printing
                    if ct == 0:
                        print("")
                    if ct % 1000 == 0:
                        print(ct)
                    elif ct % 100 == 0:
                        print(".")
                    if ct == self.truncate:
                        break
                if ct > 0:
                    print("\ntotal resources converted: {}".format(ct))

        if ct == 0:
            os.remove(dest_path)
            return False

        return dest_path


class v3SkosConverter:
    """
    This utility converts an Arches 3 SKOS-formatted scheme file into
    an Arches 4 thesaurus file and collections file for import
    """

    def __init__(
        self,
        skos_file,
        name_space="http://localhost:8000/",
        uuid_lookup={},
        verbose=False,
    ):

        with open(skos_file, "r") as incoming_skos:
            skos = incoming_skos.read()
            skos = skos.replace("http://www.archesproject.org/", name_space)

        self.v3_skos = skos
        self.uuid_lookup = uuid_lookup
        self.verbose = verbose
        self.name_space = name_space

    def new_or_existing_uuid(self, preflabel):
        """
        take a topConcept's prefLabel node, attempt to parse the JSON within,
        return a new or existing UUID for the collection based on
        whether we already have one saved in the collection uuid lookup.
        """

        if preflabel in self.uuid_lookup:
            return self.uuid_lookup[preflabel]
        else:
            new_uuid = str(uuid.uuid4())
            self.uuid_lookup[preflabel] = new_uuid
            return new_uuid

    def add_children_to_collection(
        self, source_graph, out_graph, parent_id, topconcept_id
    ):

        children = [
            i for i in source_graph.triples((topconcept_id, SKOS["narrower"], None))
        ]

        for child in children:
            out_graph.add((ARCHES[parent_id], SKOS["member"], child[2]))
            out_graph.add((child[2], RDF.type, SKOS["Concept"]))
            self.add_children_to_collection(source_graph, out_graph, child[2], child[2])

        return out_graph

    def write_skos(self, directory):

        # parse the original v3 graph
        v3graph = RDFGraph()
        v3graph.parse(data=self.v3_skos)

        # create the namespace manager
        namespaces = (("arches", ARCHES), ("skos", SKOS), ("dcterms", DCTERMS))
        nsmanager = NamespaceManager(RDFGraph())
        for ns in namespaces:
            nsmanager.bind(ns[0], ns[1])

        # create the output graphs with the new namespace manager
        v4thesaurus = RDFGraph(namespace_manager=nsmanager)
        v4collections = RDFGraph(namespace_manager=nsmanager)

        # add the concept schemes to the thesaurus
        concept_schemes = [
            i for i in v3graph.triples((None, RDF.type, SKOS["ConceptScheme"]))
        ]
        for cs in concept_schemes:
            v4thesaurus.add(cs)

        # iterate the concepts and make collections for them.
        topconcepts = [i for i in v3graph.triples((None, SKOS["hasTopConcept"], None))]
        for tc in topconcepts:

            # get the top concept name and if convert it to a Literal object
            tc_name_literal = v3graph.value(subject=tc[2], predicate=SKOS["prefLabel"])

            # get the value from the JSON formatted Literal content
            # if the Literal content is NOT JSON, then this reference data was
            # exported from v3 with the wrong command and will not work.
            try:
                tc_name = json.loads(tc_name_literal.value)["value"]
                collection_id = self.new_or_existing_uuid(tc_name)
            except ValueError:
                docs = "https://arches.readthedocs.io/en/stable/v3-to-v4-migration/"
                print(
                    "ERROR: Incompatible SKOS. See {} for more information.".format(
                        docs
                    )
                )
                exit()

            if self.verbose:
                children = [i for i in v3graph.triples((tc[2], SKOS["narrower"], None))]
                print("{}: {} immediate child concepts".format(tc_name, len(children)))
                print("    collection uuid: " + collection_id)

            # create a new collection for each top concept
            v4thesaurus.add(tc)
            v4collections.add((ARCHES[collection_id], RDF.type, SKOS["Collection"]))

            # add the preflabel for the collection, if it's not the r2r types collection
            # which already has a label in Arches by default.
            if tc_name != "Resource To Resource Relationship Types":
                simple_tc_name = Literal(tc_name, lang="en-US")
                v4collections.add(
                    (ARCHES[collection_id], SKOS["prefLabel"], simple_tc_name)
                )

            # recursively add all of the concept children to the collection for this
            # top concept.
            v4collections = self.add_children_to_collection(
                v3graph, v4collections, collection_id, tc[2]
            )

        # add ALL concepts from the v3 graph to the thesaurus. this pulls along all
        # child/parent relationships into the thesaurus, as well as all extra info
        # for each concept, like sortorder, prefLabel, etc.
        for concept in v3graph.triples((None, RDF.type, SKOS["Concept"])):
            v4thesaurus.add(concept)

            # this is the extra info related to each concept, like prefLabel, sortorder, etc.
            for s, p, o in v3graph.triples((concept[0], None, None)):
                # skip the label of the resource to resource relationship type concept
                # as it's already in Arches and this would duplicate it.
                if s.endswith("000004") and p == SKOS["prefLabel"]:
                    continue
                v4thesaurus.add((s, p, o))

        # export the thesaurus and collections to predetermined locations within the
        # package file structure.
        thesaurus_file = os.path.join(directory, "concepts", "thesaurus.xml")
        if self.verbose:
            print("writing thesaurus to: " + thesaurus_file)
        v4thesaurus.serialize(destination=thesaurus_file, format="pretty-xml")

        collections_file = os.path.join(directory, "collections", "collections.xml")
        if self.verbose:
            print("writing collections to: " + collections_file)
        v4collections.serialize(destination=collections_file, format="pretty-xml")

    def write_uuid_lookup(self, filepath):

        with open(filepath, "w") as uuid_store:
            uuid_store.write(json.dumps(self.uuid_lookup, indent=4, sort_keys=True))
            uuid_store.close()
