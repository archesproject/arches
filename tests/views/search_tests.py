'''
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
'''

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import os
import json
import time
from tests.base_test import ArchesTestCase
from django.core.urlresolvers import reverse
from django.test.client import Client
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.data_management.resources.importer import  BusinessDataImporter
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory


# these tests can be run from the command line via
# python manage.py test tests/views/search_tests.py --pattern="*.py" --settings="tests.test_settings"


class SearchTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        se = SearchEngineFactory().create()
        se.delete_index(index='strings')
        se.delete_index(index='resource')

        cls.client = Client()
        cls.client.login(username='admin', password='admin')
        
        models.ResourceInstance.objects.all().delete()
        with open(os.path.join('tests/fixtures/resource_graphs/Search Test Model.json'), 'rU') as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile['graph'])

        cls.search_model_graphid = 'e503a445-fa5f-11e6-afa8-14109fd34195'
        cls.search_model_cultural_period_nodeid = '7a182580-fa60-11e6-96d1-14109fd34195'
        cls.search_model_creation_date_nodeid = '1c1d05f5-fa60-11e6-887f-14109fd34195'
        cls.search_model_name_nodeid = '2fe14de3-fa61-11e6-897b-14109fd34195'

        # Add a concept that defines a min and max date
        concept = {
            "id": "00000000-0000-0000-0000-000000000001",
            "legacyoid": "ARCHES",
            "nodetype": "ConceptScheme",
            "values": [],
            "subconcepts": [
                {
                    "values": [
                        {
                            "value": "ANP TEST",
                            "language": "en-US",
                            "category": "label",
                            "type": "prefLabel",
                            "id": "",
                            "conceptid": ""
                        },
                        {
                            "value": "1950",
                            "language": "en-US",
                            "category": "note",
                            "type": "min year",
                            "id": "",
                            "conceptid": ""
                        },
                        {
                            "value": "1980",
                            "language": "en-US",
                            "category": "note",
                            "type": "max year",
                            "id": "",
                            "conceptid": ""
                        }
                    ],
                    "relationshiptype": "hasTopConcept",
                    "nodetype": "Concept",
                    "id": "",
                    "legacyoid": "",
                    "subconcepts": [],
                    "parentconcepts": [],
                    "relatedconcepts": []
                }
            ]
        }

        post_data = JSONSerializer().serialize(concept)
        content_type = 'application/x-www-form-urlencoded'
        response = cls.client.post(reverse('concept', kwargs={'conceptid':'00000000-0000-0000-0000-000000000001'}), post_data, content_type)
        response_json = json.loads(response.content)
        valueid = response_json['subconcepts'][0]['values'][0]['id']

        # add resource instance with only a cultural period defined
        cls.cultural_period_resource = Resource(graph_id=cls.search_model_graphid)
        tile = Tile(data={cls.search_model_cultural_period_nodeid: [valueid]},nodegroup_id=cls.search_model_cultural_period_nodeid)
        cls.cultural_period_resource.tiles.append(tile)
        cls.cultural_period_resource.save()

        # add resource instance with only a creation date defined
        cls.date_resource = Resource(graph_id=cls.search_model_graphid)
        tile = Tile(data={cls.search_model_creation_date_nodeid: '1941-01-01'},nodegroup_id=cls.search_model_creation_date_nodeid)
        cls.date_resource.tiles.append(tile)
        tile = Tile(data={cls.search_model_name_nodeid: 'testing 123'},nodegroup_id=cls.search_model_name_nodeid)
        cls.date_resource.tiles.append(tile)
        cls.date_resource.save()

        # add resource instance with with no dates or periods defined
        cls.name_resource = Resource(graph_id=cls.search_model_graphid)
        tile = Tile(data={cls.search_model_name_nodeid: 'some test name'},nodegroup_id=cls.search_model_name_nodeid)
        cls.name_resource.tiles.append(tile)
        cls.name_resource.save()

        # add delay to allow for indexes to be updated
        time.sleep(1)
        
    @classmethod
    def tearDownClass(cls):
        pass


    def test_temporal_only_search_1(self):
        """
        Search for resources that fall between 1940 and 1960

        """

        temporal_filter = {"fromDate":"1940-01-01","toDate":"1960-01-01","dateNodeId":"","inverted":False}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json['results']['hits']['total'], 2)
        self.assertItemsEqual(extract_pks(response_json), [str(self.cultural_period_resource.pk), str(self.date_resource.pk)])

    def test_temporal_only_search_2(self):
        """
        Search for resources that DON'T fall between 1940 and 1960

        """

        temporal_filter = {"fromDate":"1940-01-01","toDate":"1960-01-01","dateNodeId":"","inverted":True}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json['results']['hits']['total'], 1)
        self.assertItemsEqual(extract_pks(response_json), [str(self.cultural_period_resource.pk)])

    def test_temporal_only_search_3(self):
        """
        Search for resources that DON'T fall between 1940 and 1960 and date node is supplied

        """

        temporal_filter = {"fromDate":"1940-01-01","toDate":"1960-01-01","dateNodeId":self.search_model_creation_date_nodeid,"inverted":False}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json['results']['hits']['total'], 1)
        self.assertItemsEqual(extract_pks(response_json), [str(self.date_resource.pk)])

    def test_temporal_only_search_4(self):
        """
        Search for resources that DON'T fall between 1940 and 1960

        """

        temporal_filter = {"fromDate":"1940-01-01","toDate":"1960-01-01","dateNodeId":self.search_model_creation_date_nodeid,"inverted":True}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json['results']['hits']['total'], 0)

    def test_temporal_only_search_5(self):
        """
        Search for resources that fall between 1950 and 1960 (the cultural period resource)

        """

        temporal_filter = {"fromDate":"1950-01-01","toDate":"1960-01-01","dateNodeId":"","inverted":False}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json['results']['hits']['total'], 1)
        self.assertItemsEqual(extract_pks(response_json), [str(self.cultural_period_resource.pk)])

    def test_temporal_only_search_6(self):
        """
        Search for resources that DON'T fall between 1950 and 1960 (the cultural period resource)

        """

        temporal_filter = {"fromDate":"1950-01-01","toDate":"1960-01-01","dateNodeId":"","inverted":True}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json['results']['hits']['total'], 2)
        self.assertItemsEqual(extract_pks(response_json), [str(self.cultural_period_resource.pk), str(self.date_resource.pk)])


    def test_temporal_only_search_7(self):
        """
        Search for resources that fall between 1990 and 2000

        """

        temporal_filter = {"fromDate":"1990-01-01","toDate":"2000-01-01","dateNodeId":"","inverted":False}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json['results']['hits']['total'], 0)

    def test_temporal_only_search_8(self):
        """
        Search for resources that DON'T fall between 1990 and 2000

        """

        temporal_filter = {"fromDate":"1990-01-01","toDate":"2000-01-01","dateNodeId":"","inverted":True}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json['results']['hits']['total'], 2)
        self.assertItemsEqual(extract_pks(response_json), [str(self.cultural_period_resource.pk), str(self.date_resource.pk)])

    def test_temporal_only_search_9(self):
        """
        Search for resources that are greater then 1940

        """

        temporal_filter = {"fromDate":"1940-01-01","toDate":"","dateNodeId":"","inverted":False}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json['results']['hits']['total'], 2)
        self.assertItemsEqual(extract_pks(response_json), [str(self.cultural_period_resource.pk), str(self.date_resource.pk)])

    def test_temporal_only_search_10(self):
        """
        Search for resources that AREN'T greater then 1940

        """

        temporal_filter = {"fromDate":"1940-01-01","toDate":"","dateNodeId":"","inverted":True}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json['results']['hits']['total'], 0)

    def test_temporal_only_search_11(self):
        """
        Search for resources that AREN'T greater then 1950

        """

        temporal_filter = {"fromDate":"1950-01-01","toDate":"","dateNodeId":"","inverted":True}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json['results']['hits']['total'], 2)
        self.assertItemsEqual(extract_pks(response_json), [str(self.cultural_period_resource.pk), str(self.date_resource.pk)])

    def test_temporal_and_term_search_1(self):
        """
        Search for resources that fall between 1940 and 1960 and have the string "test" in them

        """

        temporal_filter = {"fromDate":"1940-01-01","toDate":"1960-01-01","dateNodeId":"","inverted":False}
        term_filter = [{"type":"string","context":"","context_label":"","id":"test","text":"test","value":"test","inverted":False}]
        response_json = get_response_json(self.client, temporal_filter=temporal_filter, term_filter=term_filter)
        self.assertEqual(response_json['results']['hits']['total'], 1)
        self.assertItemsEqual(extract_pks(response_json), [str(self.date_resource.pk)])

    def test_temporal_and_term_search_2(self):
        """
        Search for resources that DON'T fall between 1940 and 1960 and have the string "test" in them

        """

        temporal_filter = {"fromDate":"1940-01-01","toDate":"1960-01-01","dateNodeId":"","inverted":True}
        term_filter = [{"type":"string","context":"","context_label":"","id":"test","text":"test","value":"test","inverted":False}]
        response_json = get_response_json(self.client, temporal_filter=temporal_filter, term_filter=term_filter)
        self.assertEqual(response_json['results']['hits']['total'], 0)



def extract_pks(response_json):
    return [result['_source']['resourceinstanceid'] for result in response_json['results']['hits']['hits']]

def get_response_json(client, temporal_filter=None, term_filter=None):
    query = {}
    if temporal_filter is not None:
        query['temporalFilter'] = JSONSerializer().serialize(temporal_filter)
    if term_filter is not None:
        query['termFilter'] = JSONSerializer().serialize(term_filter)

    response = client.get('/search/resources', query)
    response_json = json.loads(response.content)
    return response_json
