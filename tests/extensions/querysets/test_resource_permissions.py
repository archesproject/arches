import uuid
from contextlib import contextmanager
from unittest import mock

from django.contrib.auth.models import Group, User
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from arches.app.models.models import (
    ResourceInstance,
    ResourceInstanceLifecycleState,
    TileModel,
)
from arches.app.models.system_settings import settings as arches_settings
from arches.app.permissions.arches_default_allow import (
    ArchesDefaultAllowPermissionFramework,
)
from arches.app.permissions.arches_default_deny import (
    ArchesDefaultDenyPermissionFramework,
)
from arches.app.utils import permission_backend

from arches.extensions.querysets.utils.permissions import (
    DEFAULT_ALLOW_PERMISSION_FRAMEWORK,
    filter_readable_resources,
)
from arches.extensions.querysets.utils.tests import GraphTestCase

DEFAULT_DENY_PERMISSION_FRAMEWORK = (
    "arches_default_deny.ArchesDefaultDenyPermissionFramework"
)


@contextmanager
def permission_framework(dotted_path, framework):
    original_dotted_path = arches_settings.PERMISSION_FRAMEWORK
    arches_settings.PERMISSION_FRAMEWORK = dotted_path
    try:
        with mock.patch.object(permission_backend, "_PERMISSION_FRAMEWORK", framework):
            yield
    finally:
        arches_settings.PERMISSION_FRAMEWORK = original_dotted_path


