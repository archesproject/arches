import uuid
from unittest.mock import MagicMock, patch

from django.db import connection
from django.test import TestCase

from arches.app.const import DefaultLifecycleStates
from arches.app.etl_modules.staging_to_tile import (
    _build_tile_data,
    _post_process_staging,
    staging_to_tile,
)
from arches.app.models.models import (
    EditLog,
    LoadEvent,
    LoadStaging,
    ResourceInstance,
    TileModel,
)
from tests.base_test import ArchesTestCase
from tests.constants import AllDatatypesTestGraph

# these tests can be run from the command line via
# python manage.py test tests.bulkdata.staging_to_tile_tests --settings="tests.test_settings"


class BuildTileDataTests(TestCase):
    """Tests for _build_tile_data."""

    def test_none_value_returns_empty_dict(self):
        self.assertEqual(_build_tile_data(None), {})

    def test_empty_dict_returns_empty_dict(self):
        self.assertEqual(_build_tile_data({}), {})

    def test_non_dict_leaf_value_passed_through(self):
        result = _build_tile_data({"node-1": "plain string"})
        self.assertEqual(result, {"node-1": "plain string"})

    def test_dict_value_extracts_value_key(self):
        staged = {"node-1": {"value": "hello", "datatype": "string"}}
        self.assertEqual(_build_tile_data(staged), {"node-1": "hello"})

    def test_null_inner_value_preserved(self):
        staged = {"node-1": {"value": None, "datatype": "string"}}
        self.assertIsNone(_build_tile_data(staged)["node-1"])

    def test_resource_instance_list_adds_rxr_id(self):
        item = {"resourceId": "abc", "ontologyProperty": ""}
        staged = {"node-1": {"value": [item], "datatype": "resource-instance-list"}}
        result = _build_tile_data(staged)
        self.assertEqual(len(result["node-1"]), 1)
        self.assertIn("resourceXresourceId", result["node-1"][0])

    def test_resource_instance_adds_rxr_id(self):
        item = {"resourceId": "abc"}
        staged = {"node-1": {"value": [item], "datatype": "resource-instance"}}
        result = _build_tile_data(staged)
        self.assertIn("resourceXresourceId", result["node-1"][0])

    def test_resource_instance_list_does_not_mutate_input(self):
        item = {"resourceId": "abc"}
        staged = {"node-1": {"value": [item], "datatype": "resource-instance-list"}}
        _build_tile_data(staged)
        self.assertNotIn("resourceXresourceId", item)

    def test_resource_instance_list_non_list_value_returns_empty_list(self):
        staged = {
            "node-1": {"value": "not-a-list", "datatype": "resource-instance-list"}
        }
        self.assertEqual(_build_tile_data(staged)["node-1"], [])

    def test_resource_instance_null_value_returns_none(self):
        """When value is None, the `is not None` guard skips list processing."""
        staged = {"node-1": {"value": None, "datatype": "resource-instance"}}
        self.assertIsNone(_build_tile_data(staged)["node-1"])

    def test_multiple_nodes_processed_independently(self):
        staged = {
            "a": {"value": "foo", "datatype": "string"},
            "b": {"value": 42, "datatype": "number"},
            "c": "bare",
        }
        self.assertEqual(_build_tile_data(staged), {"a": "foo", "b": 42, "c": "bare"})


