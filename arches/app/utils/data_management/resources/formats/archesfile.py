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
        self, business_data, reporter, overwrite="append", prevent_indexing=False,
        bulk_size=100,
    ):
        graph_uuids = GraphModel.objects.values_list("pk", flat=True)
        batch = []
        failed_resources = []  # list of {"resourceinstanceid", "graph_id", "reason"}

        # Cache per-graph defaults to avoid repeated queries
        graph_defaults_cache = {}

        def get_graph_defaults(graph_uuid):
            if graph_uuid not in graph_defaults_cache:
                graph = GraphModel.objects.select_related(
                    "publication", "resource_instance_lifecycle"
                ).get(pk=graph_uuid)
                lifecycle_state = None
                try:
                    lifecycle = graph.resource_instance_lifecycle
                    lifecycle_state = lifecycle.resource_instance_lifecycle_states.get(
                        is_initial_state=True
                    )
                except Exception:
                    pass
                graph_defaults_cache[graph_uuid] = {
                    "graph_publication": graph.publication,
                    "lifecycle_state": lifecycle_state,
                }
            return graph_defaults_cache[graph_uuid]

        def build_resource(resource):
            """Build a Resource with tiles from a business data resource dict."""
            ri = resource["resourceinstance"]
            if not ri.get("graph_id"):
                failed_resources.append({
                    "resourceinstanceid": ri.get("resourceinstanceid", "unknown"),
                    "graph_id": None,
                    "reason": "Missing graph_id",
                })
                return None
            if not ri.get("resourceinstanceid"):
                failed_resources.append({
                    "resourceinstanceid": "unknown",
                    "graph_id": ri.get("graph_id"),
                    "reason": "Missing resourceinstanceid",
                })
                return None

            graph_uuid = uuid.UUID(str(ri["graph_id"]))
            if graph_uuid not in graph_uuids:
                failed_resources.append({
                    "resourceinstanceid": ri.get("resourceinstanceid"),
                    "graph_id": str(graph_uuid),
                    "reason": f"Graph {graph_uuid} not found in database",
                })
                return None

            resourceinstanceid = uuid.UUID(str(ri["resourceinstanceid"]))
            defaults = get_graph_defaults(graph_uuid)
            resourceinstance = Resource(
                resourceinstanceid=resourceinstanceid,
                graph_id=graph_uuid,
                legacyid=ri.get("legacyid"),
                createdtime=datetime.datetime.now(),
                graph_publication=defaults["graph_publication"],
                resource_instance_lifecycle_state=defaults["lifecycle_state"],
            )

            if resource["tiles"]:
                reporter.update_tiles(len(resource["tiles"]))

                for src_tile in resource["tiles"]:
                    tile = Tile(
                        tileid=uuid.UUID(str(src_tile["tileid"])),
                        resourceinstance=resourceinstance,
                        parenttile_id=(
                            uuid.UUID(str(src_tile["parenttile_id"]))
                            if src_tile.get("parenttile_id")
                            else None
                        ),
                        nodegroup_id=(
                            str(src_tile["nodegroup_id"])
                            if src_tile.get("nodegroup_id")
                            else None
                        ),
                        sortorder=(
                            int(src_tile["sortorder"])
                            if src_tile.get("sortorder")
                            else 0
                        ),
                        data=src_tile["data"],
                    )
                    resourceinstance.tiles.append(tile)
                    reporter.update_tiles_saved()

            return resourceinstance

        # Preload constraints: {nodegroup_id: [(constraint, [node_ids], uniquetoall)]}
        from arches.app.models.models import CardModel, ConstraintModel
        constraint_map = {}
        for constraint in ConstraintModel.objects.select_related("card").prefetch_related("nodes").all():
            ng_id = str(constraint.card.nodegroup_id)
            node_ids = [str(n.nodeid) for n in constraint.nodes.all()]
            if node_ids:
                constraint_map.setdefault(ng_id, []).append({
                    "node_ids": node_ids,
                    "uniquetoall": constraint.uniquetoallinstances,
                })

        # In-memory constraint tracking:
        # global_seen: {(nodegroup_id, constraint_idx, value_key)} for uniquetoallinstances
        # per_resource_seen: reset per resource for within-resource constraints
        global_constraint_seen = set()

        # Pre-seed global constraints from existing DB data (append mode only)
        # In overwrite mode, existing records will be deleted before insert,
        # so pre-seeding would cause false positives.
        if overwrite != "overwrite":
            for ng_id, constraints in constraint_map.items():
                for ci, constraint in enumerate(constraints):
                    if not constraint["uniquetoall"]:
                        continue
                    existing_tiles = Tile.objects.filter(
                        nodegroup_id=ng_id
                    ).values_list("data", flat=True)
                    for tile_data in existing_tiles:
                        if tile_data:
                            values = []
                            skip = False
                            for nid in sorted(constraint["node_ids"]):
                                val = tile_data.get(nid)
                                if val is None:
                                    skip = True
                                    break
                                values.append(json.dumps(val, sort_keys=True))
                            if not skip:
                                global_constraint_seen.add(
                                    (ng_id, ci, tuple(values))
                                )
            if global_constraint_seen:
                print(
                    f"  Pre-seeded {len(global_constraint_seen)} existing "
                    f"constraint values from database"
                )

        def make_constraint_key(tile_data, node_ids):
            """Create a hashable key from tile data for constraint nodes."""
            values = []
            for nid in sorted(node_ids):
                val = tile_data.get(nid)
                if val is None:
                    return None  # Skip constraint check if value is null
                values.append(json.dumps(val, sort_keys=True))
            return tuple(values)

        def check_constraints(resource):
            """Check unique constraints using in-memory tracking.
            Returns error string or None."""
            per_resource_seen = set()
            for tile in resource.tiles:
                ng_id = str(tile.nodegroup_id)
                if ng_id not in constraint_map:
                    continue
                for ci, constraint in enumerate(constraint_map[ng_id]):
                    key = make_constraint_key(tile.data, constraint["node_ids"])
                    if key is None:
                        continue
                    lookup = (ng_id, ci, key)
                    if constraint["uniquetoall"]:
                        if lookup in global_constraint_seen:
                            return (
                                f"Unique constraint violation (global) on "
                                f"nodegroup {ng_id}: duplicate value"
                            )
                    else:
                        if lookup in per_resource_seen:
                            return (
                                f"Unique constraint violation (per-resource) on "
                                f"nodegroup {ng_id}: duplicate value"
                            )
                    if constraint["uniquetoall"]:
                        global_constraint_seen.add(lookup)
                    per_resource_seen.add(lookup)
            return None

        def flush_batch(batch, prevent_indexing, overwrite):
            """Validate and save a batch of resources using bulk operations."""
            if not batch:
                return
            if overwrite == "overwrite":
                existing_ids = [r.resourceinstanceid for r in batch]
                Resource.objects.filter(
                    resourceinstanceid__in=existing_ids
                ).delete()

            # Validate tiles using arches' built-in validation + constraint checks
            print(f"  Validating {len(batch)} resources...")
            valid_resources = []

            # Cache serialized graph per graph_id
            serialized_graph_cache = {}
            for resource in batch:
                gid = str(resource.graph_id)
                if gid not in serialized_graph_cache:
                    published = resource.graph.get_published_graph()
                    serialized_graph_cache[gid] = (
                        published.serialized_graph if published else None
                    )

            for ri, resource in enumerate(batch):
                if ri > 0 and ri % 25 == 0:
                    print(f"    validated {ri}/{len(batch)}...")
                resource_valid = True

                # Check unique constraints in-memory
                constraint_error = check_constraints(resource)
                if constraint_error:
                    failed_resources.append({
                        "resourceinstanceid": str(resource.resourceinstanceid),
                        "graph_id": str(resource.graph_id),
                        "reason": constraint_error,
                    })
                    resource_valid = False

                if resource_valid:
                    sg = serialized_graph_cache.get(str(resource.graph_id))
                    for tile in resource.tiles:
                        try:
                            tile.serialized_graph = sg
                            # Run datatype pre-save hooks (data normalisation)
                            for nodeid in tile.data.keys():
                                node = next(
                                    (item for item in tile.serialized_graph["nodes"]
                                     if item["nodeid"] == nodeid),
                                    None,
                                )
                                if node:
                                    datatype = tile.datatype_factory.get_instance(
                                        node["datatype"]
                                    )
                                    datatype.pre_tile_save(tile, nodeid)
                            tile.check_for_missing_nodes()
                            tile.populate_missing_nodes()
                            tile.validate(raise_early=False)
                        except TileValidationError as e:
                            reason = f"Tile {tile.tileid}: {e}"
                            if len(failed_resources) < 3:
                                print(f"    FAIL: {resource.resourceinstanceid}: {reason}")
                            failed_resources.append({
                                "resourceinstanceid": str(resource.resourceinstanceid),
                                "graph_id": str(resource.graph_id),
                                "reason": reason,
                            })
                            resource_valid = False
                            break
                        except Exception as e:
                            reason = f"Tile {tile.tileid}: {type(e).__name__}: {e}"
                            if len(failed_resources) < 3:
                                print(f"    FAIL: {resource.resourceinstanceid}: {reason}")
                            failed_resources.append({
                                "resourceinstanceid": str(resource.resourceinstanceid),
                                "graph_id": str(resource.graph_id),
                                "reason": reason,
                            })
                            resource_valid = False
                            break

                if resource_valid:
                    valid_resources.append(resource)

            print(f"  {len(valid_resources)}/{len(batch)} passed validation, {len(batch) - len(valid_resources)} failed")
            if not valid_resources:
                return

            # Bulk create resources and tiles
            tiles = []
            for resource in valid_resources:
                tiles.extend(resource.tiles)
            print(f"  Bulk creating {len(valid_resources)} resources, {len(tiles)} tiles...")
            Resource.objects.bulk_create(valid_resources)
            Tile.objects.bulk_create(tiles)
            print(f"  DB save complete. Computing descriptors...")

            for resource in valid_resources:
                try:
                    resource.save_descriptors()
                except Exception as e:
                    failed_resources.append({
                        "resourceinstanceid": str(resource.resourceinstanceid),
                        "graph_id": str(resource.graph_id),
                        "reason": f"Descriptor error: {e}",
                    })

            reporter.update_resources_saved(count=len(valid_resources))

        for resource in business_data["resources"]:
            if resource["resourceinstance"] is None:
                continue

            resourceinstance = build_resource(resource)
            if resourceinstance is None:
                continue

            batch.append(resourceinstance)

            if len(batch) >= bulk_size:
                flush_batch(batch, prevent_indexing, overwrite)
                batch = []

        flush_batch(batch, prevent_indexing, overwrite)

        # Print failure summary
        if failed_resources:
            print("\n" + "=" * 80)
            print(f"IMPORT ERRORS: {len(failed_resources)} resource(s) failed")
            print("=" * 80)

            # Group by reason for readability
            from collections import defaultdict
            by_reason = defaultdict(list)
            for failure in failed_resources:
                by_reason[failure["reason"]].append(failure)

            for reason, failures in by_reason.items():
                print(f"\n  {reason}")
                print(f"  Affected resources ({len(failures)}):")
                for f in failures[:20]:
                    print(f"    - {f['resourceinstanceid']} (graph: {f['graph_id']})")
                if len(failures) > 20:
                    print(f"    ... and {len(failures) - 20} more")

            print("\n" + "=" * 80)
        else:
            print("\nAll resources imported successfully.")

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
            import traceback
            traceback.print_exc()

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
