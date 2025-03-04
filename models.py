from arches.app.models.models import ResourceInstance, TileModel

from arches_querysets.querysets import ResourceInstanceQuerySet, TileQuerySet


class SemanticResource(ResourceInstance):
    objects = ResourceInstanceQuerySet.as_manager()

    class Meta:
        proxy = True
        db_table = "resource_instances"
        permissions = (("no_access_to_resourceinstance", "No Access"),)


class SemanticTile(TileModel):
    objects = TileQuerySet.as_manager()

    class Meta:
        proxy = True
        db_table = "tiles"
