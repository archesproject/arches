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
            "-p",
            "--component_path",
            action="store",
            dest="component_path",
            default="",
            help="The path of the Vue component to be used in the mapping",
        )

    def handle(self, *args, **options):
        super().handle(*args, **options)

        if options["operation"] == "check_mappings":
            missing_mappings = WidgetSynchronizer().check_for_missing_mappings()
            if missing_mappings:
                self.stdout.write(
                    self.style.WARNING(
                        f"Widgets without mappings: {', '.join(str(id) for id in missing_mappings)}"
                    )
                )
            else:
                self.stdout.write(self.style.SUCCESS("All widgets have mappings."))

        elif options["operation"] == "add_mapping":
            widget_name = options["widget_name"]
            component_path = options["component_path"] or None
            mapping = WidgetSynchronizer().add_mapping(
                widget_name, component_path=component_path
            )
            if mapping:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created mapping for widget '{mapping.widget.name}' with component: '{mapping.component}'"
                    )
                )
