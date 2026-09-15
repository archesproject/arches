import copy
from types import SimpleNamespace
from uuid import uuid4
from arches.app.models.models import EditLog, Language, TileModel
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.http.request import HttpRequest

from arches.extensions.querysets.datatypes.datatypes import DataTypeFactory
from arches.extensions.querysets.models import ResourceTileTree, TileTree
from arches.extensions.querysets.utils.models import ensure_request
from arches.extensions.querysets.utils.tests import GraphTestCase


class SaveTileTests(GraphTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        call_command("add_test_users", verbosity=0)
        resources = ResourceTileTree.get_tiles(
            "datatype_lookups", as_representation=True
        )
        cls.resource_42 = resources.get(pk=cls.resource_42.pk)
        cls.resource_42.graph_publication_id = cls.graph.publication_id
        cls.resource_42.save()
        cls.datatype_1 = cls.resource_42.aliased_data.datatypes_1
        cls.datatype_n = cls.resource_42.aliased_data.datatypes_n

        cls.resource_none = resources.get(pk=cls.resource_none.pk)
        cls.resource_none.graph_publication_id = cls.graph.publication_id
        cls.resource_none.save()
        cls.datatype_1_none = cls.resource_none.aliased_data.datatypes_1
        cls.datatype_n_none = cls.resource_none.aliased_data.datatypes_n

    def assert_default_values_present(self, resource):
        languages = Language.objects.all()
        for node_id_str, value in resource.aliased_data.datatypes_1.data.items():
            node = [node for node in self.data_nodes if str(node.pk) == node_id_str][0]
            with self.subTest(alias=node.alias):
                default_value = self.default_vals_by_nodeid[node_id_str]
                expected = TileTree.get_cleaned_default_value(node, default_value)
                # Saving also runs pre_structure_tile_data(), which pads a
                # blank entry for every system Language (see StringDataType).
                dt_instance = DataTypeFactory().get_instance(node.datatype)
                mock_tile = SimpleNamespace(data={node_id_str: expected})
                dt_instance.pre_structure_tile_data(
                    mock_tile, node_id_str, languages=languages
                )
                expected = mock_tile.data[node_id_str]
                self.assertEqual(value, expected)

    def test_blank_tile_save_with_defaults(self):
        # Existing tiles with `None`'s should not be updated with defaults during save
        self.resource_none.save()
        for key, value in self.resource_none.aliased_data.datatypes_1.data.items():
            self.assertIsNone(value, f"Expected None for {key}")

        # fill_blanks only intializes a tile for nodegroups that don't yet have
        # a tile. Remove those tiles so we can use fill_blanks.
        self.resource_42.aliased_data.datatypes_1.delete()
        self.resource_42.refresh_from_db()
        self.resource_42.fill_blanks()
        # Saving a blank tile should populate default values if defaults are defined.
        self.resource_42.save(force_admin=True)
        self.assert_default_values_present(self.resource_42)

        # fill_blanks gives an unsaved empty tile, but we also need to test that inserting
        # a tile (ie from the frontend) will fill defaults if no values are provided
        self.resource_42.aliased_data.datatypes_1.delete()
        self.resource_42.refresh_from_db()
        self.resource_42.fill_blanks()

        # mock a new tile via fill_blanks, but overwrite default values set by fill_blanks
        for node in self.resource_42.aliased_data.datatypes_1.data:
            self.resource_42.aliased_data.datatypes_1.data[node] = None
        # Save should stock defaults
        self.resource_42.aliased_data.datatypes_1.save(force_admin=True)
        self.assert_default_values_present(self.resource_42)

    def test_save_new_tile_provisional(self):
        tile = self.resource_none.aliased_data.datatypes_1
        tile.delete()
        tile.pk = uuid4()
        provisional_editor = User.objects.get(username="tester3")
        request = HttpRequest()
        request.user = provisional_editor
        tile.save(request=request)
        edit_log = EditLog.objects.get(tileinstanceid=tile.pk)
        self.assertEqual(edit_log.newvalue, {})

    def test_update_tile_provisional(self):
        provisional_editor = User.objects.get(username="tester3")
        request = HttpRequest()
        request.user = provisional_editor
        tile = self.resource_none.aliased_data.datatypes_1
        tile.aliased_data.number_alias = 43
        tile.save(request=request)
        edit_log = EditLog.objects.get(tileinstanceid=tile.pk)
        self.assertEqual(edit_log.oldvalue, edit_log.newvalue)
        self.assertNotEqual(edit_log.oldprovisionalvalue, edit_log.newprovisionalvalue)
        self.assertEqual(edit_log.newprovisionalvalue[str(self.number_node_1.pk)], 43)

    def test_fill_blanks(self):
        self.resource_none.tilemodel_set.all().delete()
        self.resource_none.fill_blanks()
        self.assertIsInstance(self.resource_none.aliased_data.datatypes_1, TileTree)
        self.assertIsInstance(self.resource_none.aliased_data.datatypes_n[0], TileTree)
        self.assertIsInstance(
            self.resource_none.aliased_data.datatypes_1.aliased_data.datatypes_1_child,
            TileTree,
        )

        # Remove the child, fill_blanks() again.
        self.resource_none.aliased_data.datatypes_1.aliased_data.datatypes_1_child = (
            None
        )
        self.resource_none.fill_blanks()
        self.assertIsInstance(
            self.resource_none.aliased_data.datatypes_1.aliased_data.datatypes_1_child,
            TileTree,
        )

        msg = "Attempted to append to a populated cardinality-1 nodegroup"
        with self.assertRaisesMessage(RuntimeError, msg):
            self.resource_none.append_tile("datatypes_1")

    def test_parent_tile_backfilled_on_child_tile_save(self):
        self.resource_none.tilemodel_set.all().delete()
        new_child_tile = TileTree(
            resourceinstance=self.resource_none,
            nodegroup=self.nodegroup_1_child,
            number_child=4,
            # TODO(arches_version==9.0.0): in Arches 8+, data={} can be removed.
            data={},
        )
        new_child_tile.save(force_admin=True)
        # The parent property holds the richer TileTree
        self.assertIsInstance(new_child_tile.parent, TileTree)
        # The regular Django field is untouched (still a vanilla TileModel)
        self.assertNotIsInstance(new_child_tile.parenttile, TileTree)
        self.assertIsInstance(new_child_tile.parenttile, TileModel)

    def test_cardinality_error(self):
        tt = TileTree(
            nodegroup=self.nodegroup_1, resourceinstance=self.resource_42, data={}
        )
        with self.assertRaises(ValidationError) as ctx:
            tt.save(force_admin=True)
        self.assertEqual(
            ctx.exception.message_dict, {"datatypes_1": ["Tile Cardinality Error"]}
        )

    def test_simple_tile_delete(self):
        request = ensure_request(None, True)
        request.GET["delete_missing_tiles"] = "true"
        self.resource_42.aliased_data.datatypes_1 = None
        self.resource_42.save(request=request, force_admin=True)

        resources = ResourceTileTree.get_tiles(
            "datatype_lookups", as_representation=True
        )
        local_resource_42 = resources.get(pk=self.resource_42.pk)
        self.assertEqual(local_resource_42.aliased_data.datatypes_1, None)

    def test_cardinality_n_tile_delete(self):
        request = ensure_request(None, True)
        request.GET["delete_missing_tiles"] = "true"

        tile_copy = copy.deepcopy(self.datatype_n[0])
        tile_copy.tileid = uuid4()
        tile_copy.aliased_data.datatypes_n_child[0].tileid = uuid4()

        self.resource_42.aliased_data.datatypes_n.append(tile_copy)
        self.resource_42.save(request=request, force_admin=True)

        resources = ResourceTileTree.get_tiles(
            "datatype_lookups", as_representation=True
        )
        local_resource_42 = resources.get(pk=self.resource_42.pk)

        self.assertEqual(
            len(local_resource_42.aliased_data.datatypes_n),
            2,
            "Confirm two tiles before deletion",
        )

        # now test deletion by restoring the original tiles, effectively
        # removing the newly added tile and its child tile
        local_resource_42.aliased_data.datatypes_n = [self.datatype_n[0]]
        local_resource_42.save(request=request, force_admin=True)

        resources = ResourceTileTree.get_tiles(
            "datatype_lookups", as_representation=True
        )
        local_resource_42 = resources.get(pk=self.resource_42.pk)
        self.assertEqual(
            len(local_resource_42.aliased_data.datatypes_n),
            1,
            "Confirm one tile after deletion",
        )
        self.assertEqual(
            len(
                local_resource_42.aliased_data.datatypes_n[
                    0
                ].aliased_data.datatypes_n_child
            ),
            1,
            "Confirm child tile still exists after deletion of sibling tile",
        )

    def test_tile_edit_log_records_correct_old_and_new_values(self):
        """Edit log old_value must reflect pre-update DB state, not the incoming data.

        Regression: _existing_data was overwritten with vanilla_instance.data
        (the new data) in _perform_transaction after the field sync, causing
        old_value == new_value in the edit log.
        """
        node_id_str = str(self.non_localized_string_node_1.pk)

        # Capture the value currently stored in the DB before any update.
        tile_before = TileModel.objects.get(pk=self.cardinality_1_tile.pk)
        old_stored_value = tile_before.data[node_id_str]  # "forty-two"

        new_value = "fifty-two"
        self.assertNotEqual(old_stored_value, new_value)

        # Clear any edit log entries written during setUpTestData so we can
        # use .get() unambiguously after the save.
        EditLog.objects.filter(tileinstanceid=str(self.cardinality_1_tile.pk)).delete()

        # Fetch via TileTree and update the non-localized-string value.
        tile = TileTree.get_tiles("datatype_lookups", "datatypes_1").get(
            pk=self.cardinality_1_tile.pk
        )
        tile.aliased_data.non_localized_string_alias = new_value
        tile.save(force_admin=True)

        log_entry = EditLog.objects.get(
            tileinstanceid=str(self.cardinality_1_tile.pk),
            edittype="tile edit",
        )
        self.assertEqual(
            log_entry.oldvalue[node_id_str],
            old_stored_value,
            "old_value in edit log should reflect the pre-update DB value",
        )
        self.assertEqual(
            log_entry.newvalue[node_id_str],
            new_value,
            "new_value in edit log should reflect the updated value",
        )
        self.assertNotEqual(
            log_entry.oldvalue,
            log_entry.newvalue,
            "old_value and new_value must differ in the edit log",
        )
