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

import os
import csv
import datetime
import logging
from io import StringIO
from io import BytesIO
import re
from django.contrib.gis.geos import GeometryCollection, GEOSGeometry
from django.core.files import File
from django.core.files.storage import default_storage
from django.utils.translation import gettext as _
from django.urls import reverse, resolve, get_script_prefix
from arches.app.models import models
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.flatten_dict import flatten_dict
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resources.exporter import ResourceExporter
from arches.app.utils.geo_utils import GeoUtils
from arches.app.utils.string_utils import get_str_kwarg_as_bool
import arches.app.utils.zip as zip_utils
from arches.app.models.system_settings import settings

logger = logging.getLogger(__name__)


class SearchResultsExporter(object):
    def __init__(self, search_request=None):
        if search_request is None:
            raise Exception("Need to pass in a search request")
        search_request.GET = search_request.GET.copy()
        search_request.GET["tiles"] = True
        search_request.GET["export"] = True
        self.report_link = search_request.GET.get("reportlink", False)
        self.format = search_request.GET.get("format", "tilecsv")
        self.export_system_values = get_str_kwarg_as_bool(
            "exportsystemvalues", search_request.GET
        )
        self.compact = search_request.GET.get("compact", True)
        self.precision = int(search_request.GET.get("precision", 5))
        if self.format == "shp" and self.compact is not True:
            raise Exception("Results must be compact to export to shapefile")
        self.search_request = search_request
        self.datatype_factory = DataTypeFactory()
        self.node_lookup = {}
        self.output = {}
        self.set_precision = GeoUtils().set_precision

    def insert_subcard_below_parent_card(
        self, main_card_list, sub_card_list, subcards_added
    ):
        for main_card in main_card_list:
            sub_cards_to_add = []
            for sub_card in sub_card_list:
                if main_card.nodegroup_id == sub_card.nodegroup.parentnodegroup_id:
                    if sub_card not in main_card_list:
                        sub_cards_to_add.append(sub_card)
                        subcards_added = True
            index_number = main_card_list.index(main_card) + 1
            main_card_list[index_number:index_number] = sub_cards_to_add
        return subcards_added

    def return_ordered_header(self, graphid, export_type):

        subcard_list_with_sort = []
        all_cards = models.CardModel.objects.filter(graph=graphid).prefetch_related(
            "nodegroup"
        )
        all_card_list_with_sort = list(
            all_cards.exclude(sortorder=None).order_by("sortorder")
        )
        card_list_no_sort = list(all_cards.filter(sortorder=None))
        sorted_card_list = []

        # Work out which cards with sort order are sub cards by looking at the
        # related nodegroup's parent nodegroup value

        for card_with_sortorder in all_card_list_with_sort:
            if card_with_sortorder.nodegroup.parentnodegroup_id is None:
                sorted_card_list.append(card_with_sortorder)
            else:
                subcard_list_with_sort.append(card_with_sortorder)

        # Reverse set to allow cards with sort and a parent nodegroup
        # to be injected into the main list in the correct order i.e. above
        # cards with no sort order and according to the sort order as cards are
        # injected just below the top card.

        subcard_list_with_sort.sort(key=lambda x: x.sortorder, reverse=True)

        def order_cards(subcards_added=True):
            if subcards_added == True:
                subcards_added = False
                unsorted_subcards_added = self.insert_subcard_below_parent_card(
                    sorted_card_list, card_list_no_sort, subcards_added
                )
                sorted_subcards_added = self.insert_subcard_below_parent_card(
                    sorted_card_list, subcard_list_with_sort, unsorted_subcards_added
                )
                order_cards(sorted_subcards_added)

        order_cards()

        # Create a list of nodes within each card and order them according to sort
        # order then add them to the main list of

        ordered_list_all_nodes = []
        for sorted_card in sorted_card_list:
            card_node_objects = list(
                models.CardXNodeXWidget.objects.filter(
                    card_id=sorted_card.cardid
                ).prefetch_related("node")
            )
            if len(card_node_objects) > 0:
                nodes_in_card = []
                for card_node_object in card_node_objects:
                    if card_node_object.node.datatype != "semantic":
                        nodes_in_card.append(card_node_object)
                node_object_list_sorted = sorted(
                    nodes_in_card, key=lambda x: x.sortorder
                )
                for sorted_node_object in node_object_list_sorted:
                    ordered_list_all_nodes.append(sorted_node_object)

        # Build the list of headers (in correct format for return file format) to be returned
        # from the ordered list of nodes, only where the exportable tag is true

        headers = []
        node_id_list = []
        for ordered_node in ordered_list_all_nodes:
            node_object = ordered_node.node
            if node_object.exportable is True:
                if export_type == "csv":
                    if node_object.nodeid not in node_id_list:
                        headers.append(node_object.name)
                        node_id_list.append(node_object.nodeid)

                elif export_type == "shp":
                    header_object = {}
                    header_object["fieldname"] = node_object.fieldname
                    header_object["datatype"] = node_object.datatype
                    header_object["name"] = node_object.name
                    if node_object.nodeid not in node_id_list:
                        headers.append(header_object)
                        node_id_list.append(node_object.nodeid)

        return headers

    def export(self, format, report_link):
        ret = []
        search_results_path = reverse("search_results")
        if search_results_path.startswith(get_script_prefix()):
            search_results_path = search_results_path.replace(get_script_prefix(), "/")
        func, args, kwargs = resolve(search_results_path)
        kwargs["request"] = self.search_request
        search_res_json = func(*args, **kwargs)
        if search_res_json.status_code == 500:
            return ret
        results = JSONDeserializer().deserialize(search_res_json.content)
        instances = results["results"]["hits"]["hits"]
        output = {}

        for resource_instance in instances:
            use_fieldname = self.format in ("shp",)
            resource_obj = self.flatten_tiles(
                resource_instance["_source"]["tiles"],
                self.datatype_factory,
                compact=self.compact,
                use_fieldname=use_fieldname,
            )
            has_geom = resource_obj.pop("has_geometry")
            skip_resource = self.format in ("shp",) and has_geom is False
            if skip_resource is False:
                try:
                    output[resource_instance["_source"]["graph_id"]]["output"].append(
                        resource_obj
                    )
                except KeyError as e:
                    output[resource_instance["_source"]["graph_id"]] = {"output": []}
                    output[resource_instance["_source"]["graph_id"]]["output"].append(
                        resource_obj
                    )

        for graph_id, resources in output.items():
            graph = models.GraphModel.objects.get(pk=graph_id)

            if (report_link == "true") and (format != "tilexl"):
                for resource in resources["output"]:
                    report_url = reverse(
                        "resource_report", kwargs={"resourceid": resource["resourceid"]}
                    )
                    export_namespace = settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT.rstrip(
                        "/"
                    )
                    resource["Link"] = f"{export_namespace}{report_url}"

            if format == "geojson":

                if settings.EXPORT_DATA_FIELDS_IN_CARD_ORDER is True:
                    headers = self.return_ordered_header(graph_id, "csv")
                else:
                    headers = list(
                        graph.node_set.filter(exportable=True).values_list(
                            "name", flat=True
                        )
                    )

                if (report_link == "true") and ("Link" not in headers):
                    headers.append("Link")
                ret = self.to_geojson(
                    resources["output"], headers=headers, name=graph.name
                )
                return ret, ""

            if format == "tilecsv":

                if settings.EXPORT_DATA_FIELDS_IN_CARD_ORDER is True:
                    headers = self.return_ordered_header(graph_id, "csv")
                else:
                    headers = list(
                        graph.node_set.filter(exportable=True).values_list(
                            "name", flat=True
                        )
                    )

                headers.append("resourceid")
                if (report_link == "true") and ("Link" not in headers):
                    headers.append("Link")
                ret.append(
                    self.to_csv(resources["output"], headers=headers, name=graph.name)
                )

            if format == "shp":

                if settings.EXPORT_DATA_FIELDS_IN_CARD_ORDER is True:
                    headers = self.return_ordered_header(graph_id, "shp")
                else:
                    headers = graph.node_set.filter(exportable=True).values(
                        "fieldname", "datatype", "name"
                    )[::1]

                headers.append({"fieldname": "resourceid", "datatype": "str"})

                missing_field_names = []
                for header in headers:
                    if not header["fieldname"]:
                        missing_field_names.append(header["name"])
                        header.pop("name")
                if len(missing_field_names) > 0:
                    message = _(
                        "Shapefile are fieldnames required for the following nodes: {0}".format(
                            ", ".join(missing_field_names)
                        )
                    )
                    logger.error(message)
                    raise (Exception(message))

                if (report_link == "true") and (
                    {"fieldname": "Link", "datatype": "str"} not in headers
                ):
                    headers.append({"fieldname": "Link", "datatype": "str"})
                else:
                    pass
                ret += self.to_shp(
                    resources["output"], headers=headers, name=graph.name
                )

            if format == "tilexl":
                headers = graph.node_set.filter(exportable=True).values(
                    "fieldname", "datatype", "name"
                )[::1]
                headers = graph.node_set.filter(exportable=True).values(
                    "fieldname", "datatype"
                )[::1]
                headers.append({"fieldname": "resourceid", "datatype": "str"})
                ret += self.to_tilexl(resources["output"])

            if format == "html":
                ret += self.to_html(
                    resources["output"], name=graph.name, graph_id=str(graph.pk)
                )

        full_path = self.search_request.get_full_path()
        search_request_path = (
            self.search_request.path if full_path is None else full_path
        )
        search_export_info = models.SearchExportHistory(
            user=self.search_request.user,
            numberofinstances=len(instances),
            url=search_request_path,
        )
        search_export_info.save()

        return ret, search_export_info

    def write_export_zipfile(self, files_for_export, export_info, export_name=None):
        """
        Writes a list of file like objects out to a zip file
        """
        zip_stream = zip_utils.create_zip_file(files_for_export, "outputfile")
        today = datetime.datetime.now().isoformat()
        name = (
            f"{export_name}.zip"
            if (export_name is not None and export_name != "Arches Export")
            else f"{settings.APP_NAME}_{today}.zip"
        )
        search_history_obj = models.SearchExportHistory.objects.get(
            pk=export_info.searchexportid
        )
        search_history_obj.downloadfile.name = name
        f = BytesIO(zip_stream)
        download = File(f)
        storage = default_storage
        storage.save(search_history_obj.downloadfile.name, download)
        search_history_obj.save()
        return search_history_obj.searchexportid

    def get_node(self, nodeid):
        nodeid = str(nodeid)
        try:
            return self.node_lookup[nodeid]
        except KeyError as e:
            self.node_lookup[nodeid] = models.Node.objects.get(pk=nodeid)
            return self.node_lookup[nodeid]

    def get_feature_collections(
        self, tile, node, feature_collections, fieldname, datatype
    ):
        node_value = tile["data"][str(node.nodeid)]
        try:
            for feature_index, feature in enumerate(node_value["features"]):
                feature["geometry"]["coordinates"] = self.set_precision(
                    feature["geometry"]["coordinates"], self.precision
                )
                try:
                    feature_collections[fieldname]["features"].append(feature)
                except KeyError:
                    feature_collections[fieldname] = {
                        "datatype": datatype,
                        "features": [feature],
                    }
        except TypeError as e:
            pass
        return feature_collections

    def create_resource_json(self, tiles):
        resource_json = {}
        for tile in tiles:
            if tile["parenttile_id"] is not None:
                parentTile = lookup[str(tile["parenttile_id"])]
                if tile["cardinality"] == "n":
                    try:
                        parentTile[parentTile["card_name"]][tile["card_name"]].append(
                            tile[tile["card_name"]]
                        )
                    except KeyError:
                        parentTile[parentTile["card_name"]][tile["card_name"]] = [
                            tile[tile["card_name"]]
                        ]
                else:
                    parentTile[parentTile["card_name"]][tile["card_name"]] = tile[
                        tile["card_name"]
                    ]
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
                    if self.export_system_values:
                        node_value = datatype.transform_export_values(
                            value, **{"concept_export_value_type": "id"}
                        )
                    else:
                        node_value = datatype.get_display_value(tile, node)
                    label = node.fieldname if use_fieldname is True else node.name

                    if compact:
                        if node.datatype == "geojson-feature-collection" and node_value:
                            has_geometry = True
                            feature_collections = self.get_feature_collections(
                                tile, node, feature_collections, label, datatype
                            )
                        else:
                            try:
                                compacted_data[label] += ", " + str(node_value)
                            except KeyError:
                                compacted_data[label] = str(node_value)
                    else:
                        data[label] = str(node_value)

            if (
                not compact
            ):  # add on the cardinality and card_names to the tile for use later on
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
            csvwriter.writerow(
                {k: sanitize_csv_value(str(v)) for k, v in list(instance.items())}
            )
        return {"name": f"{name}.csv", "outputfile": dest}

    def to_shp(self, instances, headers, name):
        shape_exporter = ResourceExporter(format="shp")
        dest = shape_exporter.writer.create_shapefiles(instances, headers, name)
        return dest

    def to_tilexl(self, instances):
        resourceinstanceids = [
            instance["resourceid"] for instance in instances if "resourceid" in instance
        ]
        tilexl_exporter = ResourceExporter(format="tilexl")
        dest = tilexl_exporter.export(
            resourceinstanceids=resourceinstanceids, user=self.search_request.user
        )
        return dest

    def to_html(self, instances, name, graph_id):
        resourceinstanceids = [
            instance["resourceid"] for instance in instances if "resourceid" in instance
        ]
        html_exporter = ResourceExporter(format="html")
        dest = html_exporter.export(resourceinstanceids=resourceinstanceids)
        return dest

    def get_geometry_fieldnames(
        self, instance
    ):  # the same function exist in shapefile.py l.70
        geometry_fields = []
        for k, v in instance.items():
            if isinstance(v, GeometryCollection):
                geometry_fields.append(k)
        return geometry_fields

    def to_geojson(
        self, instances, headers, name
    ):  # a part of the code exists in datatypes.py, l.567
        if len(instances) > 0:
            geometry_fields = []
            for instance in instances:
                geometry_fields_in_instance = self.get_geometry_fieldnames(instance)
                for geometry_field_value in geometry_fields_in_instance:
                    if geometry_field_value not in geometry_fields:
                        geometry_fields.append(geometry_field_value)

        features = []
        for geometry_field in geometry_fields:
            for instance in instances:
                properties = {}
                for header in headers:
                    if header != geometry_field:
                        try:
                            properties[header] = instance[header]
                        except KeyError:
                            properties[header] = None
                for key, value in instance.items():
                    if key == geometry_field:
                        if isinstance(value, GeometryCollection):
                            geometry = GEOSGeometry(value, srid=4326)
                            for geom in geometry:
                                feature = {}
                                feature["geometry"] = JSONDeserializer().deserialize(
                                    GEOSGeometry(geom, srid=4326).json
                                )
                                feature["type"] = "Feature"
                                feature["properties"] = properties
                                features.append(feature)

        feature_collection = {"type": "FeatureCollection", "features": features}
        return feature_collection


def sanitize_csv_value(value):
    return re.sub(r"^([@]|[=]|[+]|[-])", r"'\g<1>", value)
