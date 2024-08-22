import json
from arches.app.utils.betterJSONSerializer import JSONSerializer
from django.contrib.auth.models import User, Group


def sync_es(search_engine, index="test_resources"):
    search_engine.es.indices.refresh(index=index)


def get_response_json(client, **kwargs):
    query = kwargs.pop("query", {})
    for filter_name, filter_value in kwargs.items():
        query[filter_name.replace("_", "-")] = JSONSerializer().serialize(filter_value)

    resource_reviewer_group = Group.objects.get(name="Resource Reviewer")
    test_user = User.objects.get(username="unpriviliged_user")
    test_user.groups.add(resource_reviewer_group)
    client.login(username="unpriviliged_user", password="test")
    response = client.get("/search/resources", query)
    response_json = json.loads(response.content)
    return response_json
