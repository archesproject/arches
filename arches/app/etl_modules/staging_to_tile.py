import logging
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import groupby

from django.db import connection, transaction
from django.db.models import OuterRef, Subquery
from django.utils import timezone

from arches.app.models.models import (
    EditLog,
    File,
    GraphModel,
    LoadEvent,
    LoadStaging,
    Node,
    ResourceInstance,
    ResourceInstanceLifecycleState,
    TileModel,
)
from arches.app.models.system_settings import settings

logger = logging.getLogger(__name__)


@transaction.atomic
def staging_to_tile(load_id, max_workers=4):
    now = timezone.now()

    logger.debug("Loading staging records for load_id=%s", load_id)
    valid_staged_tiles = LoadStaging.objects.filter(
        load_event_id=load_id, passes_validation=True
    ).order_by("nodegroup_depth")

    # Lightweight pass: only the three fields needed for metadata — avoids
    # fetching the (potentially large) value JSON for the metadata phase.
    valid_meta = list(
        valid_staged_tiles.values("nodegroup_id", "resourceid", "legacyid")
    )
    logger.debug(
        "Loaded %d valid staging records for load_id=%s", len(valid_meta), load_id
    )
    nodegroup_ids = {r["nodegroup_id"] for r in valid_meta if r["nodegroup_id"]}

    nodegroup_to_graph = dict(
        Node.objects.filter(nodegroup_id__in=nodegroup_ids)
        .values_list("nodegroup_id", "graph_id")
        .distinct()
    )

    graph_ids = set(nodegroup_to_graph.values())
    graph_to_lifecycle_state = dict(
        GraphModel.objects.filter(graphid__in=graph_ids)
        .annotate(
            initial_state_id=Subquery(
                ResourceInstanceLifecycleState.objects.filter(
                    resource_instance_lifecycle_id=OuterRef(
                        "resource_instance_lifecycle_id"
                    ),
                    is_initial_state=True,
                ).values("id")[:1]
            )
        )
        .values_list("graphid", "initial_state_id")
    )

    resource_meta = {
        r["resourceid"]: {
            "graph_id": nodegroup_to_graph.get(r["nodegroup_id"]),
            "legacyid": r["legacyid"],
        }
        for r in valid_meta
        if r["resourceid"]
    }

    existing_ids = set(
        ResourceInstance.objects.filter(
            resourceinstanceid__in=resource_meta
        ).values_list("resourceinstanceid", flat=True)
    )
    new_ids = resource_meta.keys() - existing_ids
    logger.debug(
        "Creating %d new ResourceInstances (%d already exist)",
        len(new_ids),
        len(existing_ids),
    )
    ResourceInstance.objects.bulk_create(
        [
            ResourceInstance(
                resourceinstanceid=rid,
                graph_id=resource_meta[rid]["graph_id"],
                legacyid=resource_meta[rid]["legacyid"],
                resource_instance_lifecycle_state_id=graph_to_lifecycle_state.get(
                    resource_meta[rid]["graph_id"]
                ),
            )
            for rid in new_ids
            if resource_meta.get(rid, {}).get("graph_id")
        ],
        settings.BULK_IMPORT_BATCH_SIZE,
    )
    EditLog.objects.bulk_create(
        [
            EditLog(
                resourceclassid=resource_meta[rid]["graph_id"],
                resourceinstanceid=str(rid),
                edittype="create",
                timestamp=now,
                note="loaded from staging_table",
                transactionid=load_id,
            )
            for rid in new_ids
            if resource_meta.get(rid, {}).get("graph_id")
        ],
        settings.BULK_IMPORT_BATCH_SIZE,
    )

    # Stream full ORM objects one chunk at a time — never holds all records in memory.
    for depth, group in groupby(
        valid_staged_tiles.iterator(chunk_size=2000), key=lambda r: r.nodegroup_depth
    ):
        staged_tiles = list(group)
        logger.debug(
            "Processing nodegroup depth %s: %d staged tiles", depth, len(staged_tiles)
        )
        edit_logs = []
        inserts = [
            staged_tile
            for staged_tile in staged_tiles
            if staged_tile.operation == "insert"
        ]
        updates = [
            staged_tile
            for staged_tile in staged_tiles
            if staged_tile.operation != "insert"
        ]

        if updates:
            update_tile_ids = {staged_tile.tileid for staged_tile in updates}
            existing_tiles = {
                tile.tileid: tile
                for tile in TileModel.objects.filter(tileid__in=update_tile_ids)
            }
            existing_tile_ids = existing_tiles.keys()
            inserts += [
                staged_tile
                for staged_tile in updates
                if staged_tile.tileid not in existing_tile_ids
            ]
            real_updates = [
                staged_tile
                for staged_tile in updates
                if staged_tile.tileid in existing_tile_ids
            ]
        else:
            real_updates = []
            existing_tiles = {}

        if inserts:
            logger.debug("Bulk inserting %d tiles at depth %s", len(inserts), depth)
            tile_data_map = {r.tileid: _build_tile_data(r.value) for r in inserts}
            TileModel.objects.bulk_create(
                [
                    TileModel(
                        tileid=r.tileid,
                        data=tile_data_map[r.tileid],
                        nodegroup_id=r.nodegroup_id,
                        parenttile_id=r.parenttileid,
                        resourceinstance_id=r.resourceid,
                        sortorder=r.sortorder,
                    )
                    for r in inserts
                ],
                settings.BULK_IMPORT_BATCH_SIZE,
            )
            edit_logs += [
                EditLog(
                    resourceclassid=nodegroup_to_graph.get(r.nodegroup_id),
                    resourceinstanceid=str(r.resourceid),
                    nodegroupid=str(r.nodegroup_id),
                    tileinstanceid=str(r.tileid),
                    edittype="tile create",
                    newvalue=tile_data_map[r.tileid],
                    timestamp=now,
                    note="loaded from staging_table",
                    transactionid=load_id,
                )
                for r in inserts
            ]

        if real_updates:
            logger.debug("Bulk updating %d tiles at depth %s", len(real_updates), depth)
            tiles_to_update = []
            for r in real_updates:
                tile = existing_tiles.get(r.tileid)
                if not tile:
                    continue
                new_data = _build_tile_data(r.value)
                edit_logs.append(
                    EditLog(
                        resourceclassid=nodegroup_to_graph.get(r.nodegroup_id),
                        resourceinstanceid=str(r.resourceid),
                        nodegroupid=str(r.nodegroup_id),
                        tileinstanceid=str(r.tileid),
                        edittype="tile edit",
                        newvalue=new_data,
                        oldvalue=tile.data,
                        timestamp=now,
                        note="loaded from staging_table",
                        transactionid=load_id,
                    )
                )
                tile.data = new_data
                tile.sortorder = r.sortorder
                tiles_to_update.append(tile)
            TileModel.objects.bulk_update(tiles_to_update, ["data", "sortorder"])

        if edit_logs:
            logger.debug("Writing %d edit logs for depth %s", len(edit_logs), depth)
            EditLog.objects.bulk_create(edit_logs, settings.BULK_IMPORT_BATCH_SIZE)

    logger.debug("Tile processing complete")
    _post_process_staging(
        LoadStaging.objects.filter(load_event_id=load_id).iterator(chunk_size=2000),
        max_workers=max_workers,
    )

    LoadEvent.objects.filter(loadid=load_id).update(
        load_end_time=now,
        complete=True,
        successful=True,
    )
    logger.debug("Refreshing transaction GeoJSON geometries for load_id=%s", load_id)
    with connection.cursor() as cursor:
        cursor.execute("SELECT refresh_transaction_geojson_geometries(%s)", [load_id])
    logger.debug("staging_to_tile complete for load_id=%s", load_id)
    return True