class StagingToTileTests(ArchesTestCase):
    """
    Integration tests for staging_to_tile().
    Uses ArchesTestCase (TestCase) so each test is wrapped in a rolled-back
    savepoint. Raw cursor calls to stored procedures are mocked out.
    """

    graph_fixtures = ["All_Datatypes"]

    ETL_MODULE_ID = "0a0cea7e-b59a-431a-93d8-e9f8c41bdd6b"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.load_id = uuid.uuid4()
        # LoadEvent requires ETLModule and User FKs that exist in fixtures,
        # so we use raw SQL (the established pattern for ETL tests).
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO load_event (loadid, complete, etl_module_id, user_id)"
                " VALUES (%s, FALSE, %s, 1)",
                [cls.load_id, cls.ETL_MODULE_ID],
            )
        cls.graph_id = AllDatatypesTestGraph.GRAPH_ID.value
        cls.nodegroup_id = AllDatatypesTestGraph.BOOLEAN_NODE_NODEGROUP.value
        cls.resource_id = uuid.uuid4()

    def _staging_record(self, **kwargs):
        """Create a LoadStaging record with sensible defaults."""
        defaults = dict(
            load_event_id=self.load_id,
            resourceid=self.resource_id,
            nodegroup_id=self.nodegroup_id,
            tileid=uuid.uuid4(),
            passes_validation=True,
            nodegroup_depth=1,
            operation="insert",
            value=None,
            sortorder=0,
        )
        defaults.update(kwargs)
        return LoadStaging.objects.create(**defaults)

    def _run(self):
        """Call staging_to_tile() with the stored-procedure cursor mocked."""
        with patch("arches.app.etl_modules.staging_to_tile.connection"):
            return staging_to_tile(self.load_id)

    def test_creates_resource_instance_for_new_resource_id(self):
        self._staging_record()
        self._run()
        self.assertTrue(
            ResourceInstance.objects.filter(
                resourceinstanceid=self.resource_id
            ).exists()
        )

    def test_does_not_create_duplicate_resource_instance(self):
        ResourceInstance.objects.create(
            resourceinstanceid=self.resource_id,
            graph_id=self.graph_id,
            resource_instance_lifecycle_state_id=DefaultLifecycleStates.PERPETUAL.value,
        )
        self._staging_record()
        self._run()
        self.assertEqual(
            ResourceInstance.objects.filter(
                resourceinstanceid=self.resource_id
            ).count(),
            1,
        )

    def test_edit_log_created_for_new_resource(self):
        self._staging_record()
        self._run()
        self.assertTrue(
            EditLog.objects.filter(
                resourceinstanceid=str(self.resource_id),
                edittype="create",
                transactionid=self.load_id,
            ).exists()
        )

    def test_no_resource_edit_log_for_existing_resource(self):
        ResourceInstance.objects.create(
            resourceinstanceid=self.resource_id,
            graph_id=self.graph_id,
            resource_instance_lifecycle_state_id=DefaultLifecycleStates.PERPETUAL.value,
        )
        self._staging_record()
        self._run()
        self.assertFalse(
            EditLog.objects.filter(
                resourceinstanceid=str(self.resource_id),
                edittype="create",
                transactionid=self.load_id,
            ).exists()
        )

    def test_invalid_records_are_skipped(self):
        tile_id = uuid.uuid4()
        self._staging_record(tileid=tile_id, passes_validation=False)
        self._run()
        self.assertFalse(TileModel.objects.filter(tileid=tile_id).exists())

    def test_tile_created_for_insert_operation(self):
        tile_id = uuid.uuid4()
        self._staging_record(
            tileid=tile_id,
            value={"node-1": {"value": "hello", "datatype": "string"}},
        )
        self._run()
        tile = TileModel.objects.filter(tileid=tile_id).first()
        self.assertIsNotNone(tile)
        self.assertEqual(tile.data["node-1"], "hello")

    def test_tile_create_edit_log_created(self):
        tile_id = uuid.uuid4()
        self._staging_record(tileid=tile_id)
        self._run()
        self.assertTrue(
            EditLog.objects.filter(
                tileinstanceid=str(tile_id),
                edittype="tile create",
                transactionid=self.load_id,
            ).exists()
        )

    def test_update_operation_updates_existing_tile(self):
        tile_id = uuid.uuid4()
        ResourceInstance.objects.create(
            resourceinstanceid=self.resource_id,
            graph_id=self.graph_id,
            resource_instance_lifecycle_state_id=DefaultLifecycleStates.PERPETUAL.value,
        )
        TileModel.objects.create(
            tileid=tile_id,
            nodegroup_id=self.nodegroup_id,
            resourceinstance_id=self.resource_id,
            data={"node-1": "old"},
        )
        self._staging_record(
            tileid=tile_id,
            operation="update",
            value={"node-1": {"value": "new", "datatype": "string"}},
        )
        self._run()
        self.assertEqual(TileModel.objects.get(tileid=tile_id).data["node-1"], "new")

    def test_tile_edit_log_created_for_update(self):
        tile_id = uuid.uuid4()
        ResourceInstance.objects.create(
            resourceinstanceid=self.resource_id,
            graph_id=self.graph_id,
            resource_instance_lifecycle_state_id=DefaultLifecycleStates.PERPETUAL.value,
        )
        TileModel.objects.create(
            tileid=tile_id,
            nodegroup_id=self.nodegroup_id,
            resourceinstance_id=self.resource_id,
            data={"node-1": "old"},
        )
        self._staging_record(
            tileid=tile_id,
            operation="update",
            value={"node-1": {"value": "new", "datatype": "string"}},
        )
        self._run()
        self.assertTrue(
            EditLog.objects.filter(
                tileinstanceid=str(tile_id),
                edittype="tile edit",
                transactionid=self.load_id,
            ).exists()
        )

    def test_update_on_nonexistent_tile_falls_back_to_insert(self):
        """A staged 'update' for a tile that doesn't exist should be inserted."""
        tile_id = uuid.uuid4()
        self._staging_record(tileid=tile_id, operation="update")
        self._run()
        self.assertTrue(TileModel.objects.filter(tileid=tile_id).exists())

    def test_load_event_marked_complete_and_successful(self):
        self._staging_record()
        result = self._run()
        self.assertTrue(result)
        event = LoadEvent.objects.get(loadid=self.load_id)
        self.assertTrue(event.complete)
        self.assertTrue(event.successful)
        self.assertIsNotNone(event.load_end_time)

    def test_empty_load_returns_true(self):
        result = self._run()
        self.assertTrue(result)


