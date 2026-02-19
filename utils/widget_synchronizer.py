import sys

from django.utils.translation import gettext as _

from arches.app.models.models import Widget
from arches_component_lab.models import WidgetMapping


class WidgetSynchronizer:
    def synchronize_widgets(self, widget_name: str = None, component_name: str = None):
        """Ensure that all widgets in the Arches database have a corresponding WidgetMapping."""
        widgets = Widget.objects.all()
        mappings = WidgetMapping.objects.all()
        missing_mappings = set(widgets.values_list("widgetid", flat=True)) - set(
            mappings.values_list("widget_id", flat=True)
        )

        if len(missing_mappings) > 1 and not widget_name:
            raise ValueError(
                _(
                    "Multiple widgets are missing mappings. "
                    "Please specify a widget_name and optional component_name to create "
                    "a mapping for a specific widget."
                )
            )

        for widget_pk in missing_mappings:
            widget = Widget.objects.get(widgetid=widget_pk)
            if not component_name:
                # Provide a reasonable default mapping based on widget name
                component_name = (
                    widget.name.title()
                    .replace(" ", "")
                    .replace("-", "")
                    .replace("_", "")
                )

            if widget.name == widget_name:
                WidgetMapping.objects.create(
                    widget=widget,
                    component=f"arches_component_lab/widgets/{component_name}/{component_name}.vue",
                )
                return

            elif not widget_name:
                WidgetMapping.objects.create(
                    widget=widget,
                    component=f"arches_component_lab/widgets/{component_name}/{component_name}.vue",
                )
            sys.stdout.write(
                _(
                    f"Created mapping for widget '{widget.name}' with component '{component_name}.vue'\n"
                )
            )
