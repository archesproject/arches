import json

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django.test.client import Client

from arches.app.models.models import ControlledList, ControlledListItem, DValueType, Label, Language


class ControlledListTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.admin = User.objects.get(username="admin")
        cls.anonymous = User.objects.get(username="anonymous")

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
            [ControlledListItem(uri=f"https://archesproject.org/{num}", list=cls.list1) for num in range(5)]
            + [ControlledListItem(uri=f"https://getty.edu/{num}", list=cls.list2) for num in range(5)]
        )

        parent = ControlledListItem.objects.get(list=cls.list2, uri=f"https://getty.edu/0")
        for child in ControlledListItem.objects.filter(list=cls.list2).exclude(pk=parent.pk):
            child.parent = parent
            child.save()

        # Create a prefLabel and altLabel per item. (20)
        Label.objects.bulk_create(
            [
                Label(
                    value=f"label{num}-pref",
                    language=cls.first_language,
                    value_type=cls.pref_label,
                    item=ControlledListItem.objects.filter(list=cls.list1)[num],
                )
                for num in range(5)
            ]
            + [
                Label(
                    value=f"label{num}-alt",
                    language=cls.first_language,
                    value_type=cls.alt_label,
                    item=ControlledListItem.objects.filter(list=cls.list1)[num],
                )
                for num in range(5)
            ]
            + [
                Label(
                    value=f"label{num}-pref",
                    language=cls.first_language,
                    value_type=cls.pref_label,
                    item=ControlledListItem.objects.filter(list=cls.list2)[num],
                )
                for num in range(5)
            ]
            + [
                Label(
                    value=f"label{num}-alt",
                    language=cls.first_language,
                    value_type=cls.alt_label,
                    item=ControlledListItem.objects.filter(list=cls.list2)[num],
                )
                for num in range(5)
            ]
        )

    def test_get_controlled_lists(self):
        self.client.force_login(self.anonymous)
        response = self.client.get(reverse("controlled_lists"))

        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.admin)
        with self.assertNumQueries(8):
            # 1: session
            # 2: auth
            # 3: SELECT FROM controlled_lists
            # 4: prefetch items
            # 5: prefetch labels
            # 6: prefetch children: items
            # 7: prefetch children: labels
            # 8: prefetch grandchildren: items
            # there are no grandchildren, so no labels to get
            response = self.client.get(reverse("controlled_lists"), kwargs={"prefetchDepth": 3})

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        # from pprint import pprint
        # pprint(result)

        first_list, second_list = result["controlled_lists"]
        for item in first_list["items"]:
            self.assertEqual(item["children"], [])

        second_list_first_item = second_list["items"][0]
        self.assertEqual(second_list_first_item["children"], second_list["items"][1:])
