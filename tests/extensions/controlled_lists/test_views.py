import json
import uuid
import os, sys
from http import HTTPStatus

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from guardian.shortcuts import assign_perm

from arches.app.models.graph import Graph
from arches.app.models.models import (
    DValueType,
    Language,
    Node,
    NodeGroup,
)
from arches.extensions.controlled_lists.models import (
    List,
    ListItem,
    ListItemImage,
    ListItemImageMetadata,
    ListItemValue,
)
from .constants import TEST_PACKAGE_DIR

# these tests can be run from the command line via
# python manage.py test tests.extensions.controlled_lists.test_views --settings="tests.test_settings"


class ListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.get(username="admin")
        cls.anonymous = User.objects.get(username="anonymous")

        cls.rdm_user = User.objects.create_user(
            "test", "test@archesproject.org", "password"
        )
        rdm_admin_group = Group.objects.get(name="RDM Administrator")
        cls.rdm_user.groups.add(rdm_admin_group)

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

        # Set the parent and sortorder on the children in list2.
        cls.parent = ListItem.objects.get(list=cls.list2, uri="https://getty.edu/0")
        for i, child in enumerate(
            ListItem.objects.filter(list=cls.list2)
            .exclude(pk=cls.parent.pk)
            .order_by("sortorder")
        ):
            child.parent = cls.parent
            child.sortorder = i
            child.save()

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

        cls.graph = Graph.objects.create_graph(name="My Graph")
        cls.draft_graph = cls.graph.draft.first()
        admin = User.objects.get(username="admin")
        cls.graph.publish(user=admin)

        cls.nodegroup = NodeGroup.objects.get(pk="20000000-0000-0000-0000-100000000000")
        cls.node_using_list1 = Node(
            pk=uuid.UUID("a3c5b7d3-ef2c-4f8b-afd5-f8d4636b8834"),
            graph=cls.draft_graph,
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
            graph=cls.draft_graph,
            name="Uses list2",
            datatype="reference",
            nodegroup=cls.nodegroup,
            istopnode=False,
            config={
                "multiValue": True,
                "controlledList": str(cls.list2.pk),
            },
        )
        cls.node_using_list2.save()
        cls.graph.publish(user=admin)

    def test_get_lists(self):
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
                    "graph_id": str(self.draft_graph.graphid),
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
        self.client.force_login(self.anonymous)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(reverse("controlled_list_add"))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN, response.content)

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

    def test_import_skos_post(self):
        self.client.force_login(self.admin)
        input_file = os.path.join(
            TEST_PACKAGE_DIR,
            "reference_data",
            "controlled_lists",
            "skos_rdf_import_example.xml",
        )
        with open(input_file, "rb") as file:
            response = self.client.post(
                reverse("controlled_list_add"),
                {"skosfile": file, "overwrite_option": "overwrite"},
            )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        new_lists = List.objects.filter(name__startswith="Test Thesaurus")
        new_list = new_lists.first()
        new_list_items = new_list.list_items.all()
        new_list_item_values = ListItemValue.objects.filter(
            list_item_id__in=new_list_items.all()
        )
        self.assertEqual(new_lists.count(), 1)
        self.assertEqual(new_list_items.count(), 17)
        self.assertEqual(new_list_item_values.count(), 21)

    def test_export_skos_post(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("controlled_list_export"),
            {"list_ids": [str(self.list1.pk), str(self.list2.pk)]},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        self.assertEqual(
            response["Content-Disposition"],
            'attachment; filename="arches_controlled_lists_controlled_lists.xml"',
        )
        self.assertIn(b"<rdf:RDF", response.content)
        self.assertIn(b"<skos:ConceptScheme", response.content)

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
        existing_pks = [item.pk for item in self.list2.list_items.all()]

        self.client.post(
            reverse("controlled_list_item_add"),
            {"list_id": str(self.list2.pk), "parent_id": None},
            content_type="application/json",
        )

        self.assertQuerySetEqual(
            self.list2.list_items.exclude(pk__in=existing_pks).values(
                "list", "sortorder"
            ),
            [{"list": self.list2.pk, "sortorder": 1}],
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
            self.list1.list_items.exclude(pk__in=existing_pks).values(
                "list", "sortorder", "parent_id"
            ),
            [{"list": self.list1.pk, "sortorder": 0, "parent_id": parent_item.pk}],
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

    def test_get_list_items_flat(self):
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse("controlled_list", kwargs={"list_id": str(self.list2.pk)}),
            QUERY_STRING="flat=true",
        )

        self.assertEqual(
            [item["sortorder"] for item in response.json()["items"]],
            [0, 0, 1, 2, 3],
        )

    def test_move_list_item(self):
        """Move the top-level item in list2, which has 4 children, into list1."""
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
        self.assertEqual(self.list1.list_items.exclude(parent=None).count(), 4)

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

    @override_settings(PUBLIC_SERVER_ADDRESS="public/", FORCE_SCRIPT_NAME="script")
    def test_generate_uri(self):
        self.client.force_login(self.admin)
        item = self.list1.list_items.first()

        response = self.client.patch(
            reverse("controlled_list_item", kwargs={"item_id": str(item.pk)}),
            {"uri": ""},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT, response.content)
        item.refresh_from_db()
        self.assertEqual(
            item.uri, f"public/script/plugins/controlled-list-manager/item/{item.pk}"
        )

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

    def test_copy_list_item_missing_data(self):
        self.client.force_login(self.admin)
        item_to_copy = self.list2.list_items.first()
        data = {
            "copy_children": True,
        }
        response = self.client.post(
            reverse(
                "controlled_list_item_copy", kwargs={"item_id": str(item_to_copy.pk)}
            ),
            data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.content)

    def test_copy_list_item_not_found(self):
        self.client.force_login(self.admin)
        fake_id = uuid.uuid4()
        data = {
            "target_list_id": str(self.list1.pk),
            "copy_children": True,
        }
        response = self.client.post(
            reverse("controlled_list_item_copy", kwargs={"item_id": str(fake_id)}),
            data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    def test_copy_list_item_to_item(self):
        self.client.force_login(self.admin)
        item_to_copy = self.list2.list_items.first()
        target_item = self.list1.list_items.first()
        data = {
            "target_list_id": str(self.list1.pk),
            "target_item_id": str(target_item.pk),
            "copy_children": True,
        }
        response = self.client.post(
            reverse(
                "controlled_list_item_copy", kwargs={"item_id": str(item_to_copy.pk)}
            ),
            data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED, response.content)
        result = response.json()
        self.assertIn("copied_list_item", result)
        copied_item = result["copied_list_item"]
        self.assertNotEqual(str(item_to_copy.pk), str(copied_item["id"]))
        self.assertEqual(copied_item["parent_id"], str(target_item.pk))
        self.assertTrue(len(copied_item.get("children", [])) > 0)

    def test_copy_list_item_to_list(self):
        self.client.force_login(self.admin)
        item_to_copy = self.list2.list_items.first()
        data = {
            "target_list_id": str(self.list1.pk),
            "copy_children": False,
        }
        response = self.client.post(
            reverse(
                "controlled_list_item_copy", kwargs={"item_id": str(item_to_copy.pk)}
            ),
            data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED, response.content)
        result = response.json()
        self.assertIn("copied_list_item", result)
        copied_item = result["copied_list_item"]
        self.assertNotEqual(str(item_to_copy.pk), str(copied_item["id"]))
        self.assertEqual(copied_item["list_id"], str(self.list1.pk))
        self.assertEqual(len(copied_item.get("children", [])), 0)

    # ListView error cases

    def test_get_list_not_found(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("controlled_list", kwargs={"list_id": str(uuid.uuid4())}),
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    def test_patch_list_not_found(self):
        self.client.force_login(self.admin)
        response = self.client.patch(
            reverse("controlled_list", kwargs={"list_id": str(uuid.uuid4())}),
            {"name": "New Name"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    def test_patch_list_no_update_fields(self):
        self.client.force_login(self.admin)
        response = self.client.patch(
            reverse("controlled_list", kwargs={"list_id": str(self.list1.pk)}),
            {},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.content)

    def test_patch_list_name(self):
        self.client.force_login(self.admin)
        response = self.client.patch(
            reverse("controlled_list", kwargs={"list_id": str(self.list2.pk)}),
            {"name": "Renamed List"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT, response.content)
        self.list2.refresh_from_db()
        self.assertEqual(self.list2.name, "Renamed List")

    def test_delete_list_not_found(self):
        self.client.force_login(self.admin)
        response = self.client.delete(
            reverse("controlled_list", kwargs={"list_id": str(uuid.uuid4())}),
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    # FilteredListView tests

    def test_filtered_list_view_basic(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("controlled_list_filtered", kwargs={"list_id": str(self.list2.pk)}),
            QUERY_STRING="flat=true",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        result = response.json()
        self.assertIn("items", result)
        items = result["items"]
        # All 5 items returned in hierarchical order with depth/parent_path
        self.assertEqual(len(items), 5)
        for item in items:
            self.assertIn("depth", item)
            self.assertIn("parent_path", item)
        # Root item is first, has depth=0 and empty parent_path
        self.assertEqual(items[0]["depth"], 0)
        self.assertEqual(items[0]["parent_path"], "")
        # Children follow the root and have depth=1
        children = [i for i in items if i["depth"] == 1]
        self.assertEqual(len(children), 4)

    def test_filtered_list_view_with_term(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("controlled_list_filtered", kwargs={"list_id": str(self.list1.pk)}),
            QUERY_STRING="flat=true&term=label0",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        result = response.json()
        items = result["items"]
        self.assertEqual(len(items), 1)
        self.assertTrue(
            any(
                v.get("valuetype_id") == "prefLabel" and "label0" in v.get("value", "")
                for v in items[0]["values"]
            )
        )

    def test_filtered_list_view_no_match(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("controlled_list_filtered", kwargs={"list_id": str(self.list1.pk)}),
            QUERY_STRING="flat=true&term=doesnotexist",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        self.assertEqual(response.json()["items"], [])

    def test_filtered_list_view_not_found(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("controlled_list_filtered", kwargs={"list_id": str(uuid.uuid4())}),
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    # ListItemView additional error cases

    def test_create_list_item_anonymous(self):
        self.client.force_login(self.anonymous)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(
                reverse("controlled_list_item_add"),
                {"list_id": str(self.list1.pk), "parent_id": None},
                content_type="application/json",
            )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN, response.content)

    def test_create_list_item_missing_keys(self):
        self.client.force_login(self.admin)
        # Omit parent_id to trigger KeyError in the view
        response = self.client.post(
            reverse("controlled_list_item_add"),
            {"list_id": str(self.list1.pk)},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.content)

    def test_create_list_item_invalid_list(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("controlled_list_item_add"),
            {"list_id": str(uuid.uuid4()), "parent_id": None},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.content)

    def test_patch_list_item_not_found(self):
        self.client.force_login(self.admin)
        response = self.client.patch(
            reverse("controlled_list_item", kwargs={"item_id": str(uuid.uuid4())}),
            {"uri": "https://example.com/new"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    def test_patch_list_item_no_fields(self):
        self.client.force_login(self.admin)
        item = self.list1.list_items.first()
        response = self.client.patch(
            reverse("controlled_list_item", kwargs={"item_id": str(item.pk)}),
            {},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.content)

    def test_delete_list_item_not_found(self):
        self.client.force_login(self.admin)
        response = self.client.delete(
            reverse("controlled_list_item", kwargs={"item_id": str(uuid.uuid4())}),
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    # ListItemValueView additional tests

    def test_create_label(self):
        self.client.force_login(self.admin)
        item = self.list1.list_items.first()
        data = {
            "value": "new-label",
            "language_id": self.first_language.code,
            "valuetype_id": "altLabel",
            "list_item_id": str(item.pk),
        }
        response = self.client.post(
            reverse("controlled_list_item_value_add"),
            data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED, response.content)
        result = response.json()
        self.assertEqual(result["value"], "new-label")
        self.assertEqual(result["valuetype_id"], "altLabel")

    def test_update_label_not_found(self):
        self.client.force_login(self.admin)
        data = {
            "value": "updated",
            "valuetype_id": "altLabel",
            "language_id": self.first_language.code,
        }
        response = self.client.put(
            reverse(
                "controlled_list_item_value",
                kwargs={"value_id": str(uuid.uuid4())},
            ),
            data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    def test_update_label_missing_keys(self):
        self.client.force_login(self.admin)
        alt_label = ListItemValue.objects.filter(valuetype_id="altLabel").first()
        response = self.client.put(
            reverse(
                "controlled_list_item_value",
                kwargs={"value_id": str(alt_label.pk)},
            ),
            {"value": "updated"},  # missing valuetype_id and language_id
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.content)

    def test_delete_label_not_found(self):
        self.client.force_login(self.admin)
        response = self.client.delete(
            reverse(
                "controlled_list_item_value",
                kwargs={"value_id": str(uuid.uuid4())},
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    # ListItemImageView additional tests

    def test_delete_image_not_found(self):
        self.client.force_login(self.admin)
        response = self.client.delete(
            reverse(
                "controlled_list_item_image",
                kwargs={"image_id": str(uuid.uuid4())},
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    # ListItemImageMetadataView additional tests

    def test_create_metadata(self):
        self.client.force_login(self.admin)
        item = self.list1.list_items.first()
        temp_image = ListItemImage.objects.create(
            list_item=item,
            value="path/to/temp_image.png",
            valuetype_id="image",
        )
        first_metadata_type = ListItemImageMetadata.MetadataChoices.choices[0][0]
        data = {
            "list_item_image_id": str(temp_image.pk),
            "metadata_type": first_metadata_type,
            "value": "Test metadata value",
            "language_id": self.first_language.code,
        }
        response = self.client.post(
            reverse("controlled_list_item_image_metadata_add"),
            data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED, response.content)

    def test_update_metadata_not_found(self):
        self.client.force_login(self.admin)
        first_metadata_type = ListItemImageMetadata.MetadataChoices.choices[0][0]
        data = {
            "value": "Updated",
            "language_id": self.first_language.code,
            "metadata_type": first_metadata_type,
        }
        response = self.client.put(
            reverse(
                "controlled_list_item_image_metadata",
                kwargs={"metadata_id": str(uuid.uuid4())},
            ),
            data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    def test_update_metadata_missing_keys(self):
        self.client.force_login(self.admin)
        metadata = self.image.list_item_image_metadata.first()
        response = self.client.put(
            reverse(
                "controlled_list_item_image_metadata",
                kwargs={"metadata_id": str(metadata.pk)},
            ),
            {"value": "Updated"},  # missing language_id and metadata_type
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.content)

    def test_delete_metadata_not_found(self):
        self.client.force_login(self.admin)
        response = self.client.delete(
            reverse(
                "controlled_list_item_image_metadata",
                kwargs={"metadata_id": str(uuid.uuid4())},
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    # ListExportView additional tests

    def test_export_skos_empty_list_ids(self):
        self.client.force_login(self.admin)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(
                reverse("controlled_list_export"),
                {"list_ids": []},
                content_type="application/json",
            )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.content)

    def test_export_skos_anonymous(self):
        self.client.force_login(self.anonymous)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(
                reverse("controlled_list_export"),
                {"list_ids": [str(self.list1.pk)]},
                content_type="application/json",
            )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN, response.content)

    # Progressive-loading endpoints

    def test_get_lists_shallow(self):
        """?shallow=true returns root items only with has_children flags and
        no nested children arrays."""
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("controlled_lists"),
            QUERY_STRING="shallow=true",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        result = json.loads(response.content)

        lists_by_name = {lst["name"]: lst for lst in result["controlled_lists"]}
        list1 = lists_by_name["list1"]
        list2 = lists_by_name["list2"]

        # list1: 5 flat items, none have children.
        self.assertEqual(len(list1["items"]), 5)
        for item in list1["items"]:
            self.assertEqual(item["children"], [])
            self.assertFalse(item["has_children"])

        # list2: 1 root item (the parent), which DOES have children, but the
        # shallow response must not include them inline.
        self.assertEqual(len(list2["items"]), 1)
        root = list2["items"][0]
        self.assertEqual(root["children"], [])
        self.assertTrue(root["has_children"])

    def test_get_list_shallow(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("controlled_list", kwargs={"list_id": str(self.list2.pk)}),
            QUERY_STRING="shallow=true",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        result = json.loads(response.content)
        self.assertEqual(len(result["items"]), 1)
        self.assertTrue(result["items"][0]["has_children"])
        self.assertEqual(result["items"][0]["children"], [])

    def test_get_list_item_children(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse(
                "controlled_list_item_children",
                kwargs={"item_id": str(self.parent.pk)},
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        result = json.loads(response.content)
        # parent has 4 children, none with grandchildren.
        self.assertEqual(len(result["children"]), 4)
        for child in result["children"]:
            self.assertFalse(child["has_children"])
            self.assertEqual(child["children"], [])
            self.assertEqual(child["parent_id"], str(self.parent.pk))

    def test_get_list_item_children_not_found(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse(
                "controlled_list_item_children",
                kwargs={"item_id": str(uuid.uuid4())},
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    def test_get_list_item_ancestor_path(self):
        self.client.force_login(self.admin)
        target = self.parent.children.order_by("sortorder").first()
        response = self.client.get(
            reverse(
                "controlled_list_item_path",
                kwargs={"item_id": str(target.pk)},
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        result = json.loads(response.content)

        # Expect a single path: [list2_dict, parent_item_dict, target_item_dict]
        self.assertEqual(len(result["paths"]), 1)
        search_results = result["paths"][0]["searchResults"]
        self.assertEqual(len(search_results), 3)

        list_dict = search_results[0]
        self.assertEqual(list_dict["id"], str(self.list2.pk))
        self.assertEqual(list_dict["name"], self.list2.name)

        parent_dict = search_results[1]
        self.assertEqual(parent_dict["id"], str(self.parent.pk))
        self.assertTrue(parent_dict["has_children"])

        target_dict = search_results[2]
        self.assertEqual(target_dict["id"], str(target.pk))
        self.assertFalse(target_dict["has_children"])

    def test_get_list_item_ancestor_path_not_found(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse(
                "controlled_list_item_path",
                kwargs={"item_id": str(uuid.uuid4())},
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND, response.content)

    def test_filtered_list_includes_parent_ids(self):
        """FilteredListView rows must include parent_ids so the frontend can
        lazy-load the right branches to reveal a match."""
        self.client.force_login(self.admin)
        # A label that only the children of `parent` carry.
        response = self.client.get(
            reverse(
                "controlled_list_filtered",
                kwargs={"list_id": str(self.list2.pk)},
            ),
            QUERY_STRING="term=label1-pref",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK, response.content)
        result = json.loads(response.content)
        for item in result.get("items", []):
            self.assertIn("parent_ids", item)
            if item.get("parent_id"):
                # The immediate parent id must appear last in parent_ids.
                self.assertEqual(item["parent_ids"][-1], item["parent_id"])
