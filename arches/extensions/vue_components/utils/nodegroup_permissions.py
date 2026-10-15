from arches.app.models.models import NodeGroup
from arches.app.utils.permission_backend import get_nodegroups_by_perm


def nodegroup_ids_with_inherited_permission(user, permission):
    permitted_nodegroup_ids = set(get_nodegroups_by_perm(user, permission))
    parent_nodegroup_ids_by_id = dict(
        NodeGroup.objects.values_list("pk", "parentnodegroup_id")
    )

    def is_permitted_with_ancestors(nodegroup_id):
        while nodegroup_id is not None:
            if nodegroup_id not in permitted_nodegroup_ids:
                return False
            nodegroup_id = parent_nodegroup_ids_by_id.get(nodegroup_id)
        return True

    return {
        nodegroup_id
        for nodegroup_id in permitted_nodegroup_ids
        if is_permitted_with_ancestors(nodegroup_id)
    }
