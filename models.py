from django.db import models

from arches.app.models.models import Widget


class WidgetMapping(models.Model):
    id = models.UUIDField(primary_key=True)
    widget = models.ForeignKey(
        Widget,
        on_delete=models.CASCADE,
    )
    component = models.TextField(unique=True)

    def __str__(self):
        return f"{self.widget.name} → {self.component}"

    class Meta:
        managed = True
        db_table = "widget_mappings"
