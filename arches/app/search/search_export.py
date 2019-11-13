'''
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''


from arches.app.models import models
from arches.app.utils.flatten_dict import flatten_dict


def flatten_tiles(tiles, datatype_factory, compact=True):
    compacted_data = {}

    # first let's normalize tile.data to use labels instead of node ids
    # we'll also add on the cardinality and card_names to the tile for use later on

    lookup = {}
    feature_collections = {}
    for tile in tiles:
        data = {}
        for nodeid, value in tile['data'].items():
            node = models.Node.objects.get(pk=nodeid)
            if node.exportable:
                datatype = datatype_factory.get_instance(node.datatype)
                #node_value = datatype.transform_export_values(tile['data'][str(node.nodeid)])
                node_value = datatype.get_display_value(tile, node)
                label = node.fieldname

                if compact:
                    if node.datatype == 'geojson-feature-collection':
                        node_value = tile['data'][str(node.nodeid)]
                        for feature_index, feature in enumerate(node_value['features']):
                            try:
                                feature_collections[label]['features'].append(feature)
                            except:
                                feature_collections[label] = {'datatype': datatype, 'features': [feature]}
                    else:
                        try:
                            compacted_data[label] += ", " + str(node_value)
                        except:
                            compacted_data[label] = str(node_value)
                else:
                    data[label] = str(node_value)

        if not compact:
            tile['data'] = data
            card = models.CardModel.objects.get(nodegroup=tile['nodegroup_id'])
            tile['card_name'] = card.name
            tile['cardinality'] = node.nodegroup.cardinality
            tile[card.name] = tile['data']
            lookup[tile['tileid']] = tile

    if compact:
        for key, value in feature_collections.items():
            compacted_data[key] = value['datatype'].transform_export_values(value)
        return compacted_data

    # print(JSONSerializer().serialize(tiles, indent=4))

    resource_json = {}
    # ret = []
    # aggregate tiles into single resource instance objects rolling up tile data in the process
    # print out "ret" to understand the intermediate structure
    for tile in tiles:
        if tile['parenttile_id'] is not None:
            parentTile = lookup[str(tile['parenttile_id'])]
            if tile['cardinality'] == 'n':
                try:
                    parentTile[parentTile['card_name']][tile['card_name']].append(tile[tile['card_name']])
                except KeyError:
                    parentTile[parentTile['card_name']][tile['card_name']] = [tile[tile['card_name']]]
            else:
                parentTile[parentTile['card_name']][tile['card_name']] = tile[tile['card_name']]
        else:
            # print the following out to understand the intermediate structure
            # ret.append(tile)
            # ret.append({tile['card_name']: tile[tile['card_name']]})
            if tile['cardinality'] == 'n':
                try:
                    resource_json[tile['card_name']].append(tile[tile['card_name']])
                except KeyError:
                    resource_json[tile['card_name']] = [tile[tile['card_name']]]
            else:
                resource_json[tile['card_name']] = tile[tile['card_name']]

    return flatten_dict(resource_json)
