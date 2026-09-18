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

from django.contrib.auth.models import Group
from django.test import override_settings

from arches.app.models.models import NodeGroup
from arches.app.models.graph import Graph
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.permission_backend import (
    assign_perm,
    remove_perm,
    get_nodegroups_by_perm,
)
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.permissions.permission_cache_invalidation_tests --settings="tests.test_settings"

LOCMEM_USER_PERMISSION_CACHE = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "user_permission": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-user-permission-cache",
    },
}


@override_settings(CACHES=LOCMEM_USER_PERMISSION_CACHE)
class PermissionCacheInvalidationTests(ArchesTestCase):
    graph_fixtures = ["Data_Type_Model"]
    data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_users()
        cls.user = cls.test_users["ben"]
        cls.group = Group.objects.get(pk=2)
        cls.legacy_load_testing_package()
        cls.nodegroup = NodeGroup.objects.filter(
            node__graph_id=cls.data_type_graphid
        ).first()

    def setUp(self):
        from django.core.cache import caches

        caches["user_permission"].clear()

    def test_assign_perm_invalidates_cache(self):
        # populate the cache with the pre-change (allowed) state
        self.assertIn(
            self.nodegroup.pk, get_nodegroups_by_perm(self.user, "read_nodegroup")
        )

        with self.captureOnCommitCallbacks(execute=True):
            assign_perm("no_access_to_nodegroup", self.group, self.nodegroup)

        self.assertNotIn(
            self.nodegroup.pk, get_nodegroups_by_perm(self.user, "read_nodegroup")
        )

    def test_remove_perm_invalidates_cache(self):
        with self.captureOnCommitCallbacks(execute=True):
            assign_perm("no_access_to_nodegroup", self.group, self.nodegroup)
        self.assertNotIn(
            self.nodegroup.pk, get_nodegroups_by_perm(self.user, "read_nodegroup")
        )

        with self.captureOnCommitCallbacks(execute=True):
            remove_perm("no_access_to_nodegroup", self.group, self.nodegroup)

        self.assertIn(
            self.nodegroup.pk, get_nodegroups_by_perm(self.user, "read_nodegroup")
        )

    def test_update_permissions_from_serialized_graph_invalidates_cache(self):
        graph = Graph.objects.get(pk=self.data_type_graphid)

        with self.captureOnCommitCallbacks(execute=True):
            assign_perm("no_access_to_nodegroup", self.group, self.nodegroup)
        self.assertNotIn(
            self.nodegroup.pk, get_nodegroups_by_perm(self.user, "read_nodegroup")
        )

        # a serialized snapshot with no explicit permissions for this nodegroup
        serialized_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(graph)
        )
        serialized_graph["group_permissions"] = {}
        serialized_graph["user_permissions"] = {}

        with self.captureOnCommitCallbacks(execute=True):
            graph.update_permissions_from_serialized_graph(serialized_graph)

        self.assertIn(
            self.nodegroup.pk, get_nodegroups_by_perm(self.user, "read_nodegroup")
        )

    def test_assign_perm_invalidates_group_keyed_cache_entry(self):
        # CachedObjectPermissionChecker stores group checkers under a
        # separate "g:{group.pk}" key in the same cache -- populate that
        # entry directly (not the user-keyed one) before the change.
        self.assertIn(
            self.nodegroup.pk, get_nodegroups_by_perm(self.group, "read_nodegroup")
        )

        with self.captureOnCommitCallbacks(execute=True):
            assign_perm("no_access_to_nodegroup", self.group, self.nodegroup)

        self.assertNotIn(
            self.nodegroup.pk, get_nodegroups_by_perm(self.group, "read_nodegroup")
        )

    def test_group_membership_change_invalidates_cache(self):
        assign_perm("no_access_to_nodegroup", self.group, self.nodegroup)
        self.assertNotIn(
            self.nodegroup.pk, get_nodegroups_by_perm(self.user, "read_nodegroup")
        )

        with self.captureOnCommitCallbacks(execute=True):
            self.user.groups.remove(self.group)

        self.assertIn(
            self.nodegroup.pk, get_nodegroups_by_perm(self.user, "read_nodegroup")
        )