class ResourcePermissionTests(GraphTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user("related_resource_reader", password="x")
        cls.user.groups.add(
            *Group.objects.filter(name__in=["Resource Editor", "Resource Reviewer"])
        )
        cls.admin = User.objects.get(username="admin")

        cls.unreadable_resource = cls.create_resource("Unreadable Resource")
        TileModel.objects.create(
            nodegroup=cls.nodegroup_1, resourceinstance=cls.unreadable_resource, data={}
        )
        framework = ArchesDefaultDenyPermissionFramework()
        framework.assign_perm("view_resourceinstance", cls.user, cls.resource_42)
        framework.assign_perm("change_resourceinstance", cls.user, cls.resource_42)

        resource_instance_datatype = cls.datatype_factory.get_instance(
            "resource-instance"
        )
        cls.unreadable_reference = resource_instance_datatype.transform_value_for_tile(
            cls.unreadable_resource
        )[0]
        cls.readable_reference = resource_instance_datatype.transform_value_for_tile(
            cls.resource_42
        )[0]
        cls.missing_reference = resource_instance_datatype.from_id_string(
            str(uuid.uuid4())
        )

        cls.cardinality_1_tile.data[str(cls.resource_instance_node_1.pk)] = [
            cls.unreadable_reference
        ]
        cls.cardinality_1_tile.data[str(cls.resource_instance_list_node_1.pk)] = [
            cls.unreadable_reference,
            cls.readable_reference,
        ]
        cls.cardinality_1_tile.save()
        cls.cardinality_n_tile.data[str(cls.resource_instance_list_node_n.pk)] = [
            cls.readable_reference,
            cls.missing_reference,
        ]
        cls.cardinality_n_tile.save()
        cls.resource_instance_list_node_1.config["graphs"] = [
            {"graphid": str(cls.graph.pk)}
        ]
        cls.resource_instance_list_node_1.save()

    @classmethod
    def create_resource(cls, name):
        return ResourceInstance.objects.create(
            graph=cls.graph,
            descriptors={"en": {"name": name}},
            name=name,
            graph_publication=cls.graph.publication,
            resource_instance_lifecycle_state=ResourceInstanceLifecycleState.objects.first(),
        )

    def setUp(self):
        self.enterContext(
            permission_framework(
                DEFAULT_DENY_PERMISSION_FRAMEWORK,
                ArchesDefaultDenyPermissionFramework(),
            )
        )

    def get_resource_response(self, user):
        self.client.force_login(user)
        return self.client.get(
            reverse(
                "arches_querysets:api-resource",
                kwargs={"graph": "datatype_lookups", "pk": str(self.resource_42.pk)},
            )
        )

    def get_cardinality_1_values(self, response):
        self.assertEqual(response.status_code, 200, response.content)
        tile_data = response.json()["aliased_data"]["datatypes_1"]["aliased_data"]
        return (
            tile_data["resource_instance_alias"],
            tile_data["resource_instance_list_alias"],
        )

    def test_unreadable_related_resources_are_redacted(self):
        response = self.get_resource_response(self.user)
        single_value, list_value = self.get_cardinality_1_values(response)

        self.assertEqual(single_value["details"], [])
        self.assertEqual(single_value["display_value"], "")
        self.assertEqual(
            list_value["details"],
            [
                {
                    "resource_id": str(self.resource_42.pk),
                    "display_value": "Resource referencing 42",
                }
            ],
        )
        self.assertEqual(list_value["display_value"], "Resource referencing 42")
        self.assertNotContains(response, "Unreadable Resource")

    def test_node_values_keep_unreadable_references(self):
        single_value, list_value = self.get_cardinality_1_values(
            self.get_resource_response(self.user)
        )

        self.assertEqual(single_value["node_value"], [self.unreadable_reference])
        self.assertEqual(
            list_value["node_value"],
            [self.unreadable_reference, self.readable_reference],
        )

    def test_missing_related_resources_stay_visible(self):
        response = self.get_resource_response(self.user)

        self.assertEqual(response.status_code, 200, response.content)
        tile_data = response.json()["aliased_data"]["datatypes_n"][0]["aliased_data"]
        self.assertEqual(
            tile_data["resource_instance_list_alias_n"]["display_value"],
            "Resource referencing 42, Missing",
        )

    def test_superuser_and_default_allow_are_not_redacted(self):
        with self.subTest(user="superuser"):
            single_value, _ = self.get_cardinality_1_values(
                self.get_resource_response(self.admin)
            )
            self.assertEqual(single_value["display_value"], "Unreadable Resource")

        with (
            self.subTest(framework="default allow"),
            permission_framework(
                DEFAULT_ALLOW_PERMISSION_FRAMEWORK,
                ArchesDefaultAllowPermissionFramework(),
            ),
        ):
            single_value, _ = self.get_cardinality_1_values(
                self.get_resource_response(self.user)
            )
            self.assertEqual(single_value["display_value"], "Unreadable Resource")

    def test_readable_resources_need_a_readable_nodegroup_in_their_graph(self):
        ArchesDefaultDenyPermissionFramework().assign_perm(
            "view_resourceinstance", self.user, self.unreadable_resource
        )
        candidates = ResourceInstance.objects.filter(pk=self.unreadable_resource.pk)

        with mock.patch(
            "arches.app.models.models.UserProfile.viewable_nodegroups", set()
        ):
            self.assertFalse(filter_readable_resources(self.user, candidates).exists())
        self.assertTrue(filter_readable_resources(self.user, candidates).exists())

    def test_list_endpoints_omit_unreadable_resources(self):
        self.client.force_login(self.user)
        resource_response = self.client.get(
            reverse(
                "arches_querysets:api-resources", kwargs={"graph": "datatype_lookups"}
            )
        )
        tile_response = self.client.get(
            reverse(
                "arches_querysets:api-tiles",
                kwargs={"graph": "datatype_lookups", "nodegroup_alias": "datatypes_1"},
            )
        )

        self.assertEqual(resource_response.status_code, 200, resource_response.content)
        self.assertEqual(tile_response.status_code, 200, tile_response.content)
        self.assertEqual(
            [
                resource["resourceinstanceid"]
                for resource in resource_response.json()["results"]
            ],
            [str(self.resource_42.pk)],
        )
        self.assertEqual(
            {tile["resourceinstance"] for tile in tile_response.json()["results"]},
            {str(self.resource_42.pk)},
        )
        self.assertNotContains(resource_response, "Unreadable Resource")
        self.assertNotContains(tile_response, "Unreadable Resource")

    def test_relatable_resources_omit_unreadable_resources(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "arches_vue_components:api-relatable-resources",
                kwargs={
                    "graph": "datatype_lookups",
                    "node_alias": "resource_instance_list_alias",
                },
            ),
            {
                "initialValue": [
                    str(self.unreadable_resource.pk),
                    str(self.resource_42.pk),
                ]
            },
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            [record["resourceinstanceid"] for record in response.json()["data"]],
            [str(self.resource_42.pk)],
        )
        self.assertNotContains(response, "Unreadable Resource")

    def test_saving_returned_values_keeps_unreadable_references(self):
        single_value, list_value = self.get_cardinality_1_values(
            self.get_resource_response(self.user)
        )

        response = self.client.patch(
            reverse(
                "arches_querysets:api-tile",
                kwargs={
                    "graph": "datatype_lookups",
                    "nodegroup_alias": "datatypes_1",
                    "pk": self.cardinality_1_tile.pk,
                },
            )
            + "?index=false",
            {
                "aliased_data": {
                    "resource_instance_alias": single_value,
                    "resource_instance_list_alias": list_value,
                },
                "resourceinstance": str(self.resource_42.pk),
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertNotContains(response, "Unreadable Resource")
        stored_data = TileModel.objects.get(pk=self.cardinality_1_tile.pk).data
        self.assertEqual(
            [
                [reference["resourceId"] for reference in stored_data[str(node.pk)]]
                for node in (
                    self.resource_instance_node_1,
                    self.resource_instance_list_node_1,
                )
            ],
            [
                [str(self.unreadable_resource.pk)],
                [str(self.unreadable_resource.pk), str(self.resource_42.pk)],
            ],
        )

    def test_list_query_count_does_not_grow_with_results(self):
        self.client.force_login(self.user)
        url = reverse(
            "arches_querysets:api-resources", kwargs={"graph": "datatype_lookups"}
        )

        def get_list():
            with CaptureQueriesContext(connection) as queries:
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200, response.content)
            return response, len(queries)

        get_list()
        _, baseline_query_count = get_list()

        framework = ArchesDefaultDenyPermissionFramework()
        for index in range(10):
            resource = self.create_resource(f"Referencing {index}")
            framework.assign_perm("view_resourceinstance", self.user, resource)
            TileModel.objects.create(
                nodegroup=self.nodegroup_1,
                resourceinstance=resource,
                data={
                    str(self.resource_instance_list_node_1.pk): [
                        self.unreadable_reference,
                        self.readable_reference,
                    ]
                },
            )
        response, query_count = get_list()

        self.assertEqual(len(response.json()["results"]), 11)
        self.assertNotContains(response, "Unreadable Resource")
        self.assertEqual(query_count, baseline_query_count)
