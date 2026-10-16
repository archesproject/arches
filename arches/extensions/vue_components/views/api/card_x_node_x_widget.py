from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.views.generic import View

from arches.app.models import models
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.extensions.vue_components.utils.widget_configs import (
    serialize_graph_widget_configs,
    serialize_node_widget_config,
    serialize_nodegroup_widget_configs,
)


def nodegroup_permission_error_response():
    return JSONErrorResponse(
        message=_("You do not have permission to read this nodegroup."),
        status=403,
    )


def widget_mapping_error_response():
    return JSONErrorResponse(
        message=_("Database error occurred while fetching widget mapping."),
        status=503,
    )


class CardXNodeXWidgetView(View):
    def get(self, request, graph_slug, node_alias):
        node = models.Node.objects.get(
            graph__slug=graph_slug, alias=node_alias, source_identifier=None
        )
        if node.nodegroup_id not in get_nodegroups_by_perm(
            request.user, "models.read_nodegroup"
        ):
            return nodegroup_permission_error_response()

        try:
            widget_config = serialize_node_widget_config(node)
        except ObjectDoesNotExist:
            return widget_mapping_error_response()
        if widget_config is None:
            return JSONErrorResponse(
                message=_("No widget is configured for this node."),
                status=404,
            )
        return JSONResponse(widget_config)


class CardXNodeXWidgetListFromNodegroupView(View):
    def get(self, request, graph_slug, nodegroup_alias):
        nodes = list(
            models.Node.objects.filter(
                graph__slug=graph_slug,
                nodegroup__node__alias=nodegroup_alias,
                source_identifier=None,
            )
        )
        if nodes and nodes[0].nodegroup_id not in get_nodegroups_by_perm(
            request.user, "models.read_nodegroup"
        ):
            return nodegroup_permission_error_response()

        try:
            widget_configs = serialize_nodegroup_widget_configs(nodes)
        except ObjectDoesNotExist:
            return widget_mapping_error_response()
        return JSONResponse(widget_configs)


class CardXNodeXWidgetListFromGraphView(View):
    def get(self, request, graph_slug):
        try:
            widget_configs = serialize_graph_widget_configs(
                graph_slug,
                readable_nodegroup_ids=set(
                    get_nodegroups_by_perm(request.user, "models.read_nodegroup")
                ),
                writable_nodegroup_ids=set(
                    get_nodegroups_by_perm(request.user, "models.write_nodegroup")
                ),
            )
        except ObjectDoesNotExist:
            return widget_mapping_error_response()
        return JSONResponse(widget_configs)
