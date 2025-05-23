import logging
import uuid
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.models.models import IIIFManifest, EditLog, WorkflowHistory
from arches.app.utils.index_database import (
    index_resources_by_transaction,
    optimize_resource_iteration,
    index_tile_deletion_by_transaction,
)
from django.db import transaction, DatabaseError
from django.db.models import Func, F

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Given a transaction ID, reverse (delete or update) tiles and resources created/updated during the transaction
def reverse_edit_log_entries(transaction_id, user=None, chunk_size=2000):
    revserse_operation_transactionid = str(uuid.uuid4())

    transaction_changes = EditLog.objects.filter(transactionid=transaction_id)

    resource_create_changes = transaction_changes.filter(edittype="create")
    tile_edit_changes = transaction_changes.filter(edittype="tile edit")
    tile_create_changes = transaction_changes.filter(edittype="tile create")

    number_of_db_changes = (
        resource_create_changes.count()
        + tile_edit_changes.count()
        + tile_create_changes.count()
    )

    # cast resourceinstanceid to UUID
    resource_create_changes = resource_create_changes.annotate(
        resourceinstanceid_uuid=Func(F("resourceinstanceid"), function="UUID")
    )
    created_resources_query_set = Resource.objects.filter(
        resourceinstanceid__in=resource_create_changes.values_list(
            "resourceinstanceid_uuid", flat=True
        )
    )

    for resource in optimize_resource_iteration(
        created_resources_query_set, chunk_size=chunk_size
    ):
        resource.delete(
            fetch_relations=False,
            user=user,
            transaction_id=revserse_operation_transactionid,
        )

    # cast tileinstanceid to UUID
    tile_create_changes = tile_create_changes.annotate(
        tileinstanceid_uuid=Func(F("tileinstanceid"), function="UUID")
    )

    for tile in Tile.objects.filter(
        tileid__in=tile_create_changes.values_list("tileinstanceid_uuid", flat=True)
    ).iterator(chunk_size=chunk_size):
        tile.delete(
            recalculate_descriptors=False,
            index=False,
            transaction_id=revserse_operation_transactionid,
            user=user,
        )
    index_tile_deletion_by_transaction(transaction_id)

    with transaction.atomic():
        # cast tileinstanceid to UUID
        tile_edit_changes = tile_edit_changes.annotate(
            tileinstanceid_uuid=Func(F("tileinstanceid"), function="UUID")
        )

        for tile in Tile.objects.filter(
            tileid__in=tile_edit_changes.values_list("tileinstanceid_uuid", flat=True)
        ).iterator(chunk_size=2000):
            tile.data = tile_edit_changes.get(tileinstanceid=str(tile.tileid)).oldvalue
            tile.save(
                index=False,
                recalculate_descriptors=False,
                transaction_id=revserse_operation_transactionid,
                user=user,
            )
    if tile_edit_changes.count() > 0:
        index_resources_by_transaction(
            transaction_id,
            recalculate_descriptors=True,
        )

    return number_of_db_changes


def delete_manifests(transaction_id):
    number_of_db_changes = 0
    try:
        with transaction.atomic():
            transaction_changes = IIIFManifest.objects.filter(
                transactionid=transaction_id
            )
            for obj in transaction_changes:
                obj.delete()
                number_of_db_changes += 1
    except DatabaseError:
        logger.error("Error connecting to database")

    return number_of_db_changes


def delete_workflow_histories(transaction_id):
    number_of_db_changes = 0
    with transaction.atomic():
        # Should have already checked that the user created the transaction.
        qs = WorkflowHistory.objects.filter(workflowid=transaction_id)
        number_of_db_changes = qs.count()
        qs.delete()

    return number_of_db_changes
