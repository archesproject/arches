import uuid

from django.db import models

from arches import __version__ as _arches_version_str
from packaging.version import Version

arches_version = Version(_arches_version_str)
from arches.app.models.models import Node, ResourceInstance

from arches.extensions.querysets.datatypes.datatypes import (
    DataTypeFactory,
    ResourceInstanceDataType,
)
from arches.extensions.querysets.utils.permissions import (
    filter_readable_resources,
    resource_read_permissions_apply,
)


def get_nodegroup_alias_lookup(graph_slug):
    filters = models.Q(pk=models.F("nodegroup_id"), graph__slug=graph_slug)
    # arches_version==9.0.0
    if arches_version >= Version("8.0"):
        filters &= models.Q(source_identifier=None)
    return {node.pk: node.alias for node in Node.objects.filter(filters).only("alias")}


def redact_unreadable_related_resources(data, *, user, graph_nodes):
    if not resource_read_permissions_apply(user):
        return

    node_values_by_alias = list(_find_node_values(data))
    if not node_values_by_alias:
        return

    resource_instance_nodes = {
        node.alias: node
        for node in graph_nodes
        if isinstance(
            DataTypeFactory().get_instance(node.datatype), ResourceInstanceDataType
        )
    }
    node_values = [
        (resource_instance_nodes[alias], node_value)
        for alias, node_value in node_values_by_alias
        if alias in resource_instance_nodes
    ]
    related_resource_ids = {
        detail["resource_id"]
        for _node, node_value in node_values
        for detail in node_value["details"]
        if detail["resource_id"]
    }
    if not related_resource_ids:
        return

    related_resources = ResourceInstance.objects.filter(pk__in=related_resource_ids)
    unreadable_resource_ids = set(
        related_resources.exclude(
            pk__in=filter_readable_resources(user, related_resources).values("pk")
        ).values_list("pk", flat=True)
    )
    if not unreadable_resource_ids:
        return

    for node, node_value in node_values:
        node_value["details"] = [
            detail
            for detail in node_value["details"]
            if not detail["resource_id"]
            or uuid.UUID(detail["resource_id"]) not in unreadable_resource_ids
        ]
        node_value["display_value"] = (
            DataTypeFactory()
            .get_instance(node.datatype)
            .get_display_value(None, node, details=node_value["details"])
        )


def _find_node_values(data):
    if isinstance(data, list):
        for item in data:
            yield from _find_node_values(item)
    elif isinstance(data, dict):
        if "results" in data:
            yield from _find_node_values(data["results"])
        for alias, value in data.get("aliased_data", {}).items():
            if isinstance(value, dict) and "details" in value:
                yield alias, value
            else:
                yield from _find_node_values(value)
