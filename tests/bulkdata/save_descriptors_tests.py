import uuid
from unittest.mock import patch

from django.contrib.auth.models import User

from arches.app.etl_modules.save import _post_save_edit_log, settings
from arches.app.models import models
from arches.app.models.resource import Resource
from tests.base_test import ArchesTestCase
from tests.commands.test_resources import (
    _make_descriptor_graph,
    _save_resource_with_tile,
)

# these tests can be run from the command line via
# python manage.py test tests.bulkdata.save_descriptors_tests --settings="tests.test_settings"


class PostSaveEditLogDescriptorsTests(ArchesTestCase):
    def setUp(self):
        graph, node_group, string_node = _make_descriptor_graph("Save Descriptors")
        self.resource = _save_resource_with_tile(graph, node_group, string_node)
        self.loadid = uuid.uuid4()
        self.userid = User.objects.get(username="admin").pk
        models.EditLog.objects.create(
            resourceinstanceid=str(self.resource.pk),
            resourceclassid=str(graph.pk),
            transactionid=self.loadid,
            edittype="update",
        )
        Resource.objects.filter(pk=self.resource.pk).update(descriptors={}, name={})

    def descriptors(self):
        return Resource.objects.get(pk=self.resource.pk).descriptors

    @patch.object(settings, "ELASTICSEARCH_ENABLED", False)
    def test_descriptors_recalculated_when_es_disabled(self):
        with patch("arches.app.etl_modules.save.index_resources_by_transaction") as m:
            result = _post_save_edit_log(self.userid, self.loadid, index=True)
        m.assert_not_called()
        self.assertTrue(result["success"])
        self.assertEqual(result["data"], "completed")
        self.assertEqual(self.descriptors().get("en", {}).get("name"), "test value")

    @patch.object(settings, "ELASTICSEARCH_ENABLED", False)
    def test_descriptors_not_recalculated_when_index_false(self):
        result = _post_save_edit_log(self.userid, self.loadid, index=False)
        self.assertTrue(result["success"])
        self.assertEqual(self.descriptors(), {})

    @patch.object(settings, "ELASTICSEARCH_ENABLED", True)
    def test_es_enabled_indexes_with_descriptor_recalculation(self):
        with patch("arches.app.etl_modules.save.index_resources_by_transaction") as m:
            result = _post_save_edit_log(self.userid, self.loadid, index=True)
        m.assert_called_once()
        self.assertTrue(m.call_args.kwargs["recalculate_descriptors"])
        self.assertEqual(result["data"], "indexed")
