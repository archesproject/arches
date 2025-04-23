from django.contrib.auth.models import User
from django.test import RequestFactory
from tests.base_test import ArchesTestCase
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.views.search import search_results
import time
import json

# these tests can be run from the command line via
# python manage.py test tests.search.search_sort_tests --settings="tests.test_settings"


class SearchSortTests(ArchesTestCase):
    graph_fixtures = ["Search Sort Test Model"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.url = "/en/search?paging-filter=1&tiles=true&format=tilecsv&reportlink=false&precision=6&total=5&exportsystemvalues=false"
        cls.user = User.objects.get(username="admin")

        test_graph = Graph.objects.get(pk="cfc0d27d-b1f4-4939-a870-07d580be2b60")

        Resource.objects.create(
            graph=test_graph,
            name="B Resource (first created)",
            resourceinstanceid="8ec120f4-61cd-4fa1-8f9a-3d12cff3176f",
        )

        Resource.objects.create(
            graph=test_graph,
            name="C Resource (second created)",
            resourceinstanceid="a94c81c5-2047-4b53-8341-495f12bfad95",
        )

        Resource.objects.create(
            graph=test_graph,
            name="A Resource (third created)",
            resourceinstanceid="09ba8b82-b6db-4ece-9a46-98f6d381a7b2",
        )

        name_node_id = "322b3b82-0a39-11f0-a841-c3a65b371351"

        resource_c_name_tile = Tile.objects.create(
            **{
                "resourceinstance_id": "a94c81c5-2047-4b53-8341-495f12bfad95",
                "nodegroup_id": name_node_id,
            }
        )

        resource_c_name_tile.data = {
            "322b3b82-0a39-11f0-a841-c3a65b371351": {
                "en": {"value": "Resource C (first updated)", "direction": "ltr"}
            }
        }
        resource_c_name_tile.save()

        resource_b_name_tile = Tile.objects.create(
            **{
                "resourceinstance_id": "8ec120f4-61cd-4fa1-8f9a-3d12cff3176f",
                "nodegroup_id": name_node_id,
            }
        )

        resource_b_name_tile.data = {
            "322b3b82-0a39-11f0-a841-c3a65b371351": {
                "en": {"value": "Resource B (second updated)", "direction": "ltr"}
            }
        }
        resource_b_name_tile.save()

        resource_a_name_tile = Tile.objects.create(
            **{
                "resourceinstance_id": "09ba8b82-b6db-4ece-9a46-98f6d381a7b2",
                "nodegroup_id": name_node_id,
            }
        )

        resource_a_name_tile.data = {
            "322b3b82-0a39-11f0-a841-c3a65b371351": {
                "en": {"value": "Resource A (third updated)", "direction": "ltr"}
            }
        }
        resource_a_name_tile.save()

        # add delay to allow for indexes to be updated
        time.sleep(1)

    def search_request(self, query_params):
        factory = RequestFactory()
        url = f"{self.url}{query_params}"
        request = factory.get(url)
        request.user = self.user

        response = search_results(request)
        response_data = json.loads(response.content.decode("utf-8"))
        hits_data = response_data["results"]["hits"]["hits"]
        return [hit["_id"] for hit in hits_data]

    def test_sort_by_names_asc(self):
        hit_ids = self.search_request("&sort-by=resource_name&sort-order=asc")
        ids_ordered_by_name = [
            "09ba8b82-b6db-4ece-9a46-98f6d381a7b2",  # RA
            "8ec120f4-61cd-4fa1-8f9a-3d12cff3176f",  # RB
            "a94c81c5-2047-4b53-8341-495f12bfad95",  # RC
        ]

        self.assertListEqual(
            hit_ids,
            ids_ordered_by_name,
            "The results are not ordered by name as expected.",
        )

    def test_sort_by_names_desc(self):
        hit_ids = self.search_request("&sort-by=resource_name&sort-order=desc")
        ids_ordered_by_name = [
            "a94c81c5-2047-4b53-8341-495f12bfad95",  # RC
            "8ec120f4-61cd-4fa1-8f9a-3d12cff3176f",  # RB
            "09ba8b82-b6db-4ece-9a46-98f6d381a7b2",  # RA
        ]

        self.assertListEqual(
            hit_ids,
            ids_ordered_by_name,
            "The results are not ordered by name as expected.",
        )

    def test_sort_by_date_created_asc(self):
        hit_ids = self.search_request("&sort-by=date_created&sort-order=asc")
        ids_ordered_by_date_created = [
            "8ec120f4-61cd-4fa1-8f9a-3d12cff3176f",  # RB (1st created)
            "a94c81c5-2047-4b53-8341-495f12bfad95",  # RC (2nd created)
            "09ba8b82-b6db-4ece-9a46-98f6d381a7b2",  # RA (3rd created)
        ]

        self.assertListEqual(
            hit_ids,
            ids_ordered_by_date_created,
            "The results are not ordered by date created",
        )

    def test_sort_by_date_created_desc(self):
        hit_ids = self.search_request("&sort-by=date_created&sort-order=desc")
        ids_ordered_by_date_created = [
            "09ba8b82-b6db-4ece-9a46-98f6d381a7b2",  # RA (3rd created)
            "a94c81c5-2047-4b53-8341-495f12bfad95",  # RC (2nd created)
            "8ec120f4-61cd-4fa1-8f9a-3d12cff3176f",  # RB (1st created)
        ]

        self.assertListEqual(
            hit_ids,
            ids_ordered_by_date_created,
            "The results are not ordered by date created",
        )

    def test_sort_by_date_last_edited_asc(self):
        hit_ids = self.search_request("&sort-by=date_last_edited&sort-order=asc")
        ids_ordered_by_date_last_edited = [
            "a94c81c5-2047-4b53-8341-495f12bfad95",  # RC (1st updated)
            "8ec120f4-61cd-4fa1-8f9a-3d12cff3176f",  # RB (2nd updated)
            "09ba8b82-b6db-4ece-9a46-98f6d381a7b2",  # RA (3rd updated)
        ]

        self.assertListEqual(
            hit_ids,
            ids_ordered_by_date_last_edited,
            "The results are not ordered by date edited",
        )

    def test_sort_by_date_last_edited_desc(self):
        hit_ids = self.search_request("&sort-by=date_last_edited&sort-order=desc")
        ids_ordered_by_date_last_edited = [
            "09ba8b82-b6db-4ece-9a46-98f6d381a7b2",  # RA (3rd updated)
            "8ec120f4-61cd-4fa1-8f9a-3d12cff3176f",  # RB (2nd updated)
            "a94c81c5-2047-4b53-8341-495f12bfad95",  # RC (1st updated)
        ]

        self.assertListEqual(
            hit_ids,
            ids_ordered_by_date_last_edited,
            "The results are not ordered by date edited",
        )

    def test_sort_order_does_not_change_unsorted_data(self):
        unsorted_ids = self.search_request("")
        desc_sorted_ids = self.search_request("&sort-order=desc")

        self.assertListEqual(
            unsorted_ids, desc_sorted_ids, "The data has been unexpectedly ordered"
        )

    def test_default_ascending_sort_order(self):
        hit_ids = self.search_request("&sort-by=date_last_edited")
        ids_ordered_by_date_last_edited = [
            "a94c81c5-2047-4b53-8341-495f12bfad95",  # RC (1st updated)
            "8ec120f4-61cd-4fa1-8f9a-3d12cff3176f",  # RB (2nd updated)
            "09ba8b82-b6db-4ece-9a46-98f6d381a7b2",  # RA (3rd updated)
        ]

        self.assertListEqual(
            hit_ids,
            ids_ordered_by_date_last_edited,
            "The results are not ordered by date edited ascending",
        )
