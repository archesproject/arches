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
import sys
import csv
import json
import uuid
import datetime
from io import StringIO
from time import time
from copy import deepcopy
from os.path import isfile, join
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import (
    import_graph as resourceGraphImporter,
)
from arches.app.models.tile import Tile, TileValidationError
from arches.app.models.resource import Resource
from arches.app.models.models import ResourceInstance
from arches.app.models.models import FunctionXGraph
from arches.app.models.models import NodeGroup
from arches.app.models.models import GraphModel
from arches.app.models.system_settings import settings
from django.core.exceptions import ValidationError
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from .format import Writer
from .format import Reader
from .format import ResourceImportReporter


class ArchesFileWriter(Writer):
    def __init__(self, **kwargs):
        super(ArchesFileWriter, self).__init__(**kwargs)

    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        super(ArchesFileWriter, self).write_resources(
            graph_id=graph_id, resourceinstanceids=resourceinstanceids, **kwargs
        )

        json_for_export = []
        resources = []
        relations = []
        export = {}
        export["business_data"] = {}
        graph_id_to_publication_id = {}

        for resourceinstanceid, tiles in self.resourceinstances.items():
            resourceinstanceid = uuid.UUID(str(resourceinstanceid))
            resource = {}
            resource["tiles"] = tiles
            resource["resourceinstance"] = ResourceInstance.objects.get(
                resourceinstanceid=resourceinstanceid
            )

            graph = resource["resourceinstance"].graph

            if graph.publication_id and not graph_id_to_publication_id.get(graph.pk):
                graph_id_to_publication_id[str(graph.pk)] = str(graph.publication_id)

            resources.append(resource)

        export["business_data"]["resources"] = resources

        if str(self.graph_id) != settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID:
            json_name = os.path.join("{0}.{1}".format(self.file_name, "json"))
        else:
            json_name = os.path.join(
                "{0}".format(os.path.basename(settings.SYSTEM_SETTINGS_LOCAL_PATH))
            )

        dest = StringIO()
        export = JSONDeserializer().deserialize(
            JSONSerializer().serialize(JSONSerializer().serializeToPython(export))
        )

        for resource_data in export["business_data"]["resources"]:
            resource_instance_data = resource_data.get("resourceinstance")

            if resource_instance_data:
                resource_data["resourceinstance"]["publication_id"] = (
                    graph_id_to_publication_id.get(resource_instance_data["graph_id"])
                )

        json.dump(export, dest, indent=kwargs.get("indent", None))
        json_for_export.append({"name": json_name, "outputfile": dest})

        return json_for_export


