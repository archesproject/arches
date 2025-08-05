from django.db import models

from arches.app.models.models import Widget


class WidgetMapping(models.Model):
    id = models.UUIDField(primary_key=True)
    widget = models.OneToOneField(
        Widget,
        on_delete=models.CASCADE,
    )
    component = models.CharField(max_length=255, unique=True)

    def __str__(self):
        widget_name = self.widget.name if self.widget else "<no widget>"
        return f"{widget_name} → {self.component}"
