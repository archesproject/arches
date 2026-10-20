import logging
from arches.app.models.resource import Resource
from celery import shared_task


@shared_task
def index_resource(resource_id):
    logger = logging.getLogger(__name__)
    try:
        resource = Resource.objects.filter(pk=resource_id).get()
        resource.index()
    except Resource.DoesNotExist:
        logger.error(f"Resource with id {resource_id} does not exist.")
    except Exception as e:
        logger.error(f"Error indexing resource {resource_id}: {e}")
