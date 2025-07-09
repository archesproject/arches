from django.core.management.base import BaseCommand
from django.db import transaction

from arches_querysets.utils.tests import GraphTestCase


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Creating test data...")
        with transaction.atomic():
            GraphTestCase.setUpTestData()
        self.stdout.write("Finished!")
