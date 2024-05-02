from django.contrib.auth.models import User
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.models import models
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from yourapp.models import BulkDataDeletion  # Adjust import as necessary
from tests.arches_test_case import ArchesTestCase
import os
import uuid
# these tests can be run from the command line via
# python manage.py test tests.bulkdata.bulk_data_delete_tests --settings="tests.test_settings"

class BulkDataDeletionTests(ArchesTestCase):
    def setUpClass(self):
        super().setUpClass()
        # Setup test data here. You might want to create users, resources, tiles, etc.
        self.user = User.objects.create(username='testuser', password='securepassword')
        self.bulk_deleter = BulkDataDeletion()

        with open(os.path.join("tests/fixtures/resource_graphs/Search Test Model.json"), "r") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])
        self.search_model_graphid = "d291a445-fa5f-11e6-afa8-14109fd34195"
        self.search_model_name_nodeid = "2fe14de3-fa61-11e6-897b-14109fd34195"
        # Further setup like creating resources and tiles that the test methods will interact with.

    def test_get_number_of_deletions_with_no_resourceids(self):
        # Test to ensure deletion count is calculated correctly.
        loadid = str(uuid.uuid4())
        resourceids, tile_ct = create_test_resources_and_tiles(self.search_model_graphid, self.search_model_name_nodeid, loadid)
        number_of_resource, number_of_tiles = self.bulk_deleter.get_number_of_deletions(self.search_model_graphid, self.search_model_name_nodeid, None)
        
        self.assertEqual(number_of_resource, len(resourceids))

    def test_delete_resources(self):
        # Test to ensure resources are deleted properly.
        loadid = str(uuid.uuid4())
        resourceids, tile_ct = create_test_resources_and_tiles(self.search_model_graphid, self.search_model_name_nodeid, loadid)
        result = self.bulk_deleter.delete_resources(self.user.id, loadid, self.search_model_graphid, resourceids, verbose=False)

        self.assertTrue(result['success'])
        self.assertEqual(result['deleted_count'], len(resourceids))

    def test_delete_tiles(self):
        # Test to ensure tiles are deleted properly.
        loadid = str(uuid.uuid4())
        resourceids, tile_ct = create_test_resources_and_tiles(self.search_model_graphid, self.search_model_name_nodeid, loadid)
        result = self.bulk_deleter.delete_tiles(self.user.id, loadid, self.search_model_name_nodeid, resourceids)

        self.assertTrue(result['success'])
        # TODO: the test below needs result to include deleted_count, which it currently does not because of #10858
        # self.assertEqual(result['deleted_count'], tile_ct)

        # self.bulk_deleter.index_resource_deletion(loadid, resourceids)

    @classmethod
    def tearDownClass(self):
        self.user.delete()
        Tile.objects.filter(nodegroup_id=self.search_model_name_nodeid).delete()
        Resource.objects.filter(graph_id=self.search_model_graphid).delete()
        models.GraphModel.objects.filter(pk=self.search_model_graphid).delete()
        super().tearDownClass()


def create_test_resources_and_tiles(graphid, nodeid, transaction_id):
    count = 10
    test_resourceids = [str(uuid.uuid4()) for x in range(count)]
    for x in range(count):
        r = Resource(graph_id=graphid)
        t = Tile.get_blank_tile(nodeid, resourceid=test_resourceids[x])
        t.data[nodeid] = {"en": {"value": f"testing {x}", "direction": "ltr"}}
        r.tiles.append(t)
        r.save(transaction_id=transaction_id)
    return test_resourceids, count