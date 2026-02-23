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
        self, widget_name: str, component_path: str = None, component_name: str = None
    ) -> None:
        widget = Widget.objects.filter(name=widget_name).first()
        if not widget:
            sys.stdout.write(_(f"No widget found with the name '{widget_name}'.\n"))
            return

        if widget_name == "language-widget" and not component_path:
            component_path = "arches_component_lab/widgets/LanguageSelectWidget/LanguageSelectWidget.vue"

        component = None
        if component_path:
            component = component_path
        else:
            if not component_name:
                # Provide a reasonable default mapping based on widget name
                component_name = (
                    widget.name.title()
                    .replace(" ", "")
                    .replace("-", "")
                    .replace("_", "")
                )
            component = (
                f"arches_component_lab/widgets/{component_name}/{component_name}.vue"
            )

        mapping = WidgetMapping.objects.create(
            widget=widget,
            component=component,
        )
        return mapping
