from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query
from arches.app.search.mappings import TERMS_INDEX, RESOURCES_INDEX
from django.db import connection


def clear_resources():
    """Removes all resource instances from your db and elasticsearch resource index"""
    se = SearchEngineFactory().create()
    match_all_query = Query(se)
    match_all_query.delete(index=TERMS_INDEX)
    match_all_query.delete(index=RESOURCES_INDEX)

    print(
        "deleting",
        Resource.objects.exclude(
            resourceinstanceid=settings.RESOURCE_INSTANCE_ID
        ).count(),
        "resources",
    )
    Resource.objects.exclude(resourceinstanceid=settings.RESOURCE_INSTANCE_ID).delete()
    print(
        Resource.objects.exclude(
            resourceinstanceid=settings.RESOURCE_INSTANCE_ID
        ).count(),
        "resources remaining",
    )

    print(
        "deleting", models.ResourceXResource.objects.count(), "resource relationships"
    )
    cursor = connection.cursor()
    cursor.execute("TRUNCATE public.resource_x_resource CASCADE;")
    print(models.ResourceXResource.objects.count(), "resource relationships remaining")
