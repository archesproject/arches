import json
from django.conf import settings
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.utils.betterJSONSerializer import JSONSerializer
from django.contrib.auth.models import User, Group


def sync_es(search_engine, index=None):
    if index is None:
        index = f"{settings.ELASTICSEARCH_PREFIX}_{RESOURCES_INDEX}"
    search_engine.es.indices.refresh(index=index)


def get_response_json(client, query={}):
    for filter_type, query_string in list(query.items()):
        if not isinstance(query_string, str):
            query_json_string = JSONSerializer().serialize(query_string)
            query[filter_type] = query_json_string
    resource_reviewer_group = Group.objects.get(name="Resource Reviewer")
    test_user = User.objects.get(username="unpriviliged_user")
    test_user.groups.add(resource_reviewer_group)
    client.login(username="unpriviliged_user", password="test")
    response = client.get("/search/resources", query)
    response_json = json.loads(response.content)
    return response_json
