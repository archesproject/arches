from arches.app.utils.resource_relationship_utils import (
    get_resource_relationship_type_label,
)
from django.test import TestCase
import uuid

# these tests can be run from the command line via
# python manage.py test tests.utils.test_resource_relationship_utils --settings="tests.test_settings"


class ResourceRelationshipUtilsTests(TestCase):

    def test_get_resource_relationship_type_label(self):
        is_related_to = uuid.UUID("ac41d9be-79db-4256-b368-2f4559cfbe55")
        labels = get_resource_relationship_type_label({is_related_to})
        with self.subTest(labels=labels):
            self.assertEqual(labels[str(is_related_to)], "is related to")
