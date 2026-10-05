"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import json
import os
from http import HTTPStatus

from django.contrib.auth.models import Group, Permission, User
from django.urls import reverse
from guardian.models import GroupObjectPermission

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph
from tests import test_settings
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.views.graph_permission_tests --settings="tests.test_settings"

GRAPH_FIXTURE = os.path.join(
    list(test_settings.RESOURCE_GRAPH_LOCATIONS)[0], "Cardinality Test Model.json"
)


class NodegroupPermissionTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        with open(GRAPH_FIXTURE) as f:
            cls.graph_json = JSONDeserializer().deserialize(f.read())
        import_graph(cls.graph_json["graph"])
        cls.graph_id = cls.graph_json["graph"][0]["graphid"]
        graph = Graph.objects.get(pk=cls.graph_id)
        if not graph.publication_id:
            graph.publish()
        cls.nodegroup_id = str(
            models.Node.objects.filter(graph_id=cls.graph_id, nodegroup__isnull=False)
            .values_list("nodegroup_id", flat=True)
            .first()
        )
        cls.group = Group.objects.create(name="Nodegroup Permission Test Group")
        cls.user = User.objects.create_user("nodegroup_perm_user", "", "password")
        cls.user.groups.add(cls.group)

    def setUp(self):
        self.client.login(username="admin", password="admin")

    def apply(self, codenames, method="post", identity=None):
        payload = {
            "selectedIdentities": [identity or {"type": "group", "id": self.group.pk}],
            "selectedCards": [{"nodegroupid": self.nodegroup_id}],
            "selectedPermissions": [{"codename": codename} for codename in codenames],
        }
        return getattr(self.client, method)(
            reverse("permission_data"),
            data=json.dumps(payload),
            content_type="application/json",
        )

    def group_codenames(self):
        return set(
            GroupObjectPermission.objects.filter(
                group=self.group, object_pk=self.nodegroup_id
            ).values_list("permission__codename", flat=True)
        )

    def published_group_codenames(self):
        graph = Graph.objects.get(pk=self.graph_id)
        published_graphs = models.PublishedGraph.objects.filter(
            publication_id=graph.publication_id
        )
        self.assertTrue(published_graphs.exists())
        results = []
        for published_graph in published_graphs:
            perms = published_graph.serialized_graph["group_permissions"].get(
                self.nodegroup_id, []
            )
            permission_ids = [
                perm["permission_id"]
                for perm in perms
                if perm["group_id"] == self.group.pk
            ]
            results.append(
                set(
                    Permission.objects.filter(pk__in=permission_ids).values_list(
                        "codename", flat=True
                    )
                )
            )
        return results

    def test_apply_permissions_updates_published_snapshot(self):
        response = self.apply(["read_nodegroup"])
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.group_codenames(), {"read_nodegroup"})
        for codenames in self.published_group_codenames():
            self.assertEqual(codenames, {"read_nodegroup"})

        response = self.apply([], method="delete")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.group_codenames(), set())
        for codenames in self.published_group_codenames():
            self.assertEqual(codenames, set())

    def test_apply_permissions_does_not_set_unpublished_changes(self):
        self.apply(["read_nodegroup"])
        graph = Graph.objects.get(pk=self.graph_id)
        self.assertFalse(graph.has_unpublished_changes)

    def test_rejects_no_access_combined_with_other_perms(self):
        response = self.apply(["no_access_to_nodegroup", "read_nodegroup"])
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(self.group_codenames(), set())

    def test_rejects_invalid_codename(self):
        response = self.apply(["delete_graphmodel"])
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(self.group_codenames(), set())

    def get_permissions(self, identity_type, identity_id):
        response = self.client.get(
            reverse("permission_data"),
            {
                "nodegroupIds": json.dumps([self.nodegroup_id]),
                "identityType": identity_type,
                "identityId": identity_id,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        return json.loads(response.content)[0]

    def test_get_permissions_reports_sources(self):
        result = self.get_permissions("user", self.user.pk)
        self.assertEqual(result["source"], "default")
        self.assertEqual(result["explicit"], [])

        self.apply(["read_nodegroup"])

        result = self.get_permissions("group", self.group.pk)
        self.assertEqual(result["source"], "group")
        self.assertEqual(
            [perm["codename"] for perm in result["explicit"]], ["read_nodegroup"]
        )

        result = self.get_permissions("user", self.user.pk)
        self.assertEqual(result["source"], "group:" + self.group.name)
        self.assertEqual(result["explicit"], [])
        self.assertEqual(
            [perm["codename"] for perm in result["effective"]], ["read_nodegroup"]
        )
        self.assertEqual(
            [perm["codename"] for perm in result["perms"]], ["read_nodegroup"]
        )

        self.apply(
            ["no_access_to_nodegroup"], identity={"type": "user", "id": self.user.pk}
        )
        result = self.get_permissions("user", self.user.pk)
        self.assertEqual(result["source"], "user")
        self.assertEqual(
            [perm["codename"] for perm in result["effective"]],
            ["no_access_to_nodegroup"],
        )

    def test_publish_draft_preserves_live_permissions(self):
        graph = Graph.objects.get(pk=self.graph_id)
        graph.create_draft_graph()

        self.apply(["read_nodegroup", "write_nodegroup"])

        graph = Graph.objects.get(pk=self.graph_id)
        graph.promote_draft_graph_to_active_graph()

        self.assertEqual(self.group_codenames(), {"read_nodegroup", "write_nodegroup"})
        for codenames in self.published_group_codenames():
            self.assertEqual(codenames, {"read_nodegroup", "write_nodegroup"})

    def test_revert_all_changes_preserves_live_permissions(self):
        self.apply(["read_nodegroup"])

        graph = Graph.objects.get(pk=self.graph_id)
        published_graph = graph.get_published_graph()
        graph.restore_state_from_serialized_graph(published_graph.serialized_graph)

        self.assertEqual(self.group_codenames(), {"read_nodegroup"})

    def test_import_new_graph_applies_permissions(self):
        self.apply(["read_nodegroup"])
        graph = Graph.objects.get(pk=self.graph_id)
        exported = JSONDeserializer().deserialize(
            JSONSerializer().serialize(graph.serialize(force_recalculation=True))
        )
        self.assertTrue(exported["group_permissions"].get(self.nodegroup_id))

        graph.delete()
        GroupObjectPermission.objects.filter(object_pk=self.nodegroup_id).delete()
        self.assertFalse(Graph.objects.filter(pk=self.graph_id).exists())

        import_graph([exported])

        self.assertEqual(self.group_codenames(), {"read_nodegroup"})
