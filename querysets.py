from django.contrib.postgres.expressions import ArraySubquery
from django.db import models
from django.db.models.fields.json import KT
from django.db.models.functions import Cast


class ListQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        for obj in self:
            obj.delete_index()
        return super(ListQuerySet, self).delete(*args, **kwargs)

    def annotate_node_fields(self, **kwargs):
        from arches_controlled_lists.models import NodeProxy

        qs = self
        for annotation_name, node_field in kwargs.items():
            subquery = ArraySubquery(
                NodeProxy.objects.with_controlled_lists()
                .filter(
                    controlled_list_id=models.OuterRef("id"), source_identifier=None
                )
                .select_related("graph" if node_field.startswith("graph__") else None)
                .order_by("pk")
                .values(node_field)
            )
            qs = qs.annotate(**{annotation_name: subquery})

        return qs


class ListItemQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        for obj in self:
            obj.delete_index()
        return super(ListItemQuerySet, self).delete(*args, **kwargs)

    def with_list_item_labels(self):
        from arches_controlled_lists.models import ListItemValue

        return self.prefetch_related(
            models.Prefetch(
                "list_item_values",
                ListItemValue.objects.labels(),
                to_attr="list_item_labels",
            )
        )


class ListItemValueQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        for obj in self:
            obj.delete_index()
        return super(ListItemValueQuerySet, self).delete(*args, **kwargs)

    def values_without_images(self):
        return self.exclude(valuetype="image")

    def labels(self):
        return self.filter(valuetype__category="label")

    def images(self):
        return self.filter(valuetype="image")


class ListItemImageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(valuetype="image")


class NodeQuerySet(models.QuerySet):
    def with_controlled_lists(self):
        """Annotates a queryset with an indexed lookup on controlled lists, e.g.:
        NodeProxy.objects.with_controlled_lists().filter(
            controlled_list_id=your_list_id_as_uuid,
            source_identifier=None,
        )
        """
        return self.annotate(
            controlled_list_id=Cast(
                KT("config__controlledList"),
                output_field=models.UUIDField(),
            )
        )
