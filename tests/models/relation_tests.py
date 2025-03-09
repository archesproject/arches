from django.db import IntegrityError

from arches.app.models.models import Relation
from tests.base_test import ArchesTestCase


class RelationTests(ArchesTestCase):
    def test_bidirectional_duplicate_check(self):
        relation = Relation.objects.first()
        duplicate = Relation(
            conceptfrom_id=relation.conceptto_id,
            conceptto_id=relation.conceptfrom_id,
            relationtype=relation.relationtype,
        )
        with self.assertRaises(IntegrityError):
            duplicate.save()
