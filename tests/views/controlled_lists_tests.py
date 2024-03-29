import json
import uuid
from collections import defaultdict

from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.test.client import Client
from guardian.shortcuts import assign_perm

from arches.app.models.models import (
    ControlledList,
    ControlledListItem,
    ControlledListItemLabel,
    DValueType,
    GraphModel,
    Language,
    Node,
    NodeGroup,
)
from arches.app.views.controlled_lists import serialize
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.views.controlled_lists_tests --settings="tests.test_settings"


SYNCED_PK = uuid.uuid4()


def sync_pk_for_comparison(item):
    item.pk = SYNCED_PK
    return item


class ControlledListTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.admin = User.objects.get(username="admin")
        cls.anonymous = User.objects.get(username="anonymous")

        cls.rdm_user = User.objects.create_user(
            "test", "test@archesproject.org", "password"
        )
        rdm_admin_group = Group.objects.get(name="RDM Administrator")
        cls.rdm_user.groups.add(rdm_admin_group)

    @classmethod
    def setUpTestData(cls):
        # Create two lists.
        cls.list1 = ControlledList.objects.create(name="list1")
        # Second list has children (nested items).
        cls.list2 = ControlledList.objects.create(name="list2")

        cls.first_language = Language.objects.first()
        cls.pref_label = DValueType.objects.get(valuetype="prefLabel")
        cls.alt_label = DValueType.objects.get(valuetype="altLabel")

        # Create 5 labels per list. (10)
        ControlledListItem.objects.bulk_create(
            [
                ControlledListItem(
                    uri=f"https://archesproject.org/{num}",
                    controlled_list=cls.list1,
                    sortorder=num,
                )
                for num in range(5)
            ]
            + [
                ControlledListItem(
                    uri=f"https://getty.edu/{num}",
                    controlled_list=cls.list2,
                    sortorder=num,
                )
                for num in range(5)
            ]
        )

        parent = ControlledListItem.objects.get(
            controlled_list=cls.list2, uri="https://getty.edu/0"
        )
        for child in ControlledListItem.objects.filter(
            controlled_list=cls.list2
        ).exclude(pk=parent.pk):
            child.parent = parent
            child.save()

        # Create a prefLabel and altLabel per item. (20)
        ControlledListItemLabel.objects.bulk_create(
            [
                ControlledListItemLabel(
                    value=f"label{num}-pref",
                    language=cls.first_language,
                    value_type=cls.pref_label,
                    controlled_list_item=ControlledListItem.objects.filter(
                        controlled_list=cls.list1
                    )[num],
                )
                for num in range(5)
            ]
            + [
                ControlledListItemLabel(
                    value=f"label{num}-alt",
                    language=cls.first_language,
                    value_type=cls.alt_label,
                    controlled_list_item=ControlledListItem.objects.filter(
                        controlled_list=cls.list1
                    )[num],
                )
                for num in range(5)
            ]
            + [
                ControlledListItemLabel(
                    value=f"label{num}-pref",
                    language=cls.first_language,
                    value_type=cls.pref_label,
                    controlled_list_item=ControlledListItem.objects.filter(
                        controlled_list=cls.list2
                    )[num],
                )
                for num in range(5)
            ]
            + [
                ControlledListItemLabel(
                    value=f"label{num}-alt",
                    language=cls.first_language,
                    value_type=cls.alt_label,
                    controlled_list_item=ControlledListItem.objects.filter(
                        controlled_list=cls.list2
                    )[num],
                )
                for num in range(5)
            ]
        )

        cls.graph = GraphModel.objects.create(isresource=True)
        cls.nodegroup = NodeGroup.objects.get(pk="20000000-0000-0000-0000-100000000000")
        cls.node_using_list1 = Node(
            pk="a3c5b7d3-ef2c-4f8b-afd5-f8d4636b8834",
            graph=cls.graph,
            name="Uses list1",
            datatype="reference",
            nodegroup=cls.nodegroup,
            istopnode=False,
            config={
                "multiValue": False,
                "controlledList": str(cls.list1.pk),
            },
        )
        cls.node_using_list1.save()

        cls.node_using_list2 = Node(
            pk="a3c5b7d3-ef2c-4f8b-afd5-f8d4636b8835",
            graph=cls.graph,
            name="Uses list2",
            datatype="reference",
            nodegroup=cls.nodegroup,
            istopnode=False,
            config={
                "multiValue": False,
                "controlledList": str(cls.list2.pk),
            },
        )
        cls.node_using_list2.save()

    def test_get_controlled_lists(self):
        self.client.force_login(self.anonymous)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(reverse("controlled_lists"))

        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.admin)
        with self.assertNumQueries(11):
            # 1: session
            # 2: auth
            # 3: SELECT FROM controlled_lists
            # 4: prefetch items
            # 5: prefetch labels
            # 6: prefetch children: items
            # 7: prefetch children: labels
            # 8: prefetch grandchildren: items
            # there are no grandchildren, so no labels to get
            # 9: get permitted nodegroups
            # 10-11: permission checks
            response = self.client.get(
                reverse("controlled_lists"), kwargs={"prefetchDepth": 3}
            )

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        # from pprint import pprint
        # pprint(result)

        first_list, second_list = result["controlled_lists"]

        self.assertEqual(
            first_list["nodes"],
            [
                {
                    "id": str(self.node_using_list1.pk),
                    "name": self.node_using_list1.name,
                    "nodegroup_id": str(self.nodegroup.pk),
                    "graph_id": str(self.graph.graphid),
                },
            ],
        )

        for item in first_list["items"]:
            self.assertEqual(item["children"], [])

        self.assertEqual(len(second_list["items"]), 1)
        self.assertEqual(len(second_list["items"][0]["children"]), 4)

    def test_get_controlled_list_permitted_nodegroups(self):
        assign_perm("no_access_to_nodegroup", self.rdm_user, self.nodegroup)

        self.client.force_login(self.rdm_user)
        response = self.client.get(reverse("controlled_lists"))
        result = json.loads(response.content)

        self.assertEqual(result["controlled_lists"][0]["nodes"], [])

    def test_create_list(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("controlled_list_add"))
        self.assertEqual(ControlledList.objects.count(), 3)
        self.assertEqual(
            ControlledList.objects.filter(name__startswith="Untitled List: ").count(), 1
        )

    def test_delete_list(self):
        self.client.force_login(self.admin)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.delete(
                reverse("controlled_list", kwargs={"id": str(self.list1.pk)}),
            )
        self.assertEqual(response.status_code, 400)
        del self.node_using_list1.config["controlledList"]
        self.node_using_list1.save()
        response = self.client.delete(
            reverse("controlled_list", kwargs={"id": str(self.list1.pk)}),
        )
        self.assertEqual(ControlledList.objects.count(), 1)
        self.assertEqual(ControlledList.objects.first().pk, self.list2.pk)

    def test_create_list_item(self):
        self.client.force_login(self.admin)
        existing_pks = [item.pk for item in self.list1.controlled_list_items.all()]

        self.client.post(
            reverse("controlled_list_item_add"),
            {"parent_id": str(self.list1.pk)},
            content_type="application/json",
        )

        self.assertQuerySetEqual(
            self.list1.controlled_list_items.exclude(pk__in=existing_pks),
            [ControlledListItem(pk=SYNCED_PK, controlled_list=self.list1, sortorder=5)],
            transform=sync_pk_for_comparison,
        )

    def test_create_list_item_nested(self):
        self.client.force_login(self.admin)
        existing_pks = [item.pk for item in self.list1.controlled_list_items.all()]

        parent_item = self.list1.controlled_list_items.order_by("uri").first()
        self.client.post(
            reverse("controlled_list_item_add"),
            {"parent_id": str(parent_item.pk)},
            content_type="application/json",
        )

        self.assertQuerySetEqual(
            self.list1.controlled_list_items.exclude(pk__in=existing_pks),
            [
                ControlledListItem(
                    pk=SYNCED_PK,
                    controlled_list=self.list1,
                    sortorder=5,
                    parent_id=parent_item.pk,
                )
            ],
            transform=sync_pk_for_comparison,
        )

    def test_reorder_list_items_valid(self):
        self.client.force_login(self.admin)
        serialized_list = serialize(self.list1, depth_map=defaultdict(int))

        serialized_list["items"][0]["sortorder"] = 1
        serialized_list["items"][1]["sortorder"] = 0
        response = self.client.post(
            reverse("controlled_list", kwargs={"id": str(self.list1.pk)}),
            serialized_list,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [
                item.sortorder
                for item in ControlledListItem.objects.filter(
                    controlled_list=self.list1
                ).order_by("uri")
            ],
            [1, 0, 2, 3, 4],
        )

    def test_reorder_list_items_invalid_negative(self):
        self.client.force_login(self.admin)
        serialized_list = serialize(self.list1, depth_map=defaultdict(int), flat=False)

        serialized_list["items"][0]["sortorder"] = -1
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(
                reverse("controlled_list", kwargs={"id": str(self.list1.pk)}),
                serialized_list,
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)
