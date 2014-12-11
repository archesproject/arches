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
from django.core import management
from django.test import SimpleTestCase, TestCase
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.data_management.resources.importer import ResourceLoader
import arches.app.utils.data_management.resources.remover as resource_remover
from arches.management.commands.package_utils import resource_graphs
from arches.management.commands.package_utils import authority_files
from arches.app.models.entity import Entity

class BasicEntityTests(SimpleTestCase):
    def setUp(self):
        self.entity = TestEntityFactory.create(1)
        install()


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


class TestEntityFactory(object):
    @staticmethod
    def create(id='', value=''):
        entity = Entity()
        entity.entityid = id
        entity.entitytypeid = 'TEST.E1'
        entity.property = 'P1'
        entity.value = value
        entity.child_entities = []
        return entity



def install(path_to_source_data_dir=None):
    #truncate_db()
    # delete_index(index='concept_labels')
    # delete_index(index='entity')
    load_resource_graphs()
    #load_authority_files(path_to_source_data_dir)
    #resource_remover.truncate_resources()
    #load_resources()

def truncate_db():
    management.call_command('packages', operation='setup') 

def load_resource_graphs():
    resource_graphs.load_graphs(break_on_error=True, settings=test_settings)
    pass

def load_authority_files(path_to_files=None):
    authority_files.load_authority_files(break_on_error=True)

def delete_index(index=None):
    se = SearchEngineFactory().create()
    se.delete(index=index, force=True)
    pass

def load_resources(external_file=None):
    rl = ResourceLoader()
    if external_file != None:
        print 'loading:', external_file
        rl.load(external_file)
    else:
        for f in settings.BUSISNESS_DATA_FILES:
            rl.load(f)
