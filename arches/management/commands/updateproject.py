from django.core.management.base import BaseCommand
from django.core import management


class Command(BaseCommand):
    """
    Command for migrating projects between versions

    """

    def handle(self, *args, **options):
        self.update_to_v7_5()

    def update_to_v7_5(self):
        management.call_command("graph", operation="publish")
