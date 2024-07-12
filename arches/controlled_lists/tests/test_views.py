import json
import uuid
import sys
from http import HTTPStatus

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from guardian.shortcuts import assign_perm

from arches.app.models.graph import Graph
from arches.app.models.models import (
    DValueType,
    Language,
    Node,
    NodeGroup,
)
from arches.controlled_lists.models import (
    List,
    ListItem,
    ListItemImage,
    ListItemImageMetadata,
    ListItemValue,
)

# these tests can be run from the command line via
# python manage.py test arches.controlled_lists.tests.view_tests --settings="tests.test_settings"

SYNCED_PK = uuid.uuid4()


def sync_pk_for_comparison(item):
    item.pk = SYNCED_PK
    return item


class ListTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.list1 = List.objects.create(name="list1")
        # Second list has children (nested items).
        cls.list2 = List.objects.create(name="list2")

        cls.first_language = Language.objects.first()
        cls.new_language = Language.objects.create(
            code="eo",
            name="Esperanto",
            default_direction="ltr",
            isdefault=False,
            scope="system",
        )
        cls.pref_label = DValueType.objects.get(valuetype="prefLabel")
        cls.alt_label = DValueType.objects.get(valuetype="altLabel")

        # Create 5 labels per list. (10)
        ListItem.objects.bulk_create(
            [
                ListItem(
                    uri=f"https://archesproject.org/{num}",
                    list=cls.list1,
                    sortorder=num,
                )
                for num in range(5)
            ]
            + [
                ListItem(
                    uri=f"https://getty.edu/{num}",
                    list=cls.list2,
                    sortorder=num,
                )
                for num in range(5)
            ]
        )

        cls.parent = ListItem.objects.get(list=cls.list2, uri="https://getty.edu/0")
        for child in ListItem.objects.filter(list=cls.list2).exclude(pk=cls.parent.pk):
            child.parent = cls.parent
            child.save()

        # Create a prefLabel and altLabel per item. (20)
        list1_items = cls.list1.list_items.all()
        list2_items = cls.list2.list_items.all()
        ListItemValue.objects.bulk_create(
            [
                ListItemValue(
                    value=f"label{num}-pref",
                    language=cls.first_language,
                    valuetype=cls.pref_label,
                    list_item=list1_items[num],
                )
                for num in range(5)
            ]
            + [
                ListItemValue(
                    value=f"label{num}-alt",
                    language=cls.first_language,
                    valuetype=cls.alt_label,
                    list_item=list1_items[num],
                )
                for num in range(5)
            ]
            + [
                ListItemValue(
                    value=f"label{num}-pref",
                    language=cls.first_language,
                    valuetype=cls.pref_label,
                    list_item=list2_items[num],
                )
                for num in range(5)
            ]
            + [
                ListItemValue(
                    value=f"label{num}-alt",
                    language=cls.first_language,
                    valuetype=cls.alt_label,
                    list_item=list2_items[num],
                )
                for num in range(5)
            ]
        )

        # Create one image with full metadata for the first item in list 1.
        cls.image = ListItemImage.objects.create(
            list_item=cls.list1.list_items.first(),
            value="path/to/image.png",
            valuetype_id="image",
        )
        for metadata in ListItemImageMetadata.MetadataChoices:
            ListItemImageMetadata(
                list_item_image=cls.image,
                metadata_type=metadata,
                value=f"{metadata} for {cls.image.value}",
                language=cls.first_language,
            ).save()

        cls.graph = Graph.new(name="My Graph")
        cls.future_graph = cls.graph.create_editable_future_graph()
        admin = User.objects.get(username="admin")
        cls.graph.publish(user=admin)

        cls.nodegroup = NodeGroup.objects.get(pk="20000000-0000-0000-0000-100000000000")
        cls.node_using_list1 = Node(
            pk=uuid.UUID("a3c5b7d3-ef2c-4f8b-afd5-f8d4636b8834"),
            graph=cls.future_graph,
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
            pk=uuid.UUID("a3c5b7d3-ef2c-4f8b-afd5-f8d4636b8835"),
            graph=cls.future_graph,
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
        cls.graph.publish(user=admin)

    def test_get_lists(self):
        self.client.force_login(self.anonymous)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(reverse("controlled_lists"))

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN, response.content)

        self.client.force_login(self.admin)
        with self.assertNumQueries(14):
            # 1: session
            # 2: auth
            # 3: SELECT FROM lists
            # 4: prefetch items
            # 5: prefetch item labels/images
            # 7: prefetch image metadata
            # 8: prefetch children: items
            # 9: prefetch children: item labels/images
            # 10: prefetch children: image metadata
            # 11: prefetch grandchildren: items
            # there are no grandchildren, so no values/metadata to get
            # 12: get permitted nodegroups
            # 13-14: permission checks
            response = self.client.get(reverse("controlled_lists"))

        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        result = json.loads(response.content)

        first_list, second_list = result["controlled_lists"]

        self.assertEqual(
            first_list["nodes"],
            [
                {
                    "id": str(self.node_using_list1.pk),
                    "name": self.node_using_list1.name,
                    "nodegroup_id": str(self.nodegroup.pk),
                    "graph_id": str(self.future_graph.graphid),
                    "graph_name": "My Graph",
                },
            ],
        )

        for item in first_list["items"]:
            self.assertEqual(item["children"], [])

        self.assertEqual(len(second_list["items"]), 1)
        self.assertEqual(len(second_list["items"][0]["children"]), 4)

    def test_get_list_permitted_nodegroups(self):
        assign_perm("no_access_to_nodegroup", self.rdm_user, self.nodegroup)

        self.client.force_login(self.rdm_user)
        response = self.client.get(reverse("controlled_lists"))
        result = json.loads(response.content)

        self.assertEqual(result["controlled_lists"][0]["nodes"], [])

        response = self.client.get(
            reverse("controlled_list", kwargs={"list_id": str(self.list1.pk)}),
        )
        result = json.loads(response.content)

        self.assertEqual(result["nodes"], [])

    def test_create_list(self):
        self.client.force_login(self.admin)
        self.client.post(
            reverse("controlled_list_add"),
            {"name": ""},
            content_type="application/json",
        )
        self.assertEqual(List.objects.count(), 3)
        self.assertEqual(
            List.objects.filter(name__startswith="Untitled List: ").count(), 1
        )

    def test_delete_list(self):
        self.client.force_login(self.admin)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.delete(
                reverse("controlled_list", kwargs={"list_id": str(self.list1.pk)}),
            )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.content)
        del self.node_using_list1.config["controlledList"]
        self.node_using_list1.save()
        response = self.client.delete(
            reverse("controlled_list", kwargs={"list_id": str(self.list1.pk)}),
        )
        self.assertEqual(List.objects.count(), 1)
        self.assertEqual(List.objects.first().pk, self.list2.pk)

    def test_create_list_item(self):
        self.client.force_login(self.admin)
        existing_pks = [item.pk for item in self.list1.list_items.all()]

        self.client.post(
            reverse("controlled_list_item_add"),
            {"list_id": str(self.list1.pk), "parent_id": None},
            content_type="application/json",
        )

        self.assertQuerySetEqual(
            self.list1.list_items.exclude(pk__in=existing_pks),
            [ListItem(pk=SYNCED_PK, list=self.list1, sortorder=5)],
            transform=sync_pk_for_comparison,
        )

    def test_create_list_item_nested(self):
        self.client.force_login(self.admin)
        existing_pks = [item.pk for item in self.list1.list_items.all()]

        parent_item = self.list1.list_items.order_by("uri").first()
        self.client.post(
            reverse("controlled_list_item_add"),
            {"list_id": str(self.list1.pk), "parent_id": str(parent_item.pk)},
            content_type="application/json",
        )

        self.assertQuerySetEqual(
            self.list1.list_items.exclude(pk__in=existing_pks),
            [
                ListItem(
                    pk=SYNCED_PK,
                    list=self.list1,
                    sortorder=5,
                    parent_id=parent_item.pk,
                )
            ],
            transform=sync_pk_for_comparison,
        )

    def test_list_items_provide_new_sortorder(self):
        self.client.force_login(self.admin)

        response = self.client.patch(
            reverse("controlled_list", kwargs={"list_id": str(self.list1.pk)}),
            # Reverse the sortorder
            {
                "sortorder_map": {
                    str(item.pk): i
                    for i, item in enumerate(reversed(self.list1.list_items.all()))
                },
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT, response.content)
        self.assertQuerySetEqual(
            self.list1.list_items.all()
            .order_by("uri")
            .values_list("sortorder", flat=True),
            [4, 3, 2, 1, 0],
        )

    def test_move_list_item(self):
        """Move the top-level item in list2, which has children, into list1."""
        self.client.force_login(self.admin)

        body = {
            "parent_map": {str(self.parent.pk): None},
            "sortorder_map": {str(self.parent.pk): 5},
        }

        for i, child in enumerate(self.parent.children.all(), start=1):
            body["sortorder_map"][str(child.pk)] = 5 + i

        response = self.client.patch(
            reverse("controlled_list", kwargs={"list_id": str(self.list1.pk)}),
            body,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT, response.content)
        self.assertQuerySetEqual(
            self.list1.list_items.all()
            .order_by("uri")
            .values_list("sortorder", flat=True),
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        )

    def test_recursive_cycles(self):
        self.client.force_login(self.admin)
        serialized_list = self.list2.serialize(flat=False)

        parent = serialized_list["items"][0]
        parent_id = str(parent["id"])
        child = serialized_list["items"][0]["children"][0]
        child_id = str(child["id"])

        parent["parent_id"] = child_id
        child["parent_id"] = parent_id

        # Speed up test by lowering recursion limit
        original_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(200)
        self.addCleanup(sys.setrecursionlimit, original_limit)

        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.patch(
                reverse("controlled_list_item", kwargs={"item_id": parent_id}),
                {"parent_id": parent["parent_id"]},
                content_type="application/json",
            )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.content)

    def test_update_uri_blank(self):
        self.client.force_login(self.admin)
        item = self.list1.list_items.first()

        response = self.client.patch(
            reverse("controlled_list_item", kwargs={"item_id": str(item.pk)}),
            {"uri": ""},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT, response.content)
        item.refresh_from_db()
        self.assertIsNone(item.uri)

    def test_delete_list_item(self):
        self.client.force_login(self.admin)
        response = self.client.delete(
            reverse("controlled_list_item", kwargs={"item_id": str(self.parent.pk)})
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT, response.content)
        self.assertQuerySetEqual(ListItem.objects.filter(pk=self.parent.pk), [])

    def test_update_label_valid(self):
        self.client.force_login(self.admin)
        serialized_list = self.list1.serialize(flat=False)
        label = serialized_list["items"][0]["values"][0]
        label["language_id"] = self.new_language.code

        response = self.client.put(
            reverse("controlled_list_item_value", kwargs={"value_id": label["id"]}),
            label,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)

    def test_update_label_invalid(self):
        self.client.force_login(self.admin)
        serialized_list = self.list1.serialize(flat=False)
        label = serialized_list["items"][0]["values"][0]
        label["value"] = "A" * 2049

        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.put(
                reverse("controlled_list_item_value", kwargs={"value_id": label["id"]}),
                label,
                content_type="application/json",
            )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.content)

    def test_delete_label_valid(self):
        self.client.force_login(self.admin)
        alt_label = ListItemValue.objects.filter(valuetype_id="altLabel").first()
        response = self.client.delete(
            reverse(
                "controlled_list_item_value", kwargs={"value_id": str(alt_label.pk)}
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT, response.content)

    def test_delete_label_invalid(self):
        self.client.force_login(self.admin)
        pref_label = ListItemValue.objects.filter(valuetype_id="prefLabel").first()
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.delete(
                reverse(
                    "controlled_list_item_value",
                    kwargs={"value_id": str(pref_label.pk)},
                ),
            )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.content)

    def test_delete_image(self):
        self.client.force_login(self.admin)
        response = self.client.delete(
            reverse(
                "controlled_list_item_image", kwargs={"image_id": str(self.image.pk)}
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT, response.content)
        self.assertQuerySetEqual(ListItemImage.objects.filter(pk=self.image.pk), [])

    def test_update_metadata_valid(self):
        self.client.force_login(self.admin)
        serialized_image = self.image.serialize()
        metadatum = serialized_image["metadata"][0]
        metadatum["language_id"] = self.new_language.code

        response = self.client.put(
            reverse(
                "controlled_list_item_image_metadata",
                kwargs={"metadata_id": metadatum["id"]},
            ),
            metadatum,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)

    def test_update_metadata_invalid(self):
        self.client.force_login(self.admin)
        serialized_image = self.image.serialize()
        metadatum = serialized_image["metadata"][0]
        metadatum["value"] = "A" * 2049

        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.put(
                reverse(
                    "controlled_list_item_image_metadata",
                    kwargs={"metadata_id": metadatum["id"]},
                ),
                metadatum,
                content_type="application/json",
            )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.content)

    def test_delete_metadata(self):
        self.client.force_login(self.admin)
        metadata = self.image.list_item_image_metadata.first()
        response = self.client.delete(
            reverse(
                "controlled_list_item_image_metadata",
                kwargs={"metadata_id": str(metadata.pk)},
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT, response.content)
        self.assertQuerySetEqual(
            ListItemImageMetadata.objects.filter(pk=metadata.pk), []
        )
