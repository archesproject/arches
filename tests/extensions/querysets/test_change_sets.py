import json
import tempfile
import uuid
from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from django.test.client import MULTIPART_CONTENT
from django.urls import reverse

from arches.app.models.models import (
    CardModel,
    CardXNodeXWidget,
    EditLog,
    File,
    Node,
    TileModel,
)

from arches.extensions.querysets.rest_framework.change_sets import ResourceChangeSet
from arches.extensions.querysets.utils.tests import GraphTestCase

GRAPH = "datatype_lookups"
STRING_ALIAS = "non_localized_string_alias"
STRING_ALIAS_N = "non_localized_string_alias_n"


def without_last_updated(data):
    # Like PUT, the save response can carry pre-save last_updated timestamps.
    if isinstance(data, dict):
        return {
            key: without_last_updated(value)
            for key, value in data.items()
            if key != "last_updated"
        }
    if isinstance(data, list):
        return [without_last_updated(item) for item in data]
    return data


class ChangeSetViewMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command("add_test_users", verbosity=0)

    def setUp(self):
        self.client.force_login(User.objects.get(username="dev"))
        self.string_node = Node.objects.get(graph=self.graph, alias=STRING_ALIAS)

    def changes_url(self, resource=None):
        return reverse(
            "arches_querysets:api-resource-changes",
            kwargs={"graph": GRAPH, "pk": str((resource or self.resource_42).pk)},
        )

    def post_changes(self, changes):
        return self.client.post(
            self.changes_url(), {"changes": changes}, content_type="application/json"
        )

    def get_resource(self):
        response = self.client.get(
            reverse(
                "arches_querysets:api-resource",
                kwargs={"graph": GRAPH, "pk": str(self.resource_42.pk)},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        return response.json()

    def stored_string(self):
        self.cardinality_1_tile.refresh_from_db()
        return self.cardinality_1_tile.data[str(self.string_node.pk)]

    def set_stored_string(self, value):
        """Simulate a concurrent save by someone else."""
        data = {**self.cardinality_1_tile.data, str(self.string_node.pk): value}
        TileModel.objects.filter(pk=self.cardinality_1_tile.pk).update(data=data)

    def string_edit(self, value, original="forty-two", change_id="c1"):
        return {
            "id": change_id,
            "type": "edit",
            "nodegroupAlias": "datatypes_1",
            "tileId": str(self.cardinality_1_tile.pk),
            "aliasedData": {STRING_ALIAS: {"node_value": value}},
            "original": {STRING_ALIAS: original},
        }


class ResourceChangeSetViewTests(ChangeSetViewMixin, GraphTestCase):
    def test_edit_saves_and_returns_get_shape(self):
        edit_log_count = EditLog.objects.count()

        response = self.post_changes([self.string_edit("mine")])

        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        self.assertEqual(self.stored_string(), "mine")
        self.assertGreater(EditLog.objects.count(), edit_log_count)
        self.assertEqual(
            without_last_updated(response.json()),
            without_last_updated(self.get_resource()),
        )

    def test_modified_conflict_saves_nothing(self):
        self.set_stored_string("someone-else")

        response = self.post_changes([self.string_edit("mine")])

        self.assertEqual(response.status_code, HTTPStatus.CONFLICT, response.content)
        body = response.json()
        self.assertIsInstance(body["message"], str)
        self.assertEqual(body["resource"], self.get_resource())
        self.assertEqual(
            body["conflicts"],
            [
                {
                    "changeId": "c1",
                    "reason": "modified",
                    "nodegroupAlias": "datatypes_1",
                    "tileId": str(self.cardinality_1_tile.pk),
                    "nodes": {
                        STRING_ALIAS: {
                            "current": "someone-else",
                            "currentDisplay": "someone-else",
                            "original": "forty-two",
                        }
                    },
                }
            ],
        )
        self.assertEqual(self.stored_string(), "someone-else")

    def test_overwrite_after_conflict(self):
        self.set_stored_string("someone-else")
        conflict = self.post_changes([self.string_edit("mine")]).json()
        current = conflict["conflicts"][0]["nodes"][STRING_ALIAS]["current"]

        response = self.post_changes([self.string_edit("mine", original=current)])

        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        self.assertEqual(self.stored_string(), "mine")

    def test_identical_concurrent_edit_is_not_a_conflict(self):
        self.set_stored_string("mine")

        response = self.post_changes([self.string_edit("mine")])

        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)

    def test_all_or_nothing(self):
        self.set_stored_string("someone-else")
        edit_log_count = EditLog.objects.count()
        unrelated_edit = {
            "id": "c1",
            "type": "edit",
            "nodegroupAlias": "datatypes_n",
            "tileId": str(self.cardinality_n_tile.pk),
            "aliasedData": {STRING_ALIAS_N: {"node_value": "unrelated"}},
            "original": {STRING_ALIAS_N: "forty-two"},
        }

        response = self.post_changes(
            [unrelated_edit, self.string_edit("mine", change_id="c2")]
        )

        self.assertEqual(response.status_code, HTTPStatus.CONFLICT, response.content)
        self.assertEqual([c["changeId"] for c in response.json()["conflicts"]], ["c2"])
        self.cardinality_n_tile.refresh_from_db()
        string_node_n = Node.objects.get(graph=self.graph, alias=STRING_ALIAS_N)
        self.assertEqual(
            self.cardinality_n_tile.data[str(string_node_n.pk)], "forty-two"
        )
        self.assertEqual(EditLog.objects.count(), edit_log_count)

    def test_deleted_conflict(self):
        tile_id = str(self.cardinality_n_child_tile.pk)
        TileModel.objects.filter(pk=tile_id).delete()

        response = self.post_changes(
            [
                {
                    "id": "c1",
                    "type": "edit",
                    "nodegroupAlias": "datatypes_n_child",
                    "tileId": tile_id,
                    "aliasedData": {
                        "non_localized_string_alias_n_child": {"node_value": "x"}
                    },
                    "original": {"non_localized_string_alias_n_child": "child-n-value"},
                }
            ]
        )

        self.assertEqual(response.status_code, HTTPStatus.CONFLICT, response.content)
        self.assertEqual(
            response.json()["conflicts"],
            [
                {
                    "changeId": "c1",
                    "reason": "deleted",
                    "nodegroupAlias": "datatypes_n_child",
                    "tileId": tile_id,
                }
            ],
        )

    def test_delete_of_deleted_tile_is_not_a_conflict(self):
        response = self.post_changes(
            [
                {
                    "id": "c1",
                    "type": "delete",
                    "nodegroupAlias": "datatypes_n_child",
                    "tileId": str(uuid.uuid4()),
                }
            ]
        )

        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)

    def test_delete_tile(self):
        response = self.post_changes(
            [
                {
                    "id": "c1",
                    "type": "delete",
                    "nodegroupAlias": "datatypes_n_child",
                    "tileId": str(self.cardinality_n_child_tile.pk),
                }
            ]
        )

        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        self.assertFalse(
            TileModel.objects.filter(pk=self.cardinality_n_child_tile.pk).exists()
        )

    def test_parent_deleted_conflict(self):
        response = self.post_changes(
            [
                {
                    "id": "c1",
                    "type": "add",
                    "nodegroupAlias": "datatypes_n_child",
                    "parentTileId": str(uuid.uuid4()),
                    "tile": {"tileid": str(uuid.uuid4()), "aliased_data": {}},
                }
            ]
        )

        self.assertEqual(response.status_code, HTTPStatus.CONFLICT, response.content)
        self.assertEqual(response.json()["conflicts"][0]["reason"], "parent_deleted")

    def test_slot_taken_conflict(self):
        response = self.post_changes(
            [
                {
                    "id": "c1",
                    "type": "add",
                    "nodegroupAlias": "datatypes_1_child",
                    "parentTileId": str(self.cardinality_1_tile.pk),
                    "tile": {"tileid": str(uuid.uuid4()), "aliased_data": {}},
                }
            ]
        )

        self.assertEqual(response.status_code, HTTPStatus.CONFLICT, response.content)
        self.assertEqual(response.json()["conflicts"][0]["reason"], "slot_taken")

    def test_add_tile(self):
        new_tile_id = str(uuid.uuid4())

        response = self.post_changes(
            [
                {
                    "id": "c1",
                    "type": "add",
                    "nodegroupAlias": "datatypes_n_child",
                    "parentTileId": str(self.cardinality_n_tile.pk),
                    "tile": {
                        "tileid": new_tile_id,
                        "aliased_data": {
                            "non_localized_string_alias_n_child": {
                                "node_value": "added"
                            }
                        },
                    },
                }
            ]
        )

        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        added = TileModel.objects.get(pk=new_tile_id)
        self.assertEqual(added.resourceinstance_id, self.resource_42.pk)
        self.assertEqual(added.parenttile_id, self.cardinality_n_tile.pk)

    def test_empty_change_set_returns_resource(self):
        response = self.post_changes([])

        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        self.assertEqual(response.json(), self.get_resource())

    def test_anonymous_is_forbidden(self):
        self.client.logout()

        response = self.post_changes([self.string_edit("mine")])

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(self.stored_string(), "forty-two")

    def test_nodegroup_permission_is_enforced(self):
        editable = {str(self.nodegroup_n.pk)}
        with patch(
            "arches.app.models.models.UserProfile.editable_nodegroups", editable
        ):
            response = self.post_changes([self.string_edit("mine")])

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN, response.content)
        self.assertEqual(self.stored_string(), "forty-two")

    def test_delete_requires_delete_permission(self):
        with patch("arches.app.models.models.UserProfile.deletable_nodegroups", set()):
            response = self.post_changes(
                [
                    {
                        "id": "c1",
                        "type": "delete",
                        "nodegroupAlias": "datatypes_n_child",
                        "tileId": str(self.cardinality_n_child_tile.pk),
                    }
                ]
            )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN, response.content)
        self.assertTrue(
            TileModel.objects.filter(pk=self.cardinality_n_child_tile.pk).exists()
        )

    def test_unknown_change_type_is_rejected(self):
        response = self.post_changes(
            [{"id": "c1", "type": "replace", "nodegroupAlias": "datatypes_1"}]
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_unknown_nodegroup_alias_is_rejected(self):
        change = self.string_edit("mine")
        change["nodegroupAlias"] = "not_a_nodegroup"

        response = self.post_changes([change])

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_node_from_another_nodegroup_is_rejected(self):
        change = self.string_edit("mine")
        change["aliasedData"] = {STRING_ALIAS_N: {"node_value": "x"}}
        change["original"] = {STRING_ALIAS_N: "forty-two"}

        response = self.post_changes([change])

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_tile_from_another_resource_is_rejected(self):
        change = self.string_edit("mine")
        change["tileId"] = str(self.cardinality_1_tile_none.pk)

        response = self.post_changes([change])

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.cardinality_1_tile_none.refresh_from_db()
        self.assertNotEqual(
            self.cardinality_1_tile_none.data.get(str(self.string_node.pk)), "mine"
        )

    def test_add_with_foreign_parent_is_rejected(self):
        response = self.post_changes(
            [
                {
                    "id": "c1",
                    "type": "add",
                    "nodegroupAlias": "datatypes_n_child",
                    "parentTileId": str(self.cardinality_n_tile_none.pk),
                    "tile": {"tileid": str(uuid.uuid4()), "aliased_data": {}},
                }
            ]
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_multipart_file_upload(self):
        file_node = Node.objects.get(graph=self.graph, alias="file_list_alias")
        current = self.get_resource()["aliased_data"]["datatypes_1"]["aliased_data"]
        original_files = current["file_list_alias"]["node_value"]
        change = {
            "id": "c1",
            "type": "edit",
            "nodegroupAlias": "datatypes_1",
            "tileId": str(self.cardinality_1_tile.pk),
            "aliasedData": {
                "file_list_alias": {
                    "node_value": [{"name": "new_photo.jpg", "type": "image/jpeg"}]
                }
            },
            "original": {"file_list_alias": original_files},
        }
        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            body = {
                "json": json.dumps({"changes": [change]}),
                f"file-list_{file_node.pk}": SimpleUploadedFile(
                    "new_photo.jpg", b"fake-image-bytes", content_type="image/jpeg"
                ),
            }
            response = self.client.post(
                self.changes_url(), body, content_type=MULTIPART_CONTENT
            )

            self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
            files = response.json()["aliased_data"]["datatypes_1"]["aliased_data"][
                "file_list_alias"
            ]["node_value"]
            self.assertEqual([entry["name"] for entry in files], ["new_photo.jpg"])
            self.assertEqual(
                File.objects.get(pk=files[0]["file_id"]).path.read(),
                b"fake-image-bytes",
            )


class DataRootGraphTestCase(GraphTestCase):
    """Adds nodegroups whose root (grouping) node itself collects data."""

    @classmethod
    def create_child_nodegroups(cls):
        super().create_child_nodegroups()
        string_dt = next(dt for dt in cls.datatypes if dt.pk == "non-localized-string")
        cls.data_roots = {}
        for alias, cardinality, parent in [
            ("root_label", "1", None),
            ("root_tags", "n", None),
            ("root_child_label", "1", cls.nodegroup_n),
        ]:
            nodegroup, node = cls.create_nodegroup(alias, cardinality, parent)
            node.datatype = string_dt.pk
            node.config = string_dt.defaultconfig
            node.save()
            cls.data_roots[alias] = (nodegroup, node)

    @classmethod
    def create_cards(cls):
        super().create_cards()
        CardModel.objects.bulk_create(
            CardModel(graph=cls.graph, nodegroup=nodegroup)
            for nodegroup, _ in cls.data_roots.values()
        )

    @classmethod
    def create_widgets(cls):
        super().create_widgets()
        CardXNodeXWidget.objects.bulk_create(
            CardXNodeXWidget(
                node=node,
                widget_id=cls.find_default_widget_id(node, cls.datatypes),
                card=CardModel.objects.get(nodegroup=nodegroup),
            )
            for nodegroup, node in cls.data_roots.values()
        )

    @classmethod
    def create_relations(cls):
        super().create_relations()
        cls.data_root_tiles = {}
        for alias, parent_tile, value in [
            ("root_label", None, "label-value"),
            ("root_tags", None, "tag-a"),
            ("root_child_label", cls.cardinality_n_tile, "child-label-value"),
        ]:
            nodegroup, node = cls.data_roots[alias]
            cls.data_root_tiles[alias] = TileModel.objects.create(
                nodegroup=nodegroup,
                resourceinstance_id=cls.resource_42.pk,
                parenttile=parent_tile,
                data={str(node.pk): value},
            )


class DataBearingRootNodeTests(ChangeSetViewMixin, DataRootGraphTestCase):
    def stored(self, alias):
        tile = TileModel.objects.get(pk=self.data_root_tiles[alias].pk)
        return tile.data[str(self.data_roots[alias][1].pk)]

    def root_edit(self, alias, value, original):
        return {
            "id": "c1",
            "type": "edit",
            "nodegroupAlias": alias,
            "tileId": str(self.data_root_tiles[alias].pk),
            "aliasedData": {alias: {"node_value": value}},
            "original": {alias: original},
        }

    def assert_untouched(self, *aliases):
        expected = {
            "root_label": "label-value",
            "root_tags": "tag-a",
            "root_child_label": "child-label-value",
        }
        for alias in aliases:
            self.assertEqual(self.stored(alias), expected[alias], alias)

    def test_unrelated_edit_keeps_data_bearing_roots(self):
        response = self.post_changes([self.string_edit("mine")])

        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        self.assertEqual(self.stored_string(), "mine")
        self.assert_untouched("root_label", "root_tags", "root_child_label")
        data = response.json()["aliased_data"]
        self.assertEqual(
            data["root_label"]["aliased_data"]["root_label"]["node_value"],
            "label-value",
        )

    def test_edit_top_level_data_bearing_root(self):
        response = self.post_changes(
            [self.root_edit("root_label", "new-label", "label-value")]
        )

        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        self.assertEqual(self.stored("root_label"), "new-label")
        self.assert_untouched("root_tags", "root_child_label")

    def test_edit_nested_data_bearing_root(self):
        response = self.post_changes(
            [self.root_edit("root_child_label", "new-child-label", "child-label-value")]
        )

        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        self.assertEqual(self.stored("root_child_label"), "new-child-label")
        self.assert_untouched("root_label", "root_tags")

    def test_data_bearing_root_conflict(self):
        _, node = self.data_roots["root_label"]
        TileModel.objects.filter(pk=self.data_root_tiles["root_label"].pk).update(
            data={str(node.pk): "someone-else"}
        )

        response = self.post_changes(
            [self.root_edit("root_label", "mine", "label-value")]
        )

        self.assertEqual(response.status_code, HTTPStatus.CONFLICT, response.content)
        self.assertEqual(
            response.json()["conflicts"][0]["nodes"]["root_label"]["current"],
            "someone-else",
        )
        self.assertEqual(self.stored("root_label"), "someone-else")

    def test_add_tile_with_data_bearing_root(self):
        new_tile_id = str(uuid.uuid4())
        response = self.post_changes(
            [
                {
                    "id": "c1",
                    "type": "add",
                    "nodegroupAlias": "root_tags",
                    "parentTileId": None,
                    "tile": {
                        "tileid": new_tile_id,
                        "aliased_data": {"root_tags": {"node_value": "tag-b"}},
                    },
                }
            ]
        )

        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        node = self.data_roots["root_tags"][1]
        self.assertEqual(
            TileModel.objects.get(pk=new_tile_id).data[str(node.pk)], "tag-b"
        )
        self.assert_untouched("root_label", "root_tags", "root_child_label")


class ResourceChangeSetRebaseTests(GraphTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command("add_test_users", verbosity=0)

    def setUp(self):
        self.client.force_login(User.objects.get(username="dev"))
        self.representation = self.client.get(
            reverse(
                "arches_querysets:api-resource",
                kwargs={"graph": GRAPH, "pk": str(self.resource_42.pk)},
            )
        ).json()

    def change_set(self, changes):
        return ResourceChangeSet(
            changes,
            self.representation,
            graph_nodes=Node.objects.filter(graph=self.graph).select_related(
                "nodegroup"
            ),
            resource_id=self.resource_42.pk,
            user=None,
        )

    def test_edit_matching_server_value_is_dropped(self):
        edit = {
            "id": "c1",
            "type": "edit",
            "nodegroupAlias": "datatypes_1",
            "tileId": str(self.cardinality_1_tile.pk),
            "aliasedData": {STRING_ALIAS: {"node_value": "forty-two"}},
            "original": {STRING_ALIAS: "forty-two"},
        }

        self.assertEqual(self.change_set([edit]).rebase(), [])

    def test_add_of_existing_tile_becomes_edit_of_changed_nodes(self):
        add = {
            "id": "c1",
            "type": "add",
            "nodegroupAlias": "datatypes_1",
            "parentTileId": None,
            "tile": {
                "tileid": str(self.cardinality_1_tile.pk),
                "aliased_data": {
                    STRING_ALIAS: {"node_value": "forty-two"},
                    "number_alias": {"node_value": 43},
                },
            },
        }

        rebased = self.change_set([add]).rebase()

        self.assertEqual(len(rebased), 1)
        self.assertEqual(rebased[0]["type"], "edit")
        self.assertEqual(
            rebased[0]["aliasedData"], {"number_alias": {"node_value": 43}}
        )

    def test_reorder_matching_current_order_is_dropped(self):
        current_ids = [
            tile["tileid"]
            for tile in self.representation["aliased_data"]["datatypes_n"]
        ]
        reorder = {
            "id": "c1",
            "type": "reorder",
            "nodegroupAlias": "datatypes_n",
            "parentTileId": None,
            "tileIds": current_ids,
        }

        self.assertEqual(self.change_set([reorder]).rebase(), [])

    def test_replacing_a_deleted_cardinality_1_tile_is_not_slot_taken(self):
        changes = [
            {
                "id": "c1",
                "type": "delete",
                "nodegroupAlias": "datatypes_1_child",
                "tileId": str(self.cardinality_1_child_tile.pk),
            },
            {
                "id": "c2",
                "type": "add",
                "nodegroupAlias": "datatypes_1_child",
                "parentTileId": str(self.cardinality_1_tile.pk),
                "tile": {"tileid": str(uuid.uuid4()), "aliased_data": {}},
            },
        ]

        self.assertEqual(self.change_set(changes).find_conflicts(), [])