def _build_tile_data(staged_value):
    """
    Convert staged value JSON → tile data dict.
    """

    tile_data = {}
    for key, value_dict in staged_value.items():
        if not isinstance(value_dict, dict):
            tile_data[key] = value_dict
            continue
        tile_data_value = value_dict.get("value")
        datatype = value_dict.get("datatype")
        if (
            datatype in ("resource-instance-list", "resource-instance")
            and tile_data_value is not None
        ):
            items = tile_data_value if isinstance(tile_data_value, list) else []
            tile_data_value = [
                {**item, "resourceXresourceId": str(uuid.uuid4())} for item in items
            ]
        tile_data[key] = tile_data_value
    return tile_data


def _post_process_staging(staging_records, max_workers=4):
    """
    File associations + resource relationship refreshes.
    These are independent per-tile, so they parallize well.
    """
    resource_refresh_tile_ids = set()

    for record in staging_records:
        if not record.value:
            continue
        for value_dict in record.value.values():
            if not isinstance(value_dict, dict):
                continue
            datatype = value_dict.get("datatype")
            if datatype == "file-list":
                for file_item in value_dict.get("value") or []:
                    file_id = file_item.get("file_id")
                    if file_id:
                        File.objects.filter(fileid=file_id).update(
                            tile_id=record.tileid
                        )
            elif datatype in ("resource-instance-list", "resource-instance"):
                resource_refresh_tile_ids.add(record.tileid)

    logger.debug(
        "Refreshing resource relationships for %d tiles", len(resource_refresh_tile_ids)
    )
    if resource_refresh_tile_ids:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_refresh_resource_relationships, tid): tid
                for tid in resource_refresh_tile_ids
            }
            for future in as_completed(futures):
                future.result()  # re-raise any exceptions


def _refresh_resource_relationships(tile_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT __arches_refresh_tile_resource_relationships(%s)", [tile_id]
        )