class ArchesFileReader(Reader):
    def pre_import(self, tile, graph_id):
        for function in self.get_function_class_instances(tile, graph_id):
            try:
                function.on_import(tile)
            except NotImplementedError:
                pass
        return tile

    def get_function_class_instances(self, tile, graph_id):
        ret = []
        functionXgraphs = FunctionXGraph.objects.filter(
            graph_id=graph_id,
            config__triggering_nodegroups__contains=[tile["nodegroup_id"]],
        )
        for functionXgraph in functionXgraphs:
            func = functionXgraph.function.get_class_module()(
                functionXgraph.config, tile["nodegroup_id"]
            )
            ret.append(func)
        return ret

    def validate_business_data(self, business_data):
        errors = []
        if type(business_data) == dict and business_data["resources"]:
            for resource in business_data["resources"]:
                graph_id = resource["resourceinstance"]["graph_id"]
                for tile in resource["tiles"]:
                    try:
                        self.pre_import(tile, graph_id)
                    except ValidationError as e:
                        errors.append(e.args)
        return errors

    def import_graphs(self):
        """
        Wrapper around arches.app.utils.data_management.resource_graphs.importer method.
        """
        resourceGraphImporter(self.graphs)

    def import_reference_data(self):
        """
        Wrapper around arches.app.utils.data_management.concepts.importer method.
        """
        conceptImporter(self.reference_data)

    def replace_source_nodeid(self, tiles, mapping):
        for tile in tiles:
            new_data = []
            for sourcekey in list(tile["data"].keys()):
                for row in mapping["nodes"]:
                    if row["file_field_name"] == sourcekey:
                        d = {}
                        d[row["arches_nodeid"]] = tile["data"][sourcekey]
                        new_data.append(d)
            tile["data"] = new_data
        return tiles

    def import_business_data_without_mapping(
        self, business_data, reporter, overwrite="append", prevent_indexing=False
    ):
        errors = []
        graph_uuids = GraphModel.objects.values_list("pk", flat=True)
        last_resource = None  # only set if prevent_indexing=False
        for resource in business_data["resources"]:
            if resource["resourceinstance"] is not None:
                graph_uuid = uuid.UUID(str(resource["resourceinstance"]["graph_id"]))
                if graph_uuid in graph_uuids:
                    resourceinstanceid = uuid.UUID(
                        str(resource["resourceinstance"]["resourceinstanceid"])
                    )
                    defaults = {
                        "graph_id": graph_uuid,
                        "legacyid": resource["resourceinstance"]["legacyid"],
                    }
                    new_values = {
                        "resourceinstanceid": resourceinstanceid,
                        "createdtime": datetime.datetime.now(),
                    }
                    new_values.update(defaults)
                    if overwrite == "overwrite":
                        resourceinstance = Resource(**new_values)
                    else:
                        try:
                            resourceinstance = Resource.objects.get(
                                resourceinstanceid=resourceinstanceid
                            )
                            for key, value in defaults.items():
                                setattr(resourceinstance, key, value)
                        except Resource.DoesNotExist:
                            resourceinstance = Resource(**new_values)

                    if resource["tiles"] != []:
                        reporter.update_tiles(len(resource["tiles"]))

                        def update_or_create_tile(src_tile):
                            tile = None
                            src_tile["parenttile_id"] = (
                                uuid.UUID(str(src_tile["parenttile_id"]))
                                if src_tile["parenttile_id"]
                                else None
                            )
                            defaults = {
                                "resourceinstance": resourceinstance,
                                "parenttile_id": (
                                    str(src_tile["parenttile_id"])
                                    if src_tile["parenttile_id"]
                                    else None
                                ),
                                "nodegroup_id": (
                                    str(src_tile["nodegroup_id"])
                                    if src_tile["nodegroup_id"]
                                    else None
                                ),
                                "sortorder": (
                                    int(src_tile["sortorder"])
                                    if src_tile["sortorder"]
                                    else 0
                                ),
                                "data": src_tile["data"],
                            }
                            new_values = {"tileid": uuid.UUID(str(src_tile["tileid"]))}
                            new_values.update(defaults)
                            if overwrite == "overwrite":
                                tile = Tile(**new_values)
                            else:
                                try:
                                    tile = Tile.objects.get(
                                        tileid=uuid.UUID(str(src_tile["tileid"]))
                                    )
                                    for key, value in defaults.items():
                                        setattr(tile, key, value)
                                except Tile.DoesNotExist:
                                    tile = Tile(**new_values)
                            if tile is not None:
                                resourceinstance.tiles.append(tile)
                                reporter.update_tiles_saved()

                            for child in src_tile["tiles"]:
                                update_or_create_tile(child)

                        for tile in resource["tiles"]:
                            tile["tiles"] = [
                                child
                                for child in resource["tiles"]
                                if child["parenttile_id"] == tile["tileid"]
                            ]

                        for tile in [
                            k for k in resource["tiles"] if k["parenttile_id"] is None
                        ]:
                            update_or_create_tile(tile)

                    resourceinstance.save(index=False)

                    if not prevent_indexing:
                        last_resource = self.save_descriptors_and_index(
                            resourceinstance, last_resource=last_resource
                        )

                    reporter.update_resources_saved()

    def get_blank_tile(
        self, sourcetilegroup, blanktilecache, tiles, resourceinstanceid
    ):
        if len(sourcetilegroup[0]["data"]) > 0:
            if sourcetilegroup[0]["data"][0] != {}:
                if list(sourcetilegroup[0]["data"][0].keys())[0] not in blanktilecache:
                    blank_tile = Tile.get_blank_tile(
                        list(tiles[0]["data"][0].keys())[0],
                        resourceid=resourceinstanceid,
                    )
                    if blank_tile.data != {}:
                        for tile in blank_tile.tiles:
                            if isinstance(tile, Tile):
                                for key in list(tile.data.keys()):
                                    blanktilecache[key] = blank_tile
                else:
                    blank_tile = blanktilecache[list(tiles[0]["data"][0].keys())[0]]
            else:
                blank_tile = None
        else:
            blank_tile = None
        return blank_tile

    def import_business_data(
        self,
        business_data,
        mapping=None,
        overwrite="append",
        prevent_indexing=False,
        transaction_id=None,
    ):
        reporter = ResourceImportReporter(business_data)
        try:
            if mapping is None or mapping == "":
                self.import_business_data_without_mapping(
                    business_data,
                    reporter,
                    overwrite=overwrite,
                    prevent_indexing=prevent_indexing,
                )
            else:
                blanktilecache = {}
                target_nodegroup_cardinalities = {}
                for nodegroup in JSONSerializer().serializeToPython(
                    NodeGroup.objects.all()
                ):
                    target_nodegroup_cardinalities[nodegroup["nodegroupid"]] = (
                        nodegroup["cardinality"]
                    )

                last_resource = None  # only set if prevent_indexing=False
                for resource in business_data["resources"]:
                    reporter.update_tiles(len(resource["tiles"]))
                    parenttileids = []
                    populated_tiles = []
                    resourceinstanceid = uuid.uuid4()
                    populated_nodegroups = []

                    target_resource_model = mapping["resource_model_id"]

                    for tile in resource["tiles"]:
                        if tile["data"] != {}:

                            def get_tiles(tile):
                                if tile["parenttile_id"] is not None:
                                    if tile["parenttile_id"] not in parenttileids:
                                        parenttileids.append(tile["parenttile_id"])
                                        ret = []
                                        for sibling_tile in resource["tiles"]:
                                            if (
                                                sibling_tile["parenttile_id"]
                                                == tile["parenttile_id"]
                                            ):
                                                ret.append(sibling_tile)
                                    else:
                                        ret = None
                                else:
                                    ret = [tile]

                                # deletes nodes that don't have values
                                if ret is not None:
                                    for tile in ret:
                                        for key, value in tile["data"].items():
                                            if value == "":
                                                del tile["data"][key]
                                return ret

                            tiles = get_tiles(tile)
                            if tiles is not None:
                                mapped_tiles = self.replace_source_nodeid(
                                    tiles, mapping
                                )
                                blank_tile = self.get_blank_tile(
                                    tiles, blanktilecache, tiles, resourceinstanceid
                                )

                                def populate_tile(sourcetilegroup, target_tile):
                                    need_new_tile = False
                                    target_tile_cardinality = (
                                        target_nodegroup_cardinalities[
                                            str(target_tile.nodegroup_id)
                                        ]
                                    )
                                    if (
                                        str(target_tile.nodegroup_id)
                                        not in populated_nodegroups
                                    ):
                                        if target_tile.data != {}:
                                            for source_tile in sourcetilegroup:
                                                for tiledata in source_tile["data"]:
                                                    for nodeid in list(tiledata.keys()):
                                                        if nodeid in target_tile.data:
                                                            if (
                                                                target_tile.data[nodeid]
                                                                is None
                                                            ):
                                                                target_tile.data[
                                                                    nodeid
                                                                ] = tiledata[nodeid]
                                                                for key in list(
                                                                    tiledata.keys()
                                                                ):
                                                                    if key == nodeid:
                                                                        del tiledata[
                                                                            nodeid
                                                                        ]
                                                for tiledata in source_tile["data"]:
                                                    if tiledata == {}:
                                                        source_tile["data"].remove(
                                                            tiledata
                                                        )

                                        elif target_tile.tiles is not None:
                                            populated_child_tiles = []
                                            populated_child_nodegroups = []
                                            for childtile in target_tile.tiles:
                                                childtile_empty = True
                                                child_tile_cardinality = (
                                                    target_nodegroup_cardinalities[
                                                        str(childtile.nodegroup_id)
                                                    ]
                                                )
                                                if (
                                                    str(childtile.nodegroup_id)
                                                    not in populated_child_nodegroups
                                                ):
                                                    prototype_tile = childtile
                                                    prototype_tile.tileid = None

                                                    for source_tile in sourcetilegroup:
                                                        if (
                                                            prototype_tile.nodegroup_id
                                                            not in populated_child_nodegroups
                                                        ):
                                                            prototype_tile_copy = (
                                                                deepcopy(prototype_tile)
                                                            )

                                                            for data in source_tile[
                                                                "data"
                                                            ]:
                                                                for nodeid in list(
                                                                    data.keys()
                                                                ):
                                                                    if nodeid in list(
                                                                        prototype_tile.data.keys()
                                                                    ):
                                                                        if (
                                                                            prototype_tile.data[
                                                                                nodeid
                                                                            ]
                                                                            is None
                                                                        ):
                                                                            prototype_tile_copy.data[
                                                                                nodeid
                                                                            ] = data[
                                                                                nodeid
                                                                            ]
                                                                            for (
                                                                                key
                                                                            ) in list(
                                                                                data.keys()
                                                                            ):
                                                                                if (
                                                                                    key
                                                                                    == nodeid
                                                                                ):
                                                                                    del data[
                                                                                        nodeid
                                                                                    ]
                                                                            if (
                                                                                child_tile_cardinality
                                                                                == "1"
                                                                            ):
                                                                                populated_child_nodegroups.append(
                                                                                    prototype_tile.nodegroup_id
                                                                                )
                                                            for data in source_tile[
                                                                "data"
                                                            ]:
                                                                if data == {}:
                                                                    source_tile[
                                                                        "data"
                                                                    ].remove(data)

                                                            for key in list(
                                                                prototype_tile_copy.data.keys()
                                                            ):
                                                                if (
                                                                    prototype_tile_copy.data[
                                                                        key
                                                                    ]
                                                                    is not None
                                                                ):
                                                                    childtile_empty = (
                                                                        False
                                                                    )
                                                            if (
                                                                prototype_tile_copy.data
                                                                == {}
                                                                or childtile_empty
                                                            ):
                                                                prototype_tile_copy = (
                                                                    None
                                                                )
                                                            if (
                                                                prototype_tile_copy
                                                                is not None
                                                            ):
                                                                populated_child_tiles.append(
                                                                    prototype_tile_copy
                                                                )
                                                        else:
                                                            break

                                            target_tile.tiles = populated_child_tiles

                                        if target_tile.data:
                                            if (
                                                target_tile.data == {}
                                                and target_tile.tiles == {}
                                            ):
                                                target_tile = None

                                        populated_tiles.append(target_tile)

                                        for source_tile in sourcetilegroup:
                                            if source_tile["data"]:
                                                for data in source_tile["data"]:
                                                    if len(data) > 0:
                                                        need_new_tile = True

                                        if need_new_tile:
                                            if (
                                                self.get_blank_tile(
                                                    sourcetilegroup,
                                                    blanktilecache,
                                                    tiles,
                                                    resourceinstanceid,
                                                )
                                                is not None
                                            ):
                                                populate_tile(
                                                    sourcetilegroup,
                                                    self.get_blank_tile(
                                                        sourcetilegroup,
                                                        blanktilecache,
                                                        tiles,
                                                        resourceinstanceid,
                                                    ),
                                                )

                                        if target_tile_cardinality == "1":
                                            populated_nodegroups.append(
                                                str(target_tile.nodegroup_id)
                                            )
                                    else:
                                        target_tile = None

                                if blank_tile is not None:
                                    populate_tile(mapped_tiles, blank_tile)

                    principaluser_id = (
                        resource["princpaluser_id"]
                        if "principaluser_id" in resource
                        else None
                    )
                    newresourceinstance = Resource(
                        resourceinstanceid=resourceinstanceid,
                        graph_id=target_resource_model,
                        legacyid=None,
                        principaluser_id=principaluser_id,
                        createdtime=datetime.datetime.now(),
                    )
                    newresourceinstance.tiles = populated_tiles
                    newresourceinstance.save(index=False, transaction_id=transaction_id)

                    if not prevent_indexing:
                        last_resource = self.save_descriptors_and_index(
                            newresourceinstance, last_resource=last_resource
                        )

                    reporter.update_resources_saved()

        except (KeyError, TypeError) as e:
            print(e)

        finally:
            reporter.report_results()

    def save_descriptors_and_index(self, this_resource, last_resource):
        # Reuse the queryset for FunctionXGraph rows if the graph is the same.
        if last_resource and (last_resource.graph_id == this_resource.graph_id):
            this_resource.descriptor_function = last_resource.descriptor_function
        this_resource.save_descriptors()
        this_resource.index()
        return this_resource

    def import_all(self):
        errors = []
        conceptImporter(self.reference_data)
        resource_graph_errors, resource_graph_reporter = resourceGraphImporter(
            self.graphs
        )
        resource_graph_reporter.report_results()
        errors = self.validate_business_data(self.business_data)
        if len(errors) == 0:
            if self.business_data not in ("", []):
                self.import_business_data(self.business_data, self.mapping)
        else:
            for error in errors:
                print("{0} {1}".format(error[0], error[1]))
