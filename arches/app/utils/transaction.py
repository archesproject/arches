import logging
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.models.models import IIIFManifest, EditLog, WorkflowHistory
from django.db import transaction, DatabaseError

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Given a transaction ID, reverse (delete or update) tiles and resources created/updated during the transaction
def reverse_edit_log_entries(transaction_id):
    transaction_changes = (
        EditLog.objects.filter(transactionid=transaction_id)
        .order_by("-timestamp")
        .all()
    )
    number_of_db_changes = 0
    try:
        with transaction.atomic():
            for edit_log in transaction_changes:
                if edit_log.edittype == "create":
                    for obj in Resource.objects.filter(
                        resourceinstanceid=edit_log.resourceinstanceid
                    ):
                        obj.delete()
                        number_of_db_changes += 1
                elif edit_log.edittype == "tile create":
                    for obj in Tile.objects.filter(tileid=edit_log.tileinstanceid):
                        obj.delete()
                        number_of_db_changes += 1
                elif edit_log.edittype == "tile edit":
                    for obj in Tile.objects.filter(tileid=edit_log.tileinstanceid):
                        obj.data = edit_log.oldvalue
                        obj.save()
                        number_of_db_changes += 1
    except DatabaseError:
        logger.error("Error connecting to database")

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
