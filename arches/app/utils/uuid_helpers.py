import uuid

# Move to util function
def uuid_get_or_create(id):
    try:
        uuid.UUID(id)
        return uuid.UUID(id), False
    except (ValueError, TypeError):
        return uuid.uuid4(), True
