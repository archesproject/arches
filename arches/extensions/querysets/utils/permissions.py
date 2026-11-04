from django.db.models import Exists, OuterRef

from arches.app.models.models import Node
from arches.app.models.system_settings import settings
from arches.app.utils import permission_backend

DEFAULT_ALLOW_PERMISSION_FRAMEWORK = (
    "arches_default_allow.ArchesDefaultAllowPermissionFramework"
)


def resource_read_permissions_apply(user):
    return (
        not user.is_superuser
        and settings.PERMISSION_FRAMEWORK != DEFAULT_ALLOW_PERMISSION_FRAMEWORK
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
