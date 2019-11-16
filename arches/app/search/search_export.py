"""
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
"""

import csv
from io import StringIO
from arches.app.models import models
from arches.app.utils.flatten_dict import flatten_dict
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.geo_utils import GeoUtils
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


class SearchResultsExporter(object):
    def __init__(self, search_request=None):
        if search_request is None:
            raise Exception("Need to pass in a search request")
        search_request.GET = search_request.GET.copy()
        search_request.GET["tiles"] = True
        search_request.GET["export"] = True

        self.compact = search_request.GET.get("compact", True)
        self.precision = int(search_request.GET.get("precision", 5))
        self.search_request = search_request
        self.datatype_factory = DataTypeFactory()
        self.node_lookup = {}
        self.output = {}
        self.set_precision = GeoUtils().set_precision

    def export(self):
        from arches.app.views.search import search_results

        search_res_json = search_results(self.search_request)
        results = JSONDeserializer().deserialize(search_res_json.content)
        instances = results["results"]["hits"]["hits"]
        output = {}
        ret = []

        for resource_instance in instances:
            resource_obj = self.flatten_tiles(resource_instance["_source"]["tiles"], self.datatype_factory, compact=self.compact)
            try:
                output[resource_instance["_source"]["graph_id"]]["output"].append(resource_obj)
            except KeyError as e:
                output[resource_instance["_source"]["graph_id"]] = {"output": []}
                output[resource_instance["_source"]["graph_id"]]["output"].append(resource_obj)

        for graph_id, resources in output.items():
            graph = models.GraphModel.objects.get(pk=graph_id)
            headers = list(graph.node_set.filter(exportable=True).values_list("fieldname", flat=True))
            ret.append(self.to_csv(resources["output"], headers=headers, name=graph.name))
            # output[graph_id]['csv'] = self.to_csv(resources['output'])
        return ret

    def get_node(self, nodeid):
        nodeid = str(nodeid)
        try:
            return self.node_lookup[nodeid]
        except:
            self.node_lookup[nodeid] = models.Node.objects.get(pk=nodeid)
            return self.node_lookup[nodeid]

    def flatten_tiles(self, tiles, datatype_factory, compact=True):
        compacted_data = {}
        lookup = {}
        feature_collections = {}

        # first let's normalize tile.data to use labels instead of node ids
        for tile in tiles:
            data = {}
            for nodeid, value in tile["data"].items():
                node = self.get_node(nodeid)
                if node.exportable:
                    datatype = datatype_factory.get_instance(node.datatype)
                    # node_value = datatype.transform_export_values(tile['data'][str(node.nodeid)])
                    node_value = datatype.get_display_value(tile, node)
                    label = node.fieldname

                    if compact:
                        if node.datatype == "geojson-feature-collection":
                            node_value = tile["data"][str(node.nodeid)]
                            for feature_index, feature in enumerate(node_value["features"]):
                                feature["geometry"]["coordinates"] = self.set_precision(feature["geometry"]["coordinates"], self.precision)
                                try:
                                    feature_collections[label]["features"].append(feature)
                                except:
                                    feature_collections[label] = {"datatype": datatype, "features": [feature]}
                        else:
                            try:
                                compacted_data[label] += ", " + str(node_value)
                            except:
                                compacted_data[label] = str(node_value)
                    else:
                        data[label] = str(node_value)

            if not compact:
                # add on the cardinality and card_names to the tile for use later on
                tile["data"] = data
                card = models.CardModel.objects.get(nodegroup=tile["nodegroup_id"])
                tile["card_name"] = card.name
                tile["cardinality"] = node.nodegroup.cardinality
                tile[card.name] = tile["data"]
                lookup[tile["tileid"]] = tile

        if compact:
            for key, value in feature_collections.items():
                compacted_data[key] = value["datatype"].transform_export_values(value)
            return compacted_data

        # print(JSONSerializer().serialize(tiles, indent=4))

        resource_json = {}
        # ret = []
        # aggregate tiles into single resource instance objects rolling up tile data in the process
        # print out "ret" to understand the intermediate structure
        for tile in tiles:
            if tile["parenttile_id"] is not None:
                parentTile = lookup[str(tile["parenttile_id"])]
                if tile["cardinality"] == "n":
                    try:
                        parentTile[parentTile["card_name"]][tile["card_name"]].append(tile[tile["card_name"]])
                    except KeyError:
                        parentTile[parentTile["card_name"]][tile["card_name"]] = [tile[tile["card_name"]]]
                else:
                    parentTile[parentTile["card_name"]][tile["card_name"]] = tile[tile["card_name"]]
            else:
                # print the following out to understand the intermediate structure
                # ret.append(tile)
                # ret.append({tile['card_name']: tile[tile['card_name']]})
                if tile["cardinality"] == "n":
                    try:
                        resource_json[tile["card_name"]].append(tile[tile["card_name"]])
                    except KeyError:
                        resource_json[tile["card_name"]] = [tile[tile["card_name"]]]
                else:
                    resource_json[tile["card_name"]] = tile[tile["card_name"]]

        return flatten_dict(resource_json)

    def to_csv(self, instances, headers, name):
        dest = StringIO()
        csvwriter = csv.DictWriter(dest, delimiter=",", fieldnames=headers)
        csvwriter.writeheader()
        # csvs_for_export.append({"name": csv_name, "outputfile": dest})
        print(f"{name} = {len(instances)}")
        for instance in instances:
            csvwriter.writerow({k: str(v) for k, v in list(instance.items())})
        return {"name": f"{name}.csv", "outputfile": dest}

