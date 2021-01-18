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
import datetime
import logging
from io import StringIO
from io import BytesIO
from django.core.files import File
from django.utils.translation import ugettext as _
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.flatten_dict import flatten_dict
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.exporter import ResourceExporter
from arches.app.utils.geo_utils import GeoUtils
import arches.app.utils.zip as zip_utils
from arches.app.views import search as SearchView

logger = logging.getLogger(__name__)


class SearchResultsExporter(object):
    def __init__(self, search_request=None):
        if search_request is None:
            raise Exception("Need to pass in a search request")
        search_request.GET = search_request.GET.copy()
        search_request.GET["tiles"] = True
        search_request.GET["export"] = True
        self.format = search_request.GET.get("format", "tilecsv")
        self.compact = search_request.GET.get("compact", True)
        self.precision = int(search_request.GET.get("precision", 5))
        if self.format == "shp" and self.compact is not True:
            raise Exception("Results must be compact to export to shapefile")
        self.search_request = search_request
        self.datatype_factory = DataTypeFactory()
        self.node_lookup = {}
        self.output = {}
        self.set_precision = GeoUtils().set_precision

    def export(self, format):
        ret = []
        search_res_json = SearchView.search_results(self.search_request)
        if search_res_json.status_code == 500:
            return ret
        results = JSONDeserializer().deserialize(search_res_json.content)
        instances = results["results"]["hits"]["hits"]
        output = {}

        for resource_instance in instances:
            use_fieldname = self.format in ("shp",)
            resource_obj = self.flatten_tiles(
                resource_instance["_source"]["tiles"], self.datatype_factory, compact=self.compact, use_fieldname=use_fieldname
            )
            has_geom = resource_obj.pop("has_geometry")
            skip_resource = self.format in ("shp",) and has_geom is False
            if skip_resource is False:
                try:
                    output[resource_instance["_source"]["graph_id"]]["output"].append(resource_obj)
                except KeyError as e:
                    output[resource_instance["_source"]["graph_id"]] = {"output": []}
                    output[resource_instance["_source"]["graph_id"]]["output"].append(resource_obj)

        for graph_id, resources in output.items():
            graph = models.GraphModel.objects.get(pk=graph_id)
            if format == "tilecsv":
                headers = list(graph.node_set.filter(exportable=True).values_list("name", flat=True))
                headers.append("resourceid")
                ret.append(self.to_csv(resources["output"], headers=headers, name=graph.name))
            if format == "shp":
                headers = graph.node_set.filter(exportable=True).values("fieldname", "datatype", "name")[::1]
                missing_field_names = []
                for header in headers:
                    if not header["fieldname"]:
                        missing_field_names.append(header["name"])
                    header.pop("name")
                if len(missing_field_names) > 0:
                    message = _("Shapefile are fieldnames required for the following nodes: {0}".format(", ".join(missing_field_names)))
                    logger.error(message)
                    raise (Exception(message))

                headers = graph.node_set.filter(exportable=True).values("fieldname", "datatype")[::1]
                headers.append({"fieldname": "resourceid", "datatype": "str"})
                ret += self.to_shp(resources["output"], headers=headers, name=graph.name)

        full_path = self.search_request.get_full_path()
        search_request_path = self.search_request.path if full_path is None else full_path
        search_export_info = models.SearchExportHistory(
            user=self.search_request.user, numberofinstances=len(instances), url=search_request_path
        )
        search_export_info.save()

        return ret, search_export_info

    def write_export_zipfile(self, files_for_export, export_info):
        """
        Writes a list of file like objects out to a zip file
        """
        zip_stream = zip_utils.create_zip_file(files_for_export, "outputfile")
        today = datetime.datetime.now().isoformat()
        name = f"{settings.APP_NAME}_{today}.zip"
        search_history_obj = models.SearchExportHistory.objects.get(pk=export_info.searchexportid)
        f = BytesIO(zip_stream)
        download = File(f)
        search_history_obj.downloadfile.save(name, download)
        return search_history_obj.searchexportid

    def get_node(self, nodeid):
        nodeid = str(nodeid)
        try:
            return self.node_lookup[nodeid]
        except KeyError as e:
            self.node_lookup[nodeid] = models.Node.objects.get(pk=nodeid)
            return self.node_lookup[nodeid]

    def get_feature_collections(self, tile, node, feature_collections, fieldname, datatype):
        node_value = tile["data"][str(node.nodeid)]
        for feature_index, feature in enumerate(node_value["features"]):
            feature["geometry"]["coordinates"] = self.set_precision(feature["geometry"]["coordinates"], self.precision)
            try:
                feature_collections[fieldname]["features"].append(feature)
            except KeyError:
                feature_collections[fieldname] = {"datatype": datatype, "features": [feature]}
        return feature_collections

    def create_resource_json(self, tiles):
        resource_json = {}
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
                if tile["cardinality"] == "n":
                    try:
                        resource_json[tile["card_name"]].append(tile[tile["card_name"]])
                    except KeyError:
                        resource_json[tile["card_name"]] = [tile[tile["card_name"]]]
                else:
                    resource_json[tile["card_name"]] = tile[tile["card_name"]]
        return resource_json

    def flatten_tiles(self, tiles, datatype_factory, compact=True, use_fieldname=False):
        feature_collections = {}
        compacted_data = {}
        lookup = {}
        has_geometry = False

        for tile in tiles:  # normalize tile.data to use labels instead of node ids
            compacted_data["resourceid"] = tile["resourceinstance_id"]
            for nodeid, value in tile["data"].items():
                node = self.get_node(nodeid)
                if node.exportable:
                    datatype = datatype_factory.get_instance(node.datatype)
                    node_value = datatype.get_display_value(tile, node)
                    label = node.fieldname if use_fieldname is True else node.name

                    if compact:
                        if node.datatype == "geojson-feature-collection" and node_value:
                            has_geometry = True
                            feature_collections = self.get_feature_collections(tile, node, feature_collections, label, datatype)
                        else:
                            try:
                                compacted_data[label] += ", " + str(node_value)
                            except KeyError:
                                compacted_data[label] = str(node_value)
                    else:
                        data[label] = str(node_value)

            if not compact:  # add on the cardinality and card_names to the tile for use later on
                tile["data"] = data
                card = models.CardModel.objects.get(nodegroup=tile["nodegroup_id"])
                tile["card_name"] = card.name
                tile["cardinality"] = node.nodegroup.cardinality
                tile[card.name] = tile["data"]
                lookup[tile["tileid"]] = tile

        if compact:
            for key, value in feature_collections.items():
                compacted_data[key] = value["datatype"].transform_export_values(value)
            compacted_data["has_geometry"] = has_geometry
            return compacted_data

        resource_json = self.create_resource_json(tiles)
        return flatten_dict(resource_json)

    def to_csv(self, instances, headers, name):
        dest = StringIO()
        csvwriter = csv.DictWriter(dest, delimiter=",", fieldnames=headers)
        csvwriter.writeheader()
        for instance in instances:
            csvwriter.writerow({k: str(v) for k, v in list(instance.items())})
        return {"name": f"{name}.csv", "outputfile": dest}

    def to_shp(self, instances, headers, name):
        shape_exporter = ResourceExporter(format="shp")
        dest = shape_exporter.writer.create_shapefiles(instances, headers, name)
        return dest
