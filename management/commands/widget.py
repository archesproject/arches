from arches.management.commands.widget import Command as WidgetCommand
from arches_component_lab.utils.widget_synchronizer import WidgetSynchronizer


class Command(WidgetCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            "-wn",
            "--widget_name",
            action="store",
            dest="widget_name",
            default="",
            help="The name of the widget",
        )

        parser.add_argument(
            "-cn",
            "--component_name",
            action="store",
            dest="component_name",
            default="",
            help="The name of the Vue component to be used in the mapping",
        )

    def handle(self, *args, **options):
        super().handle(*args, **options)

        if options["operation"] == "sync_mappings":
            self.synchronize_mapping(
                widget_name=options["widget_name"],
                component_name=options["component_name"],
            )

    def synchronize_mapping(self, widget_name, component_name):
        WidgetSynchronizer().synchronize_widgets(
            widget_name=widget_name, component_name=component_name
        )
