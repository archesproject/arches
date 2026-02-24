import sys
import uuid

from django.db.models import QuerySet
from django.utils.translation import gettext as _

from arches.app.models.models import Widget
from arches_component_lab.models import WidgetMapping


class WidgetSynchronizer:
    def check_for_missing_mappings(
        self, return_as_queryset=False
    ) -> set[uuid.UUID] | QuerySet:
        widgets_without_mapping = Widget.objects.exclude(
            widgetid__in=WidgetMapping.objects.values_list("widget_id", flat=True)
        )
        if return_as_queryset:
            return widgets_without_mapping
        return set(widgets_without_mapping.values_list("widgetid", flat=True))

    def add_mapping(
        self, widget_name: str, component_path: str = None
    ) -> WidgetMapping | None:
        widget = Widget.objects.filter(name=widget_name).first()
        if not widget:
            raise ValueError(_(f"No widget found with the name '{widget_name}'."))

        if not component_path:
            raise ValueError(
                _("A component path must be provided to create a widget mapping.")
            )

        mapping = WidgetMapping.objects.create(
            widget=widget,
            component=component_path,
        )
        return mapping
