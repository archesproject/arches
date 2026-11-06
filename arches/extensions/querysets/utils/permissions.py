from django.db.models import Exists, OuterRef

from arches.app.models.models import Node
from arches.app.permissions.arches_default_allow import (
    ArchesDefaultAllowPermissionFramework,
)
from arches.app.utils import permission_backend


def resource_read_permissions_apply(user):
    # Default allow is deprecated (arches.W003) with no queryset filter (arches.E004).
    return not user.is_superuser and not isinstance(
        permission_backend._get_permission_framework(),
        ArchesDefaultAllowPermissionFramework,
    )


def filter_readable_resources(
    user,
    queryset,
    *,
    resourceinstance_field="resourceinstanceid",
    graph_field="graph_id",
):
    if not resource_read_permissions_apply(user):
        return queryset

    readable_queryset = permission_backend.filter_resource_queryset(
        user, queryset, resourceinstance_field=resourceinstance_field
    )
    return readable_queryset.filter(
        Exists(
            Node.objects.filter(
                graph_id=OuterRef(graph_field),
                nodegroup_id__in=user.userprofile.viewable_nodegroups,
            )
        )
    )
