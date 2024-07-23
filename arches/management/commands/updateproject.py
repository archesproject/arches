from django.core.management.base import BaseCommand

from arches.app.search.mappings import (
    prepare_search_index,
)


class Command(BaseCommand):  # pragma: no cover
    """
    Command for migrating projects between versions

    """

    def handle(self, *args, **options):
        answer = input("This operation currently does nothing.\n" "Continue? ")

        if answer.lower() in ["y", "yes"]:
            self.update_to_v8()
        else:
            self.stdout.write("Operation aborted.")

    def update_to_v8(self):
        prepare_search_index()
