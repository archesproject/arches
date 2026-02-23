from enum import auto, Enum, StrEnum, unique

from django.core.management import CommandError

from arches.app.const import IntegrityCheck as BaseIntegrityCheck
from arches.management.commands.validate import Command as BaseValidateCommand
from arches.management.commands.validate import CommandModes
from arches.app.models.models import Widget

from arches_component_lab.utils.widget_synchronizer import WidgetSynchronizer

IntegrityCheckDescriptions = {
    2001: "Widgets without a mapping to a Component Lab Vue component",
}


@unique
class IntegrityCheck(Enum):
    """Quasi-subclass of Core Arches ValidateCommand's IntegrityCheck, specific to Component Lab."""

    MISSING_WIDGET_MAPPINGS = 2001

    def __str__(self):
        return IntegrityCheckDescriptions[self.value]


class FixActions(StrEnum):
    """Quasi-subclass of Core Arches ValidateCommand's FixActions, specific to Component Lab."""

    CREATE_WIDGET_MAPPINGS = auto()


class Command(BaseValidateCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)

        base_choices = [check.value for check in BaseIntegrityCheck]
        choices = base_choices + [check.value for check in IntegrityCheck]
        for action in parser._actions:
            if "--fix" in action.option_strings:
                action.choices = choices
            elif "--codes" in action.option_strings:
                action.choices = choices

    def handle(self, *args, **options):
        super().handle(*args, **options)

        self.check_integrity(
            check=IntegrityCheck.MISSING_WIDGET_MAPPINGS,
            queryset=WidgetSynchronizer().check_for_missing_mappings(
                return_as_queryset=True
            ),
            fix_action=FixActions.CREATE_WIDGET_MAPPINGS,
        )

    def check_integrity(self, check, queryset, fix_action):
        """
        TODO: remove with Core Arches v8.2. Arches Apps should be able to subclass
        a base IntegrityCheck and FixActions, and the validate command should be able to
        handle those app-specific checks and fixes without needing to override the entire
        check_integrity method.
        """

        # 500 not set as a default earlier:
        # None distinguishes whether verbose output implied.
        limit = self.options["limit"] or 500

        if self.mode == CommandModes.VALIDATE:
            if self.options["codes"] and check.value not in self.options["codes"]:
                # User didn't request this specific check.
                return
            # Fixable?
            fix_status = (
                self.style.MIGRATE_HEADING("Yes")
                if fix_action
                else self.style.NOTICE("No")
            )
            if not queryset.exists():
                fix_status = self.style.MIGRATE_HEADING("N/A")
        else:
            if not self.options["fix_all"] and check.value not in self.options["fix"]:
                # User didn't request this specific check.
                return

            # Fixed?
            if fix_action is None:
                if self.options["fix_all"]:
                    fix_status = self.style.MIGRATE_HEADING("N/A")
                else:
                    raise CommandError(
                        f"Requested fixing unfixable - {check.value}: {check}"
                    )
            elif queryset.exists():
                fix_status = self.style.ERROR("No")  # until actually fixed below

                ##### Component Lab Specific Fix Logic
                if fix_action == FixActions.CREATE_WIDGET_MAPPINGS:
                    synchronizer = WidgetSynchronizer()
                    mappings = []
                    for widget in queryset:
                        mappings.append(synchronizer.add_mapping(widget.name))

                    if len(mappings):
                        fix_status = self.style.SUCCESS("Yes")
                #####

                else:
                    raise NotImplementedError

        # Print the report (after any requested fixes are made)
        if self.options["verbosity"] > 0:
            # len() works if the FixAction didn't inadvertently evaluate the qs.
            count = len(queryset)
            result = self.style.ERROR("FAIL") if count else self.style.SUCCESS("PASS")
            # Fix status takes two "columns" so add a tab
            self.stdout.write(
                "\t".join(
                    str(x)
                    for x in (result, check.value, count, fix_status + "\t", check)
                )
            )

            if self.options["verbosity"] > 1:
                self.stdout.write("\t" + "-" * 36)
                if queryset:
                    for i, n in enumerate(queryset):
                        if i < limit:
                            self.stdout.write(f"\t{n}")
                        else:
                            self.stdout.write("\t\t(truncated...)")
                            break

            self.stdout.write()
