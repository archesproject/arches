import os
import json
from arches.app.models.tile import Tile


def get_v3_config_info(v3_data_dir, v4_graph_name=None):

    conf_file = os.path.join(v3_data_dir, "rm_configs.json")
    with open(conf_file, 'rb') as openfile:
        v3_config = json.loads(openfile.read())

    # prepend the full paths to the lookup files
    for k, conf in v3_config.iteritems():

        conf["v3_nodes_csv"] = os.path.join(v3_data_dir, "graph_data",
                                            conf["v3_nodes_csv"])
        conf["v3_v4_node_lookup"] = os.path.join(v3_data_dir, "graph_data",
                                                 conf["v3_v4_node_lookup"])

    # return the augmented v3 configs
    if v4_graph_name:
        return v3_config[v4_graph_name]
    else:
        return v3_config


def test_rm_configs(v3_data_dir):

    configs = get_v3_config_info(v3_data_dir)
    v4_rm_dir = os.path.join(
        os.path.dirname(v3_data_dir), "graphs", "resource_models"
    )
    errors = []
    for rm, conf in configs.iteritems():
        print rm
        graph_file_path = os.path.join(v4_rm_dir, rm+".json")
        if not os.path.isfile(graph_file_path):
            errors.append("Missing graph json: "+graph_file_path)
        for k, v in conf.iteritems():
            if k == "v3_entitytypeid":
                continue
            if not os.path.isfile(v):
                errors.append("File does not exist: "+v)

    return errors


def count_tiles_and_values(resource_instance_id):

    ret = {'values': [], 'tile_ct': 0}

    tiles = Tile.objects.filter(resourceinstance_id=resource_instance_id)

    ret['tile_ct'] = len(tiles)

    value_ct = 0
    for tile in tiles:
        for k, v in tile.data.iteritems():
            if not v:
                continue
            if isinstance(v, list):
                value_ct += len(v)
                for i in v:
                    ret['values'].append(i)
            # assume that a dict value is a geojson object
            # further, each feature must be counted independently, because
            # that will match the count in the original v3 json data
            elif isinstance(v, dict):
                for feat in v['features']:
                    ret['values'].append(feat)
            else:
                ret['values'].append(v)

    return ret


def get_v4_json_value_ct(v4_json):

    ct = 0
    for tile in v4_json['tiles']:
        ct += len(tile['data'])

    return ct
