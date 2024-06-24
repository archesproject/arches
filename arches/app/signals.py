from django.db.models.signals import post_save
from django.dispatch import receiver

from arches.app.models import models
from arches.app.models.graph import Graph


@receiver(post_save, sender=models.GraphModel)
@receiver(post_save, sender=Graph)
def create_resource_instance_lifecycle(sender, instance, created, **kwargs):
    if (
        created
        and not instance.source_identifier_id
        and not instance.resource_instance_lifecycle
    ):
        lifecycle_state = models.ResourceInstanceLifecycle.objects.create(
            graph=instance
        )
        instance.resource_instance_lifecycle = lifecycle_state
        instance.save()
