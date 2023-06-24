from django.db.models.signals import post_delete, pre_save, post_save
from arches.app.utils.permission_backend import GroupObjectPermission, assign_perm

from arches.app.models.models import User, ContentType, ResourceInstance

@receiver(post_save, sender=User)
def create_permissions_for_new_users(sender, instance, created, **kwargs):
    from arches.app.models.resource import Resource

    if created:
        ct = ContentType.objects.get(app_label="models", model="resourceinstance")
        resourceInstanceIds = list(GroupObjectPermission.objects.filter(content_type=ct).values_list("object_pk", flat=True).distinct())
        for resourceInstanceId in resourceInstanceIds:
            resourceInstanceId = uuid.UUID(resourceInstanceId)
        resources = ResourceInstance.objects.filter(pk__in=resourceInstanceIds)
        assign_perm("no_access_to_resourceinstance", instance, resources)
        for resource_instance in resources:
            resource = Resource(resource_instance.resourceinstanceid)
            resource.graph_id = resource_instance.graph_id
            resource.createdtime = resource_instance.createdtime
            resource.index()

