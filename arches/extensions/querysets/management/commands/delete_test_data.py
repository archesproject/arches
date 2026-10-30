from django.core.management.base import BaseCommand
from django.db import transaction

from arches.app.models import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Deleting test data...")
        with transaction.atomic():
            models.ResourceInstance.objects.filter(
                graph__slug="datatype_lookups"
            ).delete()
            models.GraphModel.objects.filter(slug="datatype_lookups").delete()
        self.stdout.write("Finished!")
