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