class PostProcessStagingTests(TestCase):
    """Tests for _post_process_staging using mocks to avoid DB dependencies."""

    def _make_record(self, value):
        record = MagicMock()
        record.tileid = uuid.uuid4()
        record.value = value
        return record

    @patch("arches.app.etl_modules.staging_to_tile._refresh_resource_relationships")
    def test_resource_instance_triggers_refresh(self, mock_refresh):
        tile_id = uuid.uuid4()
        record = self._make_record(
            {"n": {"datatype": "resource-instance", "value": [{"resourceId": "x"}]}}
        )
        record.tileid = tile_id
        _post_process_staging([record])
        mock_refresh.assert_called_once_with(tile_id)

    @patch("arches.app.etl_modules.staging_to_tile._refresh_resource_relationships")
    def test_resource_instance_list_triggers_refresh(self, mock_refresh):
        tile_id = uuid.uuid4()
        record = self._make_record(
            {"n": {"datatype": "resource-instance-list", "value": []}}
        )
        record.tileid = tile_id
        _post_process_staging([record])
        mock_refresh.assert_called_once_with(tile_id)

    @patch("arches.app.etl_modules.staging_to_tile._refresh_resource_relationships")
    def test_non_resource_datatype_does_not_trigger_refresh(self, mock_refresh):
        record = self._make_record({"n": {"datatype": "string", "value": "hi"}})
        _post_process_staging([record])
        mock_refresh.assert_not_called()

    @patch("arches.app.etl_modules.staging_to_tile._refresh_resource_relationships")
    def test_null_value_record_skipped(self, mock_refresh):
        record = self._make_record(None)
        _post_process_staging([record])
        mock_refresh.assert_not_called()

    @patch("arches.app.etl_modules.staging_to_tile._refresh_resource_relationships")
    def test_non_dict_node_value_skipped(self, mock_refresh):
        """Non-dict values in the staged value dict should not cause errors."""
        record = self._make_record({"n": "not-a-dict"})
        _post_process_staging([record])  # should not raise
        mock_refresh.assert_not_called()

    @patch("arches.app.etl_modules.staging_to_tile._refresh_resource_relationships")
    @patch("arches.app.etl_modules.staging_to_tile.File")
    def test_file_list_updates_file_tile_association(self, mock_file, mock_refresh):
        file_id = str(uuid.uuid4())
        tile_id = uuid.uuid4()
        record = self._make_record(
            {"n": {"datatype": "file-list", "value": [{"file_id": file_id}]}}
        )
        record.tileid = tile_id
        _post_process_staging([record])
        mock_file.objects.filter.assert_called_once_with(fileid=file_id)
        mock_file.objects.filter.return_value.update.assert_called_once_with(
            tile_id=tile_id
        )

    @patch("arches.app.etl_modules.staging_to_tile._refresh_resource_relationships")
    @patch("arches.app.etl_modules.staging_to_tile.File")
    def test_file_list_entry_without_file_id_is_skipped(self, mock_file, mock_refresh):
        record = self._make_record(
            {"n": {"datatype": "file-list", "value": [{"no_file_id_key": "x"}]}}
        )
        _post_process_staging([record])
        mock_file.objects.filter.assert_not_called()

    @patch("arches.app.etl_modules.staging_to_tile._refresh_resource_relationships")
    def test_each_resource_tile_refreshed_once(self, mock_refresh):
        """Two nodes with resource-instance in the same tile → one refresh call."""
        tile_id = uuid.uuid4()
        record = self._make_record(
            {
                "n1": {"datatype": "resource-instance", "value": []},
                "n2": {"datatype": "resource-instance-list", "value": []},
            }
        )
        record.tileid = tile_id
        _post_process_staging([record])
        mock_refresh.assert_called_once_with(tile_id)
