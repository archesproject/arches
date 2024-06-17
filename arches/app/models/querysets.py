from django.contrib.postgres.expressions import ArraySubquery
from django.db import models
from django.db.models.fields.json import KT
from django.db.models.functions import Cast


class NodeQuerySet(models.QuerySet):
    def with_controlled_lists(self):
        """Annotates a queryset with an indexed lookup on controlled lists, e.g.:
        Node.objects.with_controlled_lists().filter(
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


class ControlledListQuerySet(models.QuerySet):
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
