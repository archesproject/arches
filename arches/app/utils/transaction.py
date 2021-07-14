from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.models.models import EditLog
from django.db import DatabaseError


# Given a transaction ID, reverse (delete or update) tiles and resources created/updated during the transaction
def reverse_edit_log_entries(transaction_id):
    transaction_changes = EditLog.objects.filter(transactionid=transaction_id).order_by("-timestamp").all()
    number_of_db_changes = 0
    try:
        for edit_log in transaction_changes:
            if edit_log.edittype == "create":
                number_of_db_changes += Resource.objects.filter(resourceinstanceid=edit_log.resourceinstanceid).delete()[0]
            elif edit_log.edittype == "tile create":
                number_of_db_changes += Tile.objects.filter(tileid=edit_log.tileinstanceid).delete()[0]
            elif edit_log.edittype == "tile edit":
                number_of_db_changes += Tile.objects.filter(tileid=edit_log.tileinstanceid).update(data=edit_log.oldvalue)
    except DatabaseError:
        print("Error connecting to database")

    return number_of_db_changes
