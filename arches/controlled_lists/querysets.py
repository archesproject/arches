from django.contrib.postgres.expressions import ArraySubquery
from django.db import models


class ListQuerySet(models.QuerySet):
    def annotate_node_fields(self, **kwargs):
        from arches.app.models.models import Node

        qs = self
        for annotation_name, node_field in kwargs.items():
            subquery = ArraySubquery(
                Node.objects.with_controlled_lists()
                .filter(
                    controlled_list_id=models.OuterRef("id"),
                    source_identifier=None,
                )
                .select_related("graph" if node_field.startswith("graph__") else None)
                .order_by("pk")
                .values(node_field)
            )
            qs = qs.annotate(**{annotation_name: subquery})

        return qs


class ListItemValueQuerySet(models.QuerySet):
    def values_without_images(self):
        return self.exclude(valuetype="image")

    def images(self):
        return self.filter(valuetype="image")


class ListItemImageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(valuetype="image")
