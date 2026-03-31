"""
Bulk import for arches JSON business data.

Provides a high-throughput import path using Django's bulk_create
instead of individual Resource.save() calls.  Intended for large
datasets (hundreds/thousands of resources) where the overhead of
per-resource save hooks is prohibitive.

Trade-offs vs the standard ArchesFileReader path:
  - No edit-log entries are created
  - Tile.save() hooks (pre/post save functions, datatype post-save
    actions) are bypassed unless fire_functions=True
  - Nested / recursive tile structures are NOT supported; tiles must
    arrive as a flat list with parenttile_id references
  - Append-mode "update existing" is not supported; resources are
    always created (duplicates are caught by constraint checks)
"""

import json
import uuid
import datetime

from arches.app.models.tile import Tile, TileValidationError
from arches.app.models.resource import Resource
from arches.app.models.models import FunctionXGraph
from arches.app.models.models import GraphModel


class BulkArchesFileImporter:
    """Bulk-create importer for arches JSON business data."""

    def __init__(
        self,
        reporter,
        overwrite="append",
        prevent_indexing=False,
        bulk_size=100,
        skip_validation=False,
        fire_functions=False,
    ):
        self.reporter = reporter
        self.overwrite = overwrite
        self.prevent_indexing = prevent_indexing
        self.bulk_size = bulk_size
        self.skip_validation = skip_validation
        self.fire_functions = fire_functions

        self.failed_resources = []
        self._imported_resource_ids = []

    # Public entry point
    def import_resources(self, business_data):
        """Import all resources from *business_data* using bulk operations."""
        graph_uuids = GraphModel.objects.values_list("pk", flat=True)
        defaults_cache = {}

        constraint_map = self._load_constraint_map()
        global_constraint_seen = self._seed_global_constraints(constraint_map)

        batch = []
        batch_rejected = 0
        seen_ids = set()
        for resource in business_data["resources"]:
            if resource["resourceinstance"] is None:
                self._fail("unknown", None, "Null resourceinstance")
                batch_rejected += 1
                continue

            resourceinstance = self._build_resource(
                resource, graph_uuids, defaults_cache,
            )
            if resourceinstance is None:
                batch_rejected += 1
                continue

            rid = resourceinstance.resourceinstanceid
            if rid in seen_ids:
                self._fail(
                    str(rid),
                    str(resourceinstance.graph_id),
                    "Duplicate resourceinstanceid within import file",
                )
                batch_rejected += 1
                continue
            seen_ids.add(rid)

            batch.append(resourceinstance)
            if len(batch) + batch_rejected >= self.bulk_size:
                self._flush_batch(
                    batch, constraint_map, global_constraint_seen,
                    rejected=batch_rejected,
                )
                batch = []
                batch_rejected = 0

        self._flush_batch(
            batch, constraint_map, global_constraint_seen,
            rejected=batch_rejected,
        )

        if not self.prevent_indexing and self._imported_resource_ids:
            from arches.app.utils.index_database import index_resources_using_singleprocessing
            from arches.app.models.resource import Resource as ResourceModel

            print(f"  Bulk indexing {len(self._imported_resource_ids)} resources...")
            resources = ResourceModel.objects.filter(
                resourceinstanceid__in=self._imported_resource_ids
            )
            index_resources_using_singleprocessing(
                resources=resources,
                batch_size=self.bulk_size,
                quiet=False,
                title="Bulk import indexing",
            )

        self._report_failures()

    # Resource construction
    def _build_resource(self, resource_data, graph_uuids, defaults_cache):
        """Build a Resource with tiles for bulk import.

        Returns the Resource instance, or None on failure.
        """
        ri = resource_data["resourceinstance"]
        if not ri.get("graph_id"):
            self._fail(ri.get("resourceinstanceid", "unknown"), None,
                       "Missing graph_id")
            return None
        if not ri.get("resourceinstanceid"):
            self._fail("unknown", ri.get("graph_id"),
                       "Missing resourceinstanceid")
            return None

        graph_uuid = uuid.UUID(str(ri["graph_id"]))
        if graph_uuid not in graph_uuids:
            self._fail(ri.get("resourceinstanceid"), str(graph_uuid),
                       f"Graph {graph_uuid} not found in database")
            return None

        if graph_uuid not in defaults_cache:
            graph = GraphModel.objects.select_related(
                "publication", "resource_instance_lifecycle"
            ).get(pk=graph_uuid)
            lifecycle_state = None
            try:
                lifecycle = graph.resource_instance_lifecycle
                lifecycle_state = (
                    lifecycle.resource_instance_lifecycle_states.get(
                        is_initial_state=True
                    )
                )
            except Exception:
                pass
            defaults_cache[graph_uuid] = {
                "graph_publication": graph.publication,
                "lifecycle_state": lifecycle_state,
            }

        defaults = defaults_cache[graph_uuid]
        resourceinstanceid = uuid.UUID(str(ri["resourceinstanceid"]))
        resourceinstance = Resource(
            resourceinstanceid=resourceinstanceid,
            graph_id=graph_uuid,
            legacyid=ri.get("legacyid"),
            createdtime=datetime.datetime.now(),
            graph_publication=defaults["graph_publication"],
            resource_instance_lifecycle_state=defaults["lifecycle_state"],
        )

        if resource_data["tiles"]:
            for src_tile in resource_data["tiles"]:
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

        return resourceinstance

    # Constraint infrastructure
    @staticmethod
    def _load_constraint_map():
        """Load unique constraints keyed by nodegroup_id."""
        from arches.app.models.models import ConstraintModel
        constraint_map = {}
        for constraint in (
            ConstraintModel.objects.select_related("card")
            .prefetch_related("nodes")
            .all()
        ):
            ng_id = str(constraint.card.nodegroup_id)
            node_ids = [str(n.nodeid) for n in constraint.nodes.all()]
            if node_ids:
                constraint_map.setdefault(ng_id, []).append({
                    "node_ids": node_ids,
                    "uniquetoall": constraint.uniquetoallinstances,
                })
        return constraint_map

    def _seed_global_constraints(self, constraint_map):
        """Pre-seed global constraint values from existing DB data.

        In overwrite mode existing records will be deleted before insert,
        so pre-seeding would cause false positives.
        """
        seen = set()
        if self.overwrite == "overwrite":
            return seen

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
                            seen.add((ng_id, ci, tuple(values)))
        if seen:
            print(
                f"  Pre-seeded {len(seen)} existing "
                f"constraint values from database"
            )
        return seen

    @staticmethod
    def _check_constraints(resource, constraint_map, global_constraint_seen):
        """Check unique constraints for a resource.

        Mutates *global_constraint_seen* for cross-batch tracking.
        Returns an error string, or None if valid.
        """
        per_resource_seen = set()
        for tile in resource.tiles:
            ng_id = str(tile.nodegroup_id)
            if ng_id not in constraint_map:
                continue
            for ci, constraint in enumerate(constraint_map[ng_id]):
                values = []
                skip = False
                for nid in sorted(constraint["node_ids"]):
                    val = tile.data.get(nid)
                    if val is None:
                        skip = True
                        break
                    values.append(json.dumps(val, sort_keys=True))
                if skip:
                    continue
                lookup = (ng_id, ci, tuple(values))
                if constraint["uniquetoall"]:
                    if lookup in global_constraint_seen:
                        return (
                            f"Unique constraint violation (global) on "
                            f"nodegroup {ng_id}: duplicate value"
                        )
                    global_constraint_seen.add(lookup)
                else:
                    if lookup in per_resource_seen:
                        return (
                            f"Unique constraint violation (per-resource) on "
                            f"nodegroup {ng_id}: duplicate value"
                        )
                per_resource_seen.add(lookup)
        return None

    # Validation
    def _validate_batch(
        self, batch, constraint_map, global_constraint_seen, rejected=0,
    ):
        """Validate a batch of resources.

        Returns (valid_resources, failures).
        """

        if self.skip_validation:
            print(f"  Skipping validation for {len(batch)} resources...")
            return list(batch), []

        total = len(batch) + rejected
        print(f"  Validating {total} resources...")
        valid_resources = []
        failures = []

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
                print(f"    validated {ri}/{len(batch) + rejected}...")
            resource_valid = True

            constraint_error = self._check_constraints(
                resource, constraint_map, global_constraint_seen
            )
            if constraint_error:
                failures.append({
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
                        for nodeid in tile.data.keys():
                            node = next(
                                (
                                    item
                                    for item in tile.serialized_graph["nodes"]
                                    if item["nodeid"] == nodeid
                                ),
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
                        failures.append({
                            "resourceinstanceid": str(
                                resource.resourceinstanceid
                            ),
                            "graph_id": str(resource.graph_id),
                            "reason": f"Tile {tile.tileid}: {e}",
                        })
                        resource_valid = False
                        break
                    except Exception as e:
                        failures.append({
                            "resourceinstanceid": str(
                                resource.resourceinstanceid
                            ),
                            "graph_id": str(resource.graph_id),
                            "reason": (
                                f"Tile {tile.tileid}: "
                                f"{type(e).__name__}: {e}"
                            ),
                        })
                        resource_valid = False
                        break

            if resource_valid:
                valid_resources.append(resource)

        failed = len(batch) - len(valid_resources)
        print(
            f"  {len(valid_resources)}/{total} passed validation, "
            f"{failed} failed, {rejected} rejected"
        )
        return valid_resources, failures

    # Batch flush: validate -> save -> post-save
    def _flush_batch(
        self, batch, constraint_map, global_constraint_seen, rejected=0,
    ):
        """Validate and save a batch of resources using bulk operations."""
        if not batch:
            return

        if self.overwrite == "overwrite":
            existing_ids = [r.resourceinstanceid for r in batch]
            Resource.objects.filter(
                resourceinstanceid__in=existing_ids
            ).delete()
        else:
            candidate_ids = [r.resourceinstanceid for r in batch]
            already_exist = set(
                Resource.objects.filter(
                    resourceinstanceid__in=candidate_ids
                ).values_list("resourceinstanceid", flat=True)
            )
            if already_exist:
                print(
                    f"  Skipping {len(already_exist)} duplicate "
                    f"resource(s) that already exist in the database"
                )
                for r in batch:
                    if r.resourceinstanceid in already_exist:
                        self._fail(
                            str(r.resourceinstanceid),
                            str(r.graph_id),
                            "Resource already exists (duplicate resourceinstanceid)",
                        )
                batch = [
                    r for r in batch
                    if r.resourceinstanceid not in already_exist
                ]
                if not batch:
                    return

        valid_resources, failures = self._validate_batch(
            batch, constraint_map, global_constraint_seen,
            rejected=rejected,
        )
        self.failed_resources.extend(failures)

        if not valid_resources:
            return

        # Bulk create
        tiles = []
        for resource in valid_resources:
            tiles.extend(resource.tiles)
        print(
            f"  Bulk creating {len(valid_resources)} resources, "
            f"{len(tiles)} tiles..."
        )
        Resource.objects.bulk_create(valid_resources)
        Tile.objects.bulk_create(tiles)
        self.reporter.update_tiles(len(tiles))
        for _ in tiles:
            self.reporter.update_tiles_saved()
        print(f"  DB save complete. Computing descriptors...")

        for resource in valid_resources:
            try:
                resource.save_descriptors()
            except Exception as e:
                self._fail(
                    str(resource.resourceinstanceid),
                    str(resource.graph_id),
                    f"Descriptor error: {e}",
                )

        if self.fire_functions:
            self._run_post_save_functions(valid_resources)

        self._imported_resource_ids.extend(
            r.resourceinstanceid for r in valid_resources
        )
        self.reporter.update_resources_saved(count=len(valid_resources))

    # Post-save function triggers
    def _run_post_save_functions(self, valid_resources):
        """Run FunctionXGraph post_save triggers for bulk-created resources."""
        print(
            f"  Running post-save functions for "
            f"{len(valid_resources)} resources..."
        )
        fxg_cache = {}
        for resource in valid_resources:
            gid = str(resource.graph_id)
            if gid not in fxg_cache:
                fxg_cache[gid] = list(
                    FunctionXGraph.objects.filter(
                        graph_id=resource.graph_id,
                    ).select_related("function").exclude(
                        function__functiontype="primarydescriptors"
                    )
                )
            for tile in resource.tiles:
                for fxg in fxg_cache[gid]:
                    triggering = fxg.config.get(
                        "triggering_nodegroups", []
                    )
                    if (
                        triggering
                        and str(tile.nodegroup_id) not in triggering
                    ):
                        continue
                    try:
                        func = fxg.function.get_class_module()(
                            fxg.config, tile.nodegroup_id
                        )
                        func.post_save(tile, None, None)
                    except NotImplementedError:
                        pass
                    except Exception as e:
                        self._fail(
                            str(resource.resourceinstanceid),
                            str(resource.graph_id),
                            f"Post-save function failed for "
                            f"tile {tile.tileid}: {e}",
                        )

    # Failure tracking / reporting
    def _fail(self, resourceinstanceid, graph_id, reason):
        self.failed_resources.append({
            "resourceinstanceid": str(resourceinstanceid),
            "graph_id": str(graph_id) if graph_id else None,
            "reason": reason,
        })

    def _report_failures(self):
        if self.failed_resources:
            print("\n" + "=" * 80)
            print(
                f"IMPORT ERRORS: {len(self.failed_resources)} "
                f"resource(s) failed"
            )
            print("=" * 80)
            from collections import defaultdict
            by_reason = defaultdict(list)
            for failure in self.failed_resources:
                by_reason[failure["reason"]].append(failure)
            for reason, failures in by_reason.items():
                print(f"\n  {reason}")
                print(f"  Affected resources ({len(failures)}):")
                for f in failures[:20]:
                    print(
                        f"    - {f['resourceinstanceid']} "
                        f"(graph: {f['graph_id']})"
                    )
                if len(failures) > 20:
                    print(f"    ... and {len(failures) - 20} more")
            print("\n" + "=" * 80)
        else:
            print("\nAll resources imported successfully.")
