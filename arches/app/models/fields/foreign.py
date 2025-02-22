from django.db import models
from django.db.models.fields.related import ForwardManyToOneDescriptor


class GhostableForwardDescriptor(ForwardManyToOneDescriptor):
    def get_object(self, instance):
        qs = self.get_queryset(instance=instance)
        return qs.filter(self.field.get_reverse_related_filter(instance)).first()


class GhostableForeignObject(models.ForeignObject):
    """Make missing related objects return None rather than raise."""

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)
        setattr(cls, self.name, GhostableForwardDescriptor(self))
