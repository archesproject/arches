import uuid

from arches.app.utils.decorators import deprecated


# Move to util function
@deprecated
def uuid_get_or_create(id):
    try:
        uuid.UUID(id)
        return uuid.UUID(id), False
    except (ValueError, TypeError):
        return uuid.uuid4(), True
