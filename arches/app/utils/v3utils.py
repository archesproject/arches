import os
import json
import uuid
from arches.app.models.tile import Tile


def get_nodegroup_tilegroup(v4_node_name, nodes, resource_id, verbose=False):

    # get the corresponding v4 node and then get the tile for its nodegroup
    v4_node = nodes.get(name=v4_node_name)
    ng_tile = Tile().get_blank_tile(v4_node.nodegroup_id, resourceid=resource_id)

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


def duplicate_tile_json(tilejson):
    """returns a duplicate of the tilejson that is passed in, but
    with all data values set to None."""

    newtile = {
        "resourceinstance_id": tilejson["resourceinstance_id"],
        "provisionaledits": tilejson["provisionaledits"],
        "parenttile_id": tilejson["parenttile_id"],
        "nodegroup_id": tilejson["nodegroup_id"],
        "sortorder": tilejson["sortorder"],
        "data": {},
        "tileid": uuid.uuid4(),
    }
    for k in list(tilejson["data"].keys()):
        newtile["data"][k] = None

    return newtile


def set_tile_data(tile, v4_uuid, datatype, value):

    if datatype == "concept-list":
        if tile["data"][v4_uuid] is None:
            tile["data"][v4_uuid] = [value]
        else:
            tile["data"][v4_uuid].append(value)
    else:
        tile["data"][v4_uuid] = value
    return tile


def get_v3_config_info(v3_data_dir, v4_graph_name=None):

    conf_file = os.path.join(v3_data_dir, "rm_configs.json")
    with open(conf_file, "rb") as openfile:
        v3_config = json.loads(openfile.read())

    # prepend the full paths to the lookup files
    for k, conf in v3_config.items():

        conf["v3_nodes_csv"] = os.path.join(v3_data_dir, "graph_data", conf["v3_nodes_csv"])
        conf["v3_v4_node_lookup"] = os.path.join(v3_data_dir, "graph_data", conf["v3_v4_node_lookup"])

    # return the augmented v3 configs
    if v4_graph_name:
        return v3_config[v4_graph_name]
    else:
        return v3_config


def test_rm_configs(v3_data_dir):

    configs = get_v3_config_info(v3_data_dir)
    v4_rm_dir = os.path.join(os.path.dirname(v3_data_dir), "graphs", "resource_models")
    errors = []

    for rm, conf in configs.items():
        print(rm)
        graph_file_path = os.path.join(v4_rm_dir, rm + ".json")
        if not os.path.isfile(graph_file_path):
            errors.append("Missing graph json: " + graph_file_path)
        for k, v in conf.items():
            if k == "v3_entitytypeid":
                continue
            if not os.path.isfile(v):
                errors.append("File does not exist: " + v)

    return errors


def count_tiles_and_values(resource_instance_id):

    ret = {"values": [], "tile_ct": 0}

    tiles = Tile.objects.filter(resourceinstance_id=resource_instance_id)

    ret["tile_ct"] = len(tiles)

    value_ct = 0
    for tile in tiles:
        for k, v in tile.data.items():
            if not v:
                continue
            if isinstance(v, list):
                value_ct += len(v)
                for i in v:
                    ret["values"].append(i)
            # assume that a dict value is a geojson object
            # further, each feature must be counted independently, because
            # that will match the count in the original v3 json data
            elif isinstance(v, dict):
                for feat in v["features"]:
                    ret["values"].append(feat)
            else:
                ret["values"].append(v)

    return ret


def get_v4_json_value_ct(v4_json):

    ct = 0
    for tile in v4_json["tiles"]:
        ct += len(tile["data"])

    return ct
