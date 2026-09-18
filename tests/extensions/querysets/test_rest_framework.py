import json
import tempfile
import unittest
import uuid
from http import HTTPStatus
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse
from arches import __version__ as _arches_version_str
from packaging.version import Version

arches_version = Version(_arches_version_str)
from arches.app.models.graph import Graph
from arches.app.models.models import EditLog, File, Language, Node, NodeGroup

from arches.extensions.querysets.rest_framework.serializers import (
    ArchesResourceSerializer,
    ArchesResourceTopNodegroupsSerializer,
    ArchesSingleNodegroupSerializer,
    ArchesTileSerializer,
)
from arches.extensions.querysets.utils.models import ensure_request
from arches.extensions.querysets.utils.tests import GraphTestCase

MUTABLE_PERMITTED_NODEGROUPS = set()


def padded_string_node_value(value, *, language="en", direction="ltr"):
    """StringDataType.pre_structure_tile_data() pads a blank entry for every
    system Language, not just the one a value was supplied for."""
    node_value = {
        lang.code: {"value": "", "direction": lang.default_direction}
        for lang in Language.objects.all()
    }
    node_value[language] = {"value": value, "direction": direction}
    return node_value


class RestFrameworkTests(GraphTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command("add_test_users", verbosity=0)

    def patched_ensure_request(self, request, force_admin):
        request.user.userprofile.viewable_nodegroups = {str(self.nodegroup_id)}
        self.set_single_viewable_nodegroup(request, self.nodegroup_1.pk)
        return ensure_request(request, force_admin)

    def test_create_tile_for_new_resource(self):
        create_url = reverse(
            "arches_querysets:api-tiles",
            kwargs={"graph": "datatype_lookups", "nodegroup_alias": "datatypes_n"},
        )
        request_body = {"aliased_data": {"string_alias_n": "create_value"}}

        # Anonymous user lacks editing permissions.
        forbidden_response = self.client.post(
            create_url, request_body, content_type="application/json"
        )
        self.assertEqual(forbidden_response.status_code, HTTPStatus.FORBIDDEN)

        # Dev user can edit.
        self.client.login(username="dev", password="dev")
        response = self.client.post(
            create_url, request_body, content_type="application/json"
        )

        # The response includes the context.
        self.assertEqual(response.status_code, HTTPStatus.CREATED, response.content)
        self.assertIn("aliased_data", response.json())
        self.assertIsInstance(uuid.UUID(response.json()["tileid"]), uuid.UUID)
        self.assertEqual(
            response.json()["aliased_data"]["string_alias_n"],
            {
                "display_value": "create_value",
                "node_value": padded_string_node_value("create_value"),
                "details": [],
            },
        )
        self.assertSequenceEqual(
            EditLog.objects.filter(
                resourceinstanceid=response.json()["resourceinstance"],
            )
            .values_list("edittype", flat=True)
            .order_by("edittype"),
            ["create", "tile create"],
        )

    def test_create_tile_for_existing_resource(self):
        create_url = reverse(
            "arches_querysets:api-tiles",
            kwargs={"graph": "datatype_lookups", "nodegroup_alias": "datatypes_n"},
        )
        request_body = {
            "aliased_data": {"string_alias_n": "create_value"},
            "resourceinstance": str(self.resource_42.pk),
        }
        self.client.login(username="dev", password="dev")
        response = self.client.post(
            create_url, request_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertIsInstance(uuid.UUID(response.json()["tileid"]), uuid.UUID)
        self.assertEqual(response.json()["resourceinstance"], str(self.resource_42.pk))
        self.assertEqual(
            response.json()["aliased_data"]["string_alias_n"],
            {
                "display_value": "create_value",
                "node_value": padded_string_node_value("create_value"),
                "details": [],
            },
        )

    def test_create_nested_tiles_for_new_resource(self):
        self.client.login(username="dev", password="dev")
        create_url = reverse(
            "arches_querysets:api-tiles",
            kwargs={"graph": "datatype_lookups", "nodegroup_alias": "datatypes_1"},
        )
        request_body = {
            "aliased_data": {
                "string_alias": "create_value",
                "datatypes_1_child": {
                    "aliased_data": {"string_alias_child": "child_create_value"}
                },
            },
        }

        response = self.client.post(
            create_url, request_body, content_type="application/json"
        )

        # The response includes the context.
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertIn("aliased_data", response.json())
        self.assertIsInstance(uuid.UUID(response.json()["tileid"]), uuid.UUID)
        parent_data = response.json()["aliased_data"]
        self.assertEqual(
            parent_data["datatypes_1_child"]["aliased_data"]["string_alias_child"],
            {
                "display_value": "child_create_value",
                "node_value": padded_string_node_value("child_create_value"),
                "details": [],
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED, response.content)

        self.assertSequenceEqual(
            EditLog.objects.filter(
                resourceinstanceid=response.json()["resourceinstance"],
            )
            .values_list("edittype", flat=True)
            .order_by("edittype"),
            ["create", "tile create", "tile create"],
        )

    def test_create_nested_tiles_for_new_resource_via_resource_serializer(self):
        self.client.login(username="dev", password="dev")
        create_url = reverse(
            "arches_querysets:api-resources",
            kwargs={"graph": "datatype_lookups"},
        )
        request_body = {
            "aliased_data": {
                "datatypes_1": {
                    "aliased_data": {
                        "string_alias": "create_value",
                        "datatypes_1_child": {
                            "aliased_data": {"string_alias_child": "child_create_value"}
                        },
                    },
                },
            },
        }

        response = self.client.post(
            create_url, request_body, content_type="application/json"
        )

        # The response includes the context.
        self.assertEqual(response.status_code, HTTPStatus.CREATED, response.json())
        parent_data = response.json()["aliased_data"]["datatypes_1"]["aliased_data"]
        self.assertEqual(
            parent_data["datatypes_1_child"]["aliased_data"]["string_alias_child"],
            {
                "display_value": "child_create_value",
                "node_value": padded_string_node_value("child_create_value"),
                "details": [],
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED, response.content)

        edits = EditLog.objects.filter(
            resourceinstanceid=response.json()["resourceinstanceid"],
        ).order_by("edittype")
        self.assertEqual(
            [edit.edittype for edit in edits], ["create", "tile create", "tile create"]
        )
        self.assertEqual(len(set([edit.transactionid for edit in edits])), 1)

    def test_update_tile(self):
        update_url = reverse(
            "arches_querysets:api-tile",
            kwargs={
                "graph": "datatype_lookups",
                "nodegroup_alias": "datatypes_1",
                "pk": self.resource_42.aliased_data.datatypes_1.pk,
            },
        )
        request_body = {
            "aliased_data": {"string_alias": "update_value"},
            "resourceinstance": str(self.resource_42.pk),
        }
        assert "tileid" not in request_body, "tileid is not required in update requests"

        self.client.login(username="dev", password="dev")
        response = self.client.patch(
            update_url, request_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.json())
        self.assertIsInstance(uuid.UUID(response.json()["tileid"]), uuid.UUID)
        self.assertEqual(response.json()["resourceinstance"], str(self.resource_42.pk))
        self.assertEqual(
            response.json()["aliased_data"]["string_alias"],
            {
                "display_value": "update_value",
                "node_value": padded_string_node_value("update_value"),
                "details": [],
            },
        )

    def test_update_tile_with_child(self):
        """PATCH a cardinality-n parent tile + child simultaneously; child value must be
        fresh in the response (regression test for stale child aliased_data after save).
        """
        parent_tile = self.resource_42.aliased_data.datatypes_n[0]
        child_tile = parent_tile.aliased_data.datatypes_n_child[0]

        update_url = reverse(
            "arches_querysets:api-tile",
            kwargs={
                "graph": "datatype_lookups",
                "nodegroup_alias": "datatypes_n",
                "pk": parent_tile.pk,
            },
        )
        request_body = {
            "resourceinstance": str(self.resource_42.pk),
            "aliased_data": {
                "non_localized_string_alias_n": "updated-parent-value",
                "datatypes_n_child": [
                    {
                        "tileid": str(child_tile.pk),
                        "resourceinstance": str(self.resource_42.pk),
                        "aliased_data": {
                            "non_localized_string_alias_n_child": "updated-child-value",
                        },
                    }
                ],
            },
        }

        self.client.login(username="dev", password="dev")
        response = self.client.patch(
            update_url, request_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.json())

        def _node_value(v):
            return v["node_value"] if isinstance(v, dict) else v

        # Parent value must be updated.
        self.assertEqual(
            _node_value(
                response.json()["aliased_data"]["non_localized_string_alias_n"]
            ),
            "updated-parent-value",
        )

        # Child value must reflect the *just-saved* value, not the pre-save value.
        child_response = response.json()["aliased_data"]["datatypes_n_child"][0]
        child_non_loc_str = child_response["aliased_data"][
            "non_localized_string_alias_n_child"
        ]
        self.assertEqual(
            _node_value(child_non_loc_str),
            "updated-child-value",
            "Child tile aliased_data must be refreshed after save, not stale",
        )

    def test_update_resource_with_nested_child_tile(self):
        """PUT to ArchesResourceDetailView updating a cardinality-n parent + child
        simultaneously; child value must be fresh in the response.

        Regression test for stale aliased_data in _targeted_refresh_aliased_data:
        resource._tile_trees holds only top-level tiles; children live in the nested
        parent._tile_trees.  TileTreeOperation updates .data in-place on the same
        Python objects that live in the hierarchy, so reprocess_tiles_aliased_data
        must see the updated data when rebuilding parent aliased_data.
        """
        parent_tile = self.resource_42.aliased_data.datatypes_n[0]
        child_tile = parent_tile.aliased_data.datatypes_n_child[0]

        update_url = reverse(
            "arches_querysets:api-resource",
            kwargs={"graph": "datatype_lookups", "pk": str(self.resource_42.pk)},
        )
        request_body = {
            "aliased_data": {
                "datatypes_n": [
                    {
                        "tileid": str(parent_tile.pk),
                        "resourceinstance": str(self.resource_42.pk),
                        "aliased_data": {
                            "non_localized_string_alias_n": "resource-put-parent-value",
                            "datatypes_n_child": [
                                {
                                    "tileid": str(child_tile.pk),
                                    "resourceinstance": str(self.resource_42.pk),
                                    "aliased_data": {
                                        "non_localized_string_alias_n_child": "resource-put-child-value",
                                    },
                                }
                            ],
                        },
                    }
                ],
            },
        }

        self.client.login(username="dev", password="dev")
        response = self.client.put(
            update_url, request_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.json())

        def _node_value(v):
            return v["node_value"] if isinstance(v, dict) else v

        parents = response.json()["aliased_data"]["datatypes_n"]
        self.assertEqual(len(parents), 1)

        # Parent value must be updated.
        self.assertEqual(
            _node_value(parents[0]["aliased_data"]["non_localized_string_alias_n"]),
            "resource-put-parent-value",
        )

        # Child value must reflect the *just-saved* value, not the pre-save stale value.
        children = parents[0]["aliased_data"]["datatypes_n_child"]
        self.assertEqual(len(children), 1)
        self.assertEqual(
            _node_value(
                children[0]["aliased_data"]["non_localized_string_alias_n_child"]
            ),
            "resource-put-child-value",
            "Child tile aliased_data must be refreshed after resource PUT, not stale",
        )

    # ------------------------------------------------------------------ #
    # PATCH tile endpoint — parent + child, all cardinality combinations
    # ------------------------------------------------------------------ #

    def test_insert_and_update_tile_patch_1_1_parent_and_child(self):
        """PATCH card-1 parent + card-1 child; response must reflect inserted/updated values (1→1)."""
        parent_tile = self.resource_42.aliased_data.datatypes_1
        child_tile = parent_tile.aliased_data.datatypes_1_child
        update_url = reverse(
            "arches_querysets:api-tile",
            kwargs={
                "graph": "datatype_lookups",
                "nodegroup_alias": "datatypes_1",
                "pk": parent_tile.pk,
            },
        )

        def _nv(v):
            return v["node_value"] if isinstance(v, dict) else v

        self.client.login(username="dev", password="dev")
        # First PATCH: insert; response must reflect the inserted values.
        insert_response = self.client.patch(
            update_url,
            {
                "resourceinstance": str(self.resource_42.pk),
                "aliased_data": {
                    "non_localized_string_alias": "initial-1-1-parent",
                    "datatypes_1_child": {
                        "tileid": str(child_tile.pk),
                        "resourceinstance": str(self.resource_42.pk),
                        "aliased_data": {
                            "non_localized_string_alias_child": "initial-1-1-child"
                        },
                    },
                },
            },
            content_type="application/json",
        )
        self.assertEqual(
            insert_response.status_code, HTTPStatus.OK, insert_response.json()
        )
        self.assertEqual(
            _nv(insert_response.json()["aliased_data"]["non_localized_string_alias"]),
            "initial-1-1-parent",
        )
        insert_child = insert_response.json()["aliased_data"]["datatypes_1_child"]
        self.assertEqual(
            _nv(insert_child["aliased_data"]["non_localized_string_alias_child"]),
            "initial-1-1-child",
            "Card-1 child must be fresh in tile PATCH insert response (1→1)",
        )

        # Second PATCH: update; response must reflect the new value, not the stale one.
        update_response = self.client.patch(
            update_url,
            {
                "resourceinstance": str(self.resource_42.pk),
                "aliased_data": {
                    "non_localized_string_alias": "patch-1-1-parent",
                    "datatypes_1_child": {
                        "tileid": str(child_tile.pk),
                        "resourceinstance": str(self.resource_42.pk),
                        "aliased_data": {
                            "non_localized_string_alias_child": "patch-1-1-child"
                        },
                    },
                },
            },
            content_type="application/json",
        )
        self.assertEqual(
            update_response.status_code, HTTPStatus.OK, update_response.json()
        )
        self.assertEqual(
            _nv(update_response.json()["aliased_data"]["non_localized_string_alias"]),
            "patch-1-1-parent",
        )
        update_child = update_response.json()["aliased_data"]["datatypes_1_child"]
        self.assertEqual(
            _nv(update_child["aliased_data"]["non_localized_string_alias_child"]),
            "patch-1-1-child",
            "Card-1 child must be fresh in tile PATCH update response (1→1)",
        )

    def test_insert_and_update_tile_patch_1_n_parent_and_child(self):
        """PATCH card-1 parent + card-n child; response must reflect inserted/updated values (1→n)."""
        parent_tile = self.resource_42.aliased_data.datatypes_1
        child_tile = parent_tile.aliased_data.datatypes_1_n_child[0]
        update_url = reverse(
            "arches_querysets:api-tile",
            kwargs={
                "graph": "datatype_lookups",
                "nodegroup_alias": "datatypes_1",
                "pk": parent_tile.pk,
            },
        )

        def _nv(v):
            return v["node_value"] if isinstance(v, dict) else v

        self.client.login(username="dev", password="dev")
        # First PATCH: insert; response must reflect the inserted values.
        insert_response = self.client.patch(
            update_url,
            {
                "resourceinstance": str(self.resource_42.pk),
                "aliased_data": {
                    "non_localized_string_alias": "initial-1-n-parent",
                    "datatypes_1_n_child": [
                        {
                            "tileid": str(child_tile.pk),
                            "resourceinstance": str(self.resource_42.pk),
                            "aliased_data": {
                                "non_localized_string_alias_1_n_child": "initial-1-n-child"
                            },
                        }
                    ],
                },
            },
            content_type="application/json",
        )
        self.assertEqual(
            insert_response.status_code, HTTPStatus.OK, insert_response.json()
        )
        self.assertEqual(
            _nv(insert_response.json()["aliased_data"]["non_localized_string_alias"]),
            "initial-1-n-parent",
        )
        insert_children = insert_response.json()["aliased_data"]["datatypes_1_n_child"]
        self.assertEqual(len(insert_children), 1)
        self.assertEqual(
            _nv(
                insert_children[0]["aliased_data"][
                    "non_localized_string_alias_1_n_child"
                ]
            ),
            "initial-1-n-child",
            "Card-n child must be fresh in tile PATCH insert response (1→n)",
        )

        # Second PATCH: update; response must reflect the new value, not the stale one.
        update_response = self.client.patch(
            update_url,
            {
                "resourceinstance": str(self.resource_42.pk),
                "aliased_data": {
                    "non_localized_string_alias": "patch-1-n-parent",
                    "datatypes_1_n_child": [
                        {
                            "tileid": str(child_tile.pk),
                            "resourceinstance": str(self.resource_42.pk),
                            "aliased_data": {
                                "non_localized_string_alias_1_n_child": "patch-1-n-child"
                            },
                        }
                    ],
                },
            },
            content_type="application/json",
        )
        self.assertEqual(
            update_response.status_code, HTTPStatus.OK, update_response.json()
        )
        self.assertEqual(
            _nv(update_response.json()["aliased_data"]["non_localized_string_alias"]),
            "patch-1-n-parent",
        )
        update_children = update_response.json()["aliased_data"]["datatypes_1_n_child"]
        self.assertEqual(len(update_children), 1)
        self.assertEqual(
            _nv(
                update_children[0]["aliased_data"][
                    "non_localized_string_alias_1_n_child"
                ]
            ),
            "patch-1-n-child",
            "Card-n child must be fresh in tile PATCH update response (1→n)",
        )

    def test_insert_and_update_tile_patch_n_1_parent_and_child(self):
        """PATCH card-n parent + card-1 child; response must reflect inserted/updated values (n→1)."""
        parent_tile = self.resource_42.aliased_data.datatypes_n[0]
        child_tile = parent_tile.aliased_data.datatypes_n_1_child
        update_url = reverse(
            "arches_querysets:api-tile",
            kwargs={
                "graph": "datatype_lookups",
                "nodegroup_alias": "datatypes_n",
                "pk": parent_tile.pk,
            },
        )

        def _nv(v):
            return v["node_value"] if isinstance(v, dict) else v

        self.client.login(username="dev", password="dev")
        # First PATCH: insert; response must reflect the inserted values.
        insert_response = self.client.patch(
            update_url,
            {
                "resourceinstance": str(self.resource_42.pk),
                "aliased_data": {
                    "non_localized_string_alias_n": "initial-n-1-parent",
                    "datatypes_n_1_child": {
                        "tileid": str(child_tile.pk),
                        "resourceinstance": str(self.resource_42.pk),
                        "aliased_data": {
                            "non_localized_string_alias_n_1_child": "initial-n-1-child"
                        },
                    },
                },
            },
            content_type="application/json",
        )
        self.assertEqual(
            insert_response.status_code, HTTPStatus.OK, insert_response.json()
        )
        self.assertEqual(
            _nv(insert_response.json()["aliased_data"]["non_localized_string_alias_n"]),
            "initial-n-1-parent",
        )
        insert_child = insert_response.json()["aliased_data"]["datatypes_n_1_child"]
        self.assertEqual(
            _nv(insert_child["aliased_data"]["non_localized_string_alias_n_1_child"]),
            "initial-n-1-child",
            "Card-1 child must be fresh in tile PATCH insert response (n→1)",
        )

        # Second PATCH: update; response must reflect the new value, not the stale one.
        update_response = self.client.patch(
            update_url,
            {
                "resourceinstance": str(self.resource_42.pk),
                "aliased_data": {
                    "non_localized_string_alias_n": "patch-n-1-parent",
                    "datatypes_n_1_child": {
                        "tileid": str(child_tile.pk),
                        "resourceinstance": str(self.resource_42.pk),
                        "aliased_data": {
                            "non_localized_string_alias_n_1_child": "patch-n-1-child"
                        },
                    },
                },
            },
            content_type="application/json",
        )
        self.assertEqual(
            update_response.status_code, HTTPStatus.OK, update_response.json()
        )
        self.assertEqual(
            _nv(update_response.json()["aliased_data"]["non_localized_string_alias_n"]),
            "patch-n-1-parent",
        )
        update_child = update_response.json()["aliased_data"]["datatypes_n_1_child"]
        self.assertEqual(
            _nv(update_child["aliased_data"]["non_localized_string_alias_n_1_child"]),
            "patch-n-1-child",
            "Card-1 child must be fresh in tile PATCH update response (n→1)",
        )

    # ------------------------------------------------------------------ #
    # PUT resource endpoint — parent + child, all cardinality combinations
    # ------------------------------------------------------------------ #

    def test_insert_and_update_resource_put_1_1_parent_and_child(self):
        """PUT resource with card-1 parent + card-1 child; response must reflect inserted/updated values (1→1)."""
        parent_tile = self.resource_42.aliased_data.datatypes_1
        child_tile = parent_tile.aliased_data.datatypes_1_child
        update_url = reverse(
            "arches_querysets:api-resource",
            kwargs={"graph": "datatype_lookups", "pk": str(self.resource_42.pk)},
        )

        def _nv(v):
            return v["node_value"] if isinstance(v, dict) else v

        self.client.login(username="dev", password="dev")
        # First PUT: insert; response must reflect the inserted values.
        insert_response = self.client.put(
            update_url,
            {
                "aliased_data": {
                    "datatypes_1": {
                        "tileid": str(parent_tile.pk),
                        "resourceinstance": str(self.resource_42.pk),
                        "aliased_data": {
                            "non_localized_string_alias": "initial-1-1-parent",
                            "datatypes_1_child": {
                                "tileid": str(child_tile.pk),
                                "resourceinstance": str(self.resource_42.pk),
                                "aliased_data": {
                                    "non_localized_string_alias_child": "initial-1-1-child"
                                },
                            },
                        },
                    },
                },
            },
            content_type="application/json",
        )
        self.assertEqual(
            insert_response.status_code, HTTPStatus.OK, insert_response.json()
        )
        insert_parent = insert_response.json()["aliased_data"]["datatypes_1"]
        self.assertEqual(
            _nv(insert_parent["aliased_data"]["non_localized_string_alias"]),
            "initial-1-1-parent",
        )
        insert_child = insert_parent["aliased_data"]["datatypes_1_child"]
        self.assertEqual(
            _nv(insert_child["aliased_data"]["non_localized_string_alias_child"]),
            "initial-1-1-child",
            "Card-1 child must be fresh in resource PUT insert response (1→1)",
        )

        # Second PUT: update; response must reflect the new value, not the stale one.
        update_response = self.client.put(
            update_url,
            {
                "aliased_data": {
                    "datatypes_1": {
                        "tileid": str(parent_tile.pk),
                        "resourceinstance": str(self.resource_42.pk),
                        "aliased_data": {
                            "non_localized_string_alias": "put-1-1-parent",
                            "datatypes_1_child": {
                                "tileid": str(child_tile.pk),
                                "resourceinstance": str(self.resource_42.pk),
                                "aliased_data": {
                                    "non_localized_string_alias_child": "put-1-1-child"
                                },
                            },
                        },
                    },
                },
            },
            content_type="application/json",
        )
        self.assertEqual(
            update_response.status_code, HTTPStatus.OK, update_response.json()
        )
        update_parent = update_response.json()["aliased_data"]["datatypes_1"]
        self.assertEqual(
            _nv(update_parent["aliased_data"]["non_localized_string_alias"]),
            "put-1-1-parent",
        )
        update_child = update_parent["aliased_data"]["datatypes_1_child"]
        self.assertEqual(
            _nv(update_child["aliased_data"]["non_localized_string_alias_child"]),
            "put-1-1-child",
            "Card-1 child must be fresh in resource PUT update response (1→1)",
        )

    def test_insert_and_update_resource_put_1_n_parent_and_child(self):
        """PUT resource with card-1 parent + card-n child; response must reflect inserted/updated values (1→n)."""
        parent_tile = self.resource_42.aliased_data.datatypes_1
        child_tile = parent_tile.aliased_data.datatypes_1_n_child[0]
        update_url = reverse(
            "arches_querysets:api-resource",
            kwargs={"graph": "datatype_lookups", "pk": str(self.resource_42.pk)},
        )

        def _nv(v):
            return v["node_value"] if isinstance(v, dict) else v

        self.client.login(username="dev", password="dev")
        # First PUT: insert; response must reflect the inserted values.
        insert_response = self.client.put(
            update_url,
            {
                "aliased_data": {
                    "datatypes_1": {
                        "tileid": str(parent_tile.pk),
                        "resourceinstance": str(self.resource_42.pk),
                        "aliased_data": {
                            "non_localized_string_alias": "initial-1-n-parent",
                            "datatypes_1_n_child": [
                                {
                                    "tileid": str(child_tile.pk),
                                    "resourceinstance": str(self.resource_42.pk),
                                    "aliased_data": {
                                        "non_localized_string_alias_1_n_child": "initial-1-n-child"
                                    },
                                }
                            ],
                        },
                    },
                },
            },
            content_type="application/json",
        )
        self.assertEqual(
            insert_response.status_code, HTTPStatus.OK, insert_response.json()
        )
        insert_parent = insert_response.json()["aliased_data"]["datatypes_1"]
        self.assertEqual(
            _nv(insert_parent["aliased_data"]["non_localized_string_alias"]),
            "initial-1-n-parent",
        )
        insert_children = insert_parent["aliased_data"]["datatypes_1_n_child"]
        self.assertEqual(len(insert_children), 1)
        self.assertEqual(
            _nv(
                insert_children[0]["aliased_data"][
                    "non_localized_string_alias_1_n_child"
                ]
            ),
            "initial-1-n-child",
            "Card-n child must be fresh in resource PUT insert response (1→n)",
        )

        # Second PUT: update; response must reflect the new value, not the stale one.
        update_response = self.client.put(
            update_url,
            {
                "aliased_data": {
                    "datatypes_1": {
                        "tileid": str(parent_tile.pk),
                        "resourceinstance": str(self.resource_42.pk),
                        "aliased_data": {
                            "non_localized_string_alias": "put-1-n-parent",
                            "datatypes_1_n_child": [
                                {
                                    "tileid": str(child_tile.pk),
                                    "resourceinstance": str(self.resource_42.pk),
                                    "aliased_data": {
                                        "non_localized_string_alias_1_n_child": "put-1-n-child"
                                    },
                                }
                            ],
                        },
                    },
                },
            },
            content_type="application/json",
        )
        self.assertEqual(
            update_response.status_code, HTTPStatus.OK, update_response.json()
        )
        update_parent = update_response.json()["aliased_data"]["datatypes_1"]
        self.assertEqual(
            _nv(update_parent["aliased_data"]["non_localized_string_alias"]),
            "put-1-n-parent",
        )
        update_children = update_parent["aliased_data"]["datatypes_1_n_child"]
        self.assertEqual(len(update_children), 1)
        self.assertEqual(
            _nv(
                update_children[0]["aliased_data"][
                    "non_localized_string_alias_1_n_child"
                ]
            ),
            "put-1-n-child",
            "Card-n child must be fresh in resource PUT update response (1→n)",
        )

    def test_insert_and_update_resource_put_n_1_parent_and_child(self):
        """PUT resource with card-n parent + card-1 child; response must reflect inserted/updated values (n→1)."""
        parent_tile = self.resource_42.aliased_data.datatypes_n[0]
        child_tile = parent_tile.aliased_data.datatypes_n_1_child
        update_url = reverse(
            "arches_querysets:api-resource",
            kwargs={"graph": "datatype_lookups", "pk": str(self.resource_42.pk)},
        )

        def _nv(v):
            return v["node_value"] if isinstance(v, dict) else v

        self.client.login(username="dev", password="dev")
        # First PUT: insert; response must reflect the inserted values.
        insert_response = self.client.put(
            update_url,
            {
                "aliased_data": {
                    "datatypes_n": [
                        {
                            "tileid": str(parent_tile.pk),
                            "resourceinstance": str(self.resource_42.pk),
                            "aliased_data": {
                                "non_localized_string_alias_n": "initial-n-1-parent",
                                "datatypes_n_1_child": {
                                    "tileid": str(child_tile.pk),
                                    "resourceinstance": str(self.resource_42.pk),
                                    "aliased_data": {
                                        "non_localized_string_alias_n_1_child": "initial-n-1-child"
                                    },
                                },
                            },
                        }
                    ],
                },
            },
            content_type="application/json",
        )
        self.assertEqual(
            insert_response.status_code, HTTPStatus.OK, insert_response.json()
        )
        insert_parents = insert_response.json()["aliased_data"]["datatypes_n"]
        self.assertEqual(len(insert_parents), 1)
        self.assertEqual(
            _nv(insert_parents[0]["aliased_data"]["non_localized_string_alias_n"]),
            "initial-n-1-parent",
        )
        insert_child = insert_parents[0]["aliased_data"]["datatypes_n_1_child"]
        self.assertEqual(
            _nv(insert_child["aliased_data"]["non_localized_string_alias_n_1_child"]),
            "initial-n-1-child",
            "Card-1 child must be fresh in resource PUT insert response (n→1)",
        )

        # Second PUT: update; response must reflect the new value, not the stale one.
        update_response = self.client.put(
            update_url,
            {
                "aliased_data": {
                    "datatypes_n": [
                        {
                            "tileid": str(parent_tile.pk),
                            "resourceinstance": str(self.resource_42.pk),
                            "aliased_data": {
                                "non_localized_string_alias_n": "put-n-1-parent",
                                "datatypes_n_1_child": {
                                    "tileid": str(child_tile.pk),
                                    "resourceinstance": str(self.resource_42.pk),
                                    "aliased_data": {
                                        "non_localized_string_alias_n_1_child": "put-n-1-child"
                                    },
                                },
                            },
                        }
                    ],
                },
            },
            content_type="application/json",
        )
        self.assertEqual(
            update_response.status_code, HTTPStatus.OK, update_response.json()
        )
        update_parents = update_response.json()["aliased_data"]["datatypes_n"]
        self.assertEqual(len(update_parents), 1)
        self.assertEqual(
            _nv(update_parents[0]["aliased_data"]["non_localized_string_alias_n"]),
            "put-n-1-parent",
        )
        update_child = update_parents[0]["aliased_data"]["datatypes_n_1_child"]
        self.assertEqual(
            _nv(update_child["aliased_data"]["non_localized_string_alias_n_1_child"]),
            "put-n-1-child",
            "Card-1 child must be fresh in resource PUT update response (n→1)",
        )

    def test_client_supplied_tileid_survives_new_cardinality_n_tile_via_resource_put(
        self,
    ):
        client_tileid = str(uuid.uuid4())
        parent_tile = self.resource_42.aliased_data.datatypes_1
        update_url = reverse(
            "arches_querysets:api-resource",
            kwargs={"graph": "datatype_lookups", "pk": str(self.resource_42.pk)},
        )
        request_body = {
            "aliased_data": {
                "datatypes_1": {
                    "tileid": str(parent_tile.pk),
                    "resourceinstance": str(self.resource_42.pk),
                    "aliased_data": {
                        "datatypes_1_n_child": [
                            {
                                "tileid": client_tileid,
                                "resourceinstance": str(self.resource_42.pk),
                                "aliased_data": {
                                    "non_localized_string_alias_1_n_child": "verify_tileid_value"
                                },
                            }
                        ],
                    },
                },
            },
        }
        self.client.login(username="dev", password="dev")
        response = self.client.put(
            update_url, request_body, content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)

        def _nv(v):
            return v["node_value"] if isinstance(v, dict) else v

        new_children = response.json()["aliased_data"]["datatypes_1"]["aliased_data"][
            "datatypes_1_n_child"
        ]
        matching = [
            child
            for child in new_children
            if _nv(child["aliased_data"]["non_localized_string_alias_1_n_child"])
            == "verify_tileid_value"
        ]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["tileid"], client_tileid)

    def test_update_tile_with_new_file_upload_on_existing_tile(self):
        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            file_node_id = str(
                Node.objects.get(graph=self.graph, alias="file_list_alias").pk
            )
            pre_existing_file = File.objects.create(path="uploadedfiles/existing.jpg")

            update_url = reverse(
                "arches_querysets:api-tile",
                kwargs={
                    "graph": "datatype_lookups",
                    "nodegroup_alias": "datatypes_1",
                    "pk": self.resource_42.aliased_data.datatypes_1.pk,
                },
            )
            request_body = {
                "aliased_data": {
                    "file_list_alias": [
                        {
                            "name": "existing.jpg",
                            "file_id": str(pre_existing_file.pk),
                            "url": f"/files/{pre_existing_file.pk}",
                        },
                        {"name": "new_photo.jpg", "type": "image/jpeg"},
                    ],
                },
                "resourceinstance": str(self.resource_42.pk),
            }
            encoded_body = encode_multipart(
                BOUNDARY,
                {
                    "json": json.dumps(request_body),
                    f"file-list_{file_node_id}": SimpleUploadedFile(
                        "new_photo.jpg", b"fake-image-bytes", content_type="image/jpeg"
                    ),
                },
            )

            self.client.login(username="dev", password="dev")
            response = self.client.patch(
                update_url, encoded_body, content_type=MULTIPART_CONTENT
            )

            self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
            updated_files = response.json()["aliased_data"]["file_list_alias"][
                "node_value"
            ]
            self.assertEqual(len(updated_files), 2)

            existing_entry = next(
                file_entry
                for file_entry in updated_files
                if file_entry["name"] == "existing.jpg"
            )
            new_entry = next(
                file_entry
                for file_entry in updated_files
                if file_entry["name"] == "new_photo.jpg"
            )

            # The pre-existing entry and its File row are untouched.
            self.assertEqual(existing_entry["file_id"], str(pre_existing_file.pk))
            self.assertTrue(File.objects.filter(pk=pre_existing_file.pk).exists())

            # The new upload is linked to a real File row with the uploaded
            # content, not left pointing at a phantom/nonexistent file.
            self.assertIsNotNone(new_entry["file_id"])
            new_file_model = File.objects.get(pk=new_entry["file_id"])
            self.assertEqual(new_file_model.path.read(), b"fake-image-bytes")

            # No orphans: exactly the pre-existing File row plus the new one.
            self.assertEqual(File.objects.count(), 2)

    def test_update_tile_removes_file_dropped_from_list(self):
        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            kept_file = File.objects.create(path="uploadedfiles/kept.jpg")
            dropped_file = File.objects.create(path="uploadedfiles/dropped.jpg")

            update_url = reverse(
                "arches_querysets:api-tile",
                kwargs={
                    "graph": "datatype_lookups",
                    "nodegroup_alias": "datatypes_1",
                    "pk": self.resource_42.aliased_data.datatypes_1.pk,
                },
            )
            self.client.login(username="dev", password="dev")

            # Establish real, persisted tile state with two files.
            seed_body = {
                "aliased_data": {
                    "file_list_alias": [
                        {
                            "name": "kept.jpg",
                            "file_id": str(kept_file.pk),
                            "url": f"/files/{kept_file.pk}",
                        },
                        {
                            "name": "dropped.jpg",
                            "file_id": str(dropped_file.pk),
                            "url": f"/files/{dropped_file.pk}",
                        },
                    ],
                },
                "resourceinstance": str(self.resource_42.pk),
            }
            seed_response = self.client.patch(
                update_url, seed_body, content_type="application/json"
            )
            self.assertEqual(
                seed_response.status_code, HTTPStatus.OK, seed_response.content
            )

            # Drop dropped.jpg from the list.
            update_body = {
                "aliased_data": {
                    "file_list_alias": [
                        {
                            "name": "kept.jpg",
                            "file_id": str(kept_file.pk),
                            "url": f"/files/{kept_file.pk}",
                        },
                    ],
                },
                "resourceinstance": str(self.resource_42.pk),
            }
            response = self.client.patch(
                update_url, update_body, content_type="application/json"
            )
            self.assertEqual(response.status_code, HTTPStatus.OK, response.content)

            updated_files = response.json()["aliased_data"]["file_list_alias"][
                "node_value"
            ]
            self.assertEqual(len(updated_files), 1)
            self.assertEqual(updated_files[0]["name"], "kept.jpg")

            self.assertTrue(File.objects.filter(pk=kept_file.pk).exists())
            self.assertFalse(File.objects.filter(pk=dropped_file.pk).exists())

    @unittest.skipIf(arches_version < Version("8.0"), reason="Arches 8+ only logic")
    def test_out_of_date_resource(self):
        Graph.objects.get(pk=self.graph.pk).publish(user=None)

        update_url = reverse(
            "arches_querysets:api-resource",
            kwargs={"graph": "datatype_lookups", "pk": str(self.resource_42.pk)},
        )
        self.client.login(username="dev", password="dev")
        request_body = {"aliased_data": {"datatypes_1": None}}
        response = self.client.put(
            update_url, request_body, content_type="application/json"
        )
        self.assertContains(
            response,
            "Graph Has Different Publication",
            status_code=HTTPStatus.BAD_REQUEST,
        )

    def test_instantiate_empty_resource_serializer(self):
        serializer = ArchesResourceSerializer(graph_slug="datatype_lookups")
        self.assertIsNone(serializer.data["resourceinstanceid"])
        # Default values are stocked.
        self.assertEqual(
            serializer.data["aliased_data"]["datatypes_1"]["aliased_data"][
                "number_alias"
            ]["node_value"],
            7,
        )

    def test_instantiate_empty_tile_serializer(self):
        serializer = ArchesTileSerializer(
            graph_slug="datatype_lookups", nodegroup_alias="datatypes_1"
        )
        self.assertIsNone(serializer.data["tileid"])
        # Default values are stocked.
        self.assertEqual(
            serializer.data["aliased_data"]["number_alias"]["node_value"], 7
        )

    def test_bind_data_to_serializer(self):
        # Get some default data from the serializer.
        static_data = ArchesTileSerializer(
            graph_slug="datatype_lookups", nodegroup_alias="datatypes_1"
        ).data
        # Pretend that data came from somewhere else, and process it, e.g. in a script.
        serializer = ArchesTileSerializer(
            graph_slug="datatype_lookups",
            nodegroup_alias="datatypes_1",
            data=static_data,
        )
        self.assertTrue(serializer.is_valid())

        # Or, submit it to the API
        self.client.login(username="dev", password="dev")
        create_url = reverse(
            "arches_querysets:api-tiles",
            kwargs={"graph": "datatype_lookups", "nodegroup_alias": "datatypes_1"},
        )
        response = self.client.post(
            create_url, serializer.data, content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_exclude_children_option(self):
        serializer = ArchesResourceSerializer(graph_slug="datatype_lookups")
        self.assertIn(
            "datatypes_1_child",
            serializer.data["aliased_data"]["datatypes_1"]["aliased_data"],
        )
        serializer = ArchesResourceTopNodegroupsSerializer(
            graph_slug="datatype_lookups"
        )
        self.assertNotIn(
            "datatypes_1_child",
            serializer.data["aliased_data"]["datatypes_1"]["aliased_data"],
        )
        serializer = ArchesTileSerializer(
            graph_slug="datatype_lookups", nodegroup_alias="datatypes_1"
        )
        self.assertIn("datatypes_1_child", serializer.data["aliased_data"])
        serializer = ArchesSingleNodegroupSerializer(
            graph_slug="datatype_lookups", nodegroup_alias="datatypes_1"
        )
        self.assertNotIn("datatypes_1_child", serializer.data["aliased_data"])

    def test_blank_views_tile_id(self):
        response = self.client.get(
            reverse(
                "arches_querysets:api-tile-blank",
                kwargs={"graph": "datatype_lookups", "nodegroup_alias": "datatypes_1"},
            )
        )
        self.assertIsNone(response.json()["tileid"])

    def test_blank_views_exclude_children_option(self):
        response = self.client.get(
            reverse(
                "arches_querysets:api-resource-blank",
                kwargs={"graph": "datatype_lookups"},
            )
        )
        self.assertContains(response, "datatypes_1_child")

        response = self.client.get(
            reverse(
                "arches_querysets:api-resource-blank",
                kwargs={"graph": "datatype_lookups"},
            ),
            QUERY_STRING="exclude_children=true",
        )
        self.assertNotContains(response, "datatypes_1_child")

        response = self.client.get(
            reverse(
                "arches_querysets:api-tile-blank",
                kwargs={"graph": "datatype_lookups", "nodegroup_alias": "datatypes_1"},
            )
        )
        self.assertContains(response, "datatypes_1_child")

        response = self.client.get(
            reverse(
                "arches_querysets:api-tile-blank",
                kwargs={
                    "graph": "datatype_lookups",
                    "nodegroup_alias": "datatypes_1",
                },
            ),
            QUERY_STRING="exclude_children=true",
        )
        self.assertNotContains(response, "datatypes_1_child")

    def test_fill_blanks_option(self):
        self.resource_42.tilemodel_set.all().delete()
        response = self.client.get(
            reverse(
                "arches_querysets:api-resource",
                kwargs={"graph": "datatype_lookups", "pk": str(self.resource_42.pk)},
            ),
            QUERY_STRING="fill_blanks=true",
        )
        parent_data = response.json()["aliased_data"]["datatypes_1"]
        self.assertIsNone(parent_data["tileid"])
        child_data = parent_data["aliased_data"]["datatypes_1_child"]
        self.assertIsNone(child_data["tileid"])

    @patch(
        "arches.app.models.models.UserProfile.viewable_nodegroups",
        MUTABLE_PERMITTED_NODEGROUPS,
    )
    def test_serializer_observes_nodegroup_permissions(self):
        resource_serializer = ArchesResourceSerializer(graph_slug="datatype_lookups")
        self.assertNotIn("datatypes_1", resource_serializer.data["aliased_data"])

        # A TileSerializer where the topmost nodegroup is not permitted raises
        tile_serializer = ArchesTileSerializer(
            graph_slug="datatype_lookups", nodegroup_alias="datatypes_1"
        )
        with self.assertRaises(PermissionError):
            tile_serializer.data

        # Otherwise we just return whatever part of the tree we can.
        MUTABLE_PERMITTED_NODEGROUPS.add(str(self.nodegroup_1.pk))
        tile_serializer = ArchesTileSerializer(
            graph_slug="datatype_lookups", nodegroup_alias="datatypes_1"
        )
        self.assertIn("number_alias", tile_serializer.data["aliased_data"])
        self.assertNotIn("datatypes_1_child", tile_serializer.data["aliased_data"])

    def test_filter_kwargs(self):
        node_alias = "string_alias"

        response = self.client.get(
            reverse(
                "arches_querysets:api-resources",
                kwargs={"graph": "datatype_lookups"},
            ),
            # Additional lookups tested in test_lookups.py
            QUERY_STRING=f"aliased_data__{node_alias}__any_lang_icontains=forty",
        )
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            response.json()["results"][0]["resourceinstanceid"],
            str(self.resource_42.pk),
        )

        response = self.client.get(
            reverse(
                "arches_querysets:api-tiles",
                kwargs={"graph": "datatype_lookups", "nodegroup_alias": "datatypes_1"},
            ),
            QUERY_STRING=f"aliased_data__{node_alias}__any_lang_icontains=forty",
        )
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            response.json()["results"][0]["resourceinstance"], str(self.resource_42.pk)
        )

        node_alias = "string_alias_n"
        response = self.client.get(
            reverse(
                "arches_querysets:api-tiles",
                kwargs={"graph": "datatype_lookups", "nodegroup_alias": "datatypes_n"},
            ),
            QUERY_STRING=f"aliased_data__{node_alias}__isnull=true",
        )
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            response.json()["results"][0]["resourceinstance"],
            str(self.resource_none.pk),
        )

    def test_filter_kwargs_disallows_joins(self):
        self.assertContains(
            self.client.get(
                reverse(
                    "arches_querysets:api-resources",
                    kwargs={"graph": "datatype_lookups"},
                ),
                QUERY_STRING=f"aliased_data__principaluser__username=dev",
            ),
            "Invalid filter param: principaluser",
            status_code=HTTPStatus.BAD_REQUEST,
        )

    def test_bogus_graph_slug(self):
        response = self.client.get(
            reverse("arches_querysets:api-resources", kwargs={"graph": "bogus"})
        )
        self.assertContains(
            response,
            "No nodes found for graph slug",
            status_code=HTTPStatus.BAD_REQUEST,
        )
        response = self.client.get(
            reverse(
                "arches_querysets:api-tiles",
                kwargs={"graph": "bogus", "nodegroup_alias": "bogus"},
            )
        )
        self.assertContains(
            response,
            "No nodes found for graph slug",
            status_code=HTTPStatus.BAD_REQUEST,
        )


class RestFrameworkPerformanceTests(GraphTestCase):
    @patch(
        "arches.extensions.querysets.rest_framework.serializers.get_nodegroup_alias_lookup"
    )
    def test_derivation_of_nodegroup_aliases(self, mocked_util):
        """Querying nodegroup aliases should only be done once in the view layer,
        not multiple times when building nested serializers. The serializer layer
        still has fallback code to support scripts, see test_bind_data_to_serializer(),
        but it shouldn't be called when using views.
        """
        self.client.get(
            reverse(
                "arches_querysets:api-resources", kwargs={"graph": "datatype_lookups"}
            )
        )
        mocked_util.assert_not_called()

    def test_resource_list_view_performance(self):
        # 1: auth
        # 2: auth groups
        # 3: node alias lookup in get_tiles()
        # 4-16: PerformanceTests.test_get_graph_objects()
        # 17: resource count (paginator)
        # 18: select resources limit 500
        # 19: tile depth 1
        # 20: tile depth 2
        # 21: tile depth 3: none!
        # 22-25: arches perms (BUG: core arches)
        num_queries = 25
        if arches_version < Version("8.1.0a0"):
            num_queries += 1  # extra user profile query on Arches 8.0 and below.
        if arches_version < Version("8.2.0a8"):
            num_queries += 1  # extra django-guardian query below 3.3.2.
        with self.assertNumQueries(num_queries):
            response = self.client.get(
                reverse(
                    "arches_querysets:api-resources",
                    kwargs={"graph": "datatype_lookups"},
                ),
                # Some datatypes are inefficient in fetching data for display values,
                # e.g. nodes, so make sure we're getting the resource with only Nones
                QUERY_STRING="aliased_data__number_alias__isnull=true",
            )
        self.assertContains(response, "datatypes_1_child", status_code=HTTPStatus.OK)
        self.assertEqual(response.json()["count"], 1)
        top_tile = response.json()["results"][0]["aliased_data"]["datatypes_1"]
        self.assertIsNone(top_tile["aliased_data"]["number_alias"]["node_value"])

    def test_tile_list_view_performance(self):
        # 1: auth
        # 2: auth groups
        # 3: node alias lookup in get_tiles()
        # 4-16: PerformanceTests.test_get_graph_objects()
        # 17: tile count (paginator)
        # 18: select tiles limit 500
        # 19: tile depth 2
        # 20: tile depth 3: none!
        # 21-24: arches perms (BUG: core arches)
        num_queries = 24
        if arches_version < Version("8.1.0a0"):
            num_queries += 1  # extra user profile query on Arches 8.0 and below.
        if arches_version < Version("8.2.0a8"):
            num_queries += 1  # extra django-guardian query below 3.3.2.
        with self.assertNumQueries(num_queries):
            response = self.client.get(
                reverse(
                    "arches_querysets:api-tiles",
                    kwargs={
                        "graph": "datatype_lookups",
                        "nodegroup_alias": "datatypes_1",
                    },
                ),
                # Some datatypes are inefficient in fetching data for display values,
                # e.g. nodes, so make sure we're getting the resource with only Nones
                QUERY_STRING="aliased_data__number_alias__isnull=true",
            )
        self.assertContains(response, "datatypes_1_child", status_code=HTTPStatus.OK)
        self.assertEqual(response.json()["count"], 1)
        top_tile = response.json()["results"][0]
        self.assertIsNone(top_tile["aliased_data"]["number_alias"]["node_value"])

    def test_resource_blank_view_performance(self):
        # 1-4: perms
        # 5: get_nodegroup_alias_lookup()
        # 6-10: NodeFetcherMixin._find_graph_nodes()
        num_queries = 10
        if arches_version < Version("8.1.0a0"):
            num_queries += 1  # extra user profile query on Arches 8.0 and below.
        if arches_version < Version("8.2.0a8"):
            num_queries += 1  # extra django-guardian query below 3.3.2.
        with self.assertNumQueries(num_queries):
            response = self.client.get(
                reverse(
                    "arches_querysets:api-resource-blank",
                    kwargs={"graph": "datatype_lookups"},
                )
            )
        self.assertContains(response, "datatypes_1_child")
