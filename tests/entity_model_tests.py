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
from tests import test_settings
from tests import test_setup
from django.core import management
from django.test import SimpleTestCase, TestCase
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.data_management.resources.importer import ResourceLoader
import arches.app.utils.data_management.resources.remover as resource_remover
from arches.management.commands.package_utils import resource_graphs
from arches.management.commands.package_utils import authority_files
from arches.app.models import models
from arches.app.models.entity import Entity
from arches.app.models.resource import Resource
from arches.app.models.concept import Concept
from arches.app.models.concept import ConceptValue
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"

def setUpModule():
    test_setup.install()

class BasicEntityTests(SimpleTestCase):

    # def setUp(self):
    #     global run_install
    #     if run_install:
    #         print '-' * 80
    #         #test_setup.install()
    #         run_install = False
    #     pass


    def test_init_entity_from_json(self):
        """
        Test to see that a json string can be parsed into a Entity instance

        """
        json_string = '''
            {
                "entityid":"1234",
                "entitytypeid":"TEST.E1",
                "property":"P1",
                "value":"123",
                "child_entities":[]
            }
            '''
        entity = Entity(json_string)
        self.assertEqual(entity.entityid, '1234')
        self.assertEqual(entity.entitytypeid, 'TEST.E1')
        self.assertEqual(entity.property, 'P1')
        self.assertEqual(entity.value, '123')
        self.assertEqual(entity.child_entities, [])

    def test_init_entity_from_python(self):
        """
        Test to see that a json string can be parsed into a Entity instance
        """
        python_object = {
            "entityid":"1234",
            "entitytypeid":"TEST.E1",
            "property":"P1",
            "value":"123",
            "child_entities":[]
        }
        entity = Entity(python_object)
        self.assertEqual(entity.entityid, '1234')
        self.assertEqual(entity.entitytypeid, 'TEST.E1')
        self.assertEqual(entity.property, 'P1')
        self.assertEqual(entity.value, '123')
        self.assertEqual(entity.child_entities, [])

    def test_save(self):
        val = models.Values.objects.get(value='Legal')
        python_object = {
            "entityid":"",
            "entitytypeid":"PERSON.E1",
            "value":"",
            "property":"P1",
            "child_entities":[{
                "entityid":"",
                "entitytypeid":"NAME.E1",
                "value":"Alexei",
                "property":"P1",
                "child_entities":[{
                    "entityid":"",
                    "entitytypeid":"NAME_TYPE.E1",
                    "value":val.pk,
                    "property":"P1",
                    "child_entities":[]
                }]
            }]
        }
        entity = Entity(python_object)
        entity._save()
        self.assertNotEqual(python_object['entityid'], entity.entityid)

        entity = Entity().get(entity.entityid)
        self.assertEqual(entity.child_entities[0].value, 'Alexei')
        self.assertEqual(entity.child_entities[0].child_entities[0].value, str(val.pk))
    
    def test_post_save_data_integrity2(self):
        python_object = {
            "entityid":"",
            "entitytypeid":"PERSON.E1",
            "value":"",
            "property":"P1",
            "child_entities":[{
                "entityid":"",
                "entitytypeid":"LOCATION.E1",
                "value":"",
                "property":"P1",
                "child_entities":[{
                    "entityid":"",
                    "entitytypeid":"PERIOD.E1",
                    "value":"",
                    "property":"P1",
                    "child_entities":[{
                        "entityid":"",
                        "entitytypeid":"ADDRESS.E1",
                        "value":"859",
                        "property":"P1",
                        "child_entities":[]
                    }]
                }]
            }]
        }
        entity = Resource(python_object)
        entity.save()
        self.assertNotEqual(python_object['entityid'], entity.entityid)

        entity = Resource().get(entity.entityid)
        self.assertEqual(int(entity.child_entities[0].child_entities[0].child_entities[0].value), 859)
        
        entity.child_entities[0].child_entities = []

        count_of_entities_before_save = models.Entities.objects.count()
        entity.save()
        count_of_entities_after_save = models.Entities.objects.count()

        # test for database integrity
        self.assertEqual(count_of_entities_before_save - count_of_entities_after_save, 3)
        self.assertEqual(models.Relations.objects.count(), 0)

    def test_delete_of_entity(self):
        val = models.Values.objects.get(value='Legal')
        python_object = {
            "entityid":"",
            "entitytypeid":"PERSON.E1",
            "value":"",
            "property":"P1",
            "child_entities":[{
                "entityid":"",
                "entitytypeid":"NAME.E1",
                "value":"Alexei",
                "property":"P1",
                "child_entities":[{
                    "entityid":"",
                    "entitytypeid":"NAME_TYPE.E1",
                    "value":val.pk,
                    "property":"P1",
                    "child_entities":[]
                }]
            },{
                "entityid":"",
                "entitytypeid":"LOCATION.E1",
                "value":"",
                "property":"P1",
                "child_entities":[{
                    "entityid":"",
                    "entitytypeid":"PERIOD.E1",
                    "value":"",
                    "property":"P1",
                    "child_entities":[{
                        "entityid":"",
                        "entitytypeid":"ADDRESS.E1",
                        "value":"859",
                        "property":"P1",
                        "child_entities":[]
                    }]
                }]
            }]
        }

        entity = Resource(python_object)
        entity.save()

        count_of_entities_before_delete = models.Entities.objects.count()
        count_of_relations_before_delete = models.Relations.objects.count()
        count_of_strings_before_delete = models.Strings.objects.count()
        count_of_numbers_before_delete = models.Numbers.objects.count()
        count_of_domains_before_delete = models.Domains.objects.count()
        entity.delete()
        count_of_entities_after_delete = models.Entities.objects.count()
        count_of_relations_after_delete = models.Relations.objects.count()
        count_of_strings_after_delete = models.Strings.objects.count()
        count_of_numbers_after_delete = models.Numbers.objects.count()
        count_of_domains_after_delete = models.Domains.objects.count()


        with self.assertRaises(models.Entities.DoesNotExist):
            Resource().get(entity.entityid)

        self.assertEqual(count_of_entities_before_delete - count_of_entities_after_delete, 6)
        self.assertEqual(count_of_relations_before_delete - count_of_relations_after_delete, 5)
        self.assertEqual(count_of_strings_before_delete - count_of_strings_after_delete, 1)
        self.assertEqual(count_of_numbers_before_delete - count_of_numbers_after_delete, 1)
        self.assertEqual(count_of_domains_before_delete - count_of_domains_after_delete, 1)

    def test_set_entity_value(self):
        python_object = {
            "entityid":"",
            "entitytypeid":"PERSON.E1",
            "value":"",
            "property":"P1",
            "child_entities":[]
        }
        entity1 = Resource(python_object)
        entity1.save()
        self.assertNotEqual(python_object['entityid'], entity1.entityid)

        entity2 = Resource().get(entity1.entityid)
        entity2.set_entity_value('ADDRESS.E1', '5703')
        entity2.save()

        entity3 = Resource().get(entity2.entityid)
        self.assertEqual(int(entity3.child_entities[0].child_entities[0].child_entities[0].value), 5703)

# def get_db_stats():
#     return {
#         'entities': models.Entities.objects.count(),
#         'relations': models.Relations.objects.count(),
#         'strings': models.Strings.objects.count(),
#         'numbers': models.Numbers.objects.count(),
#         'domains': models.Domains.objects.count()
#     }