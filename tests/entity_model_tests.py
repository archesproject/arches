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

from django.test import SimpleTestCase, TestCase
from arches.app.models.entity import Entity

class BasicEntityTests(SimpleTestCase):
    def setUp(self):
        self.entity = TestEntityFactory.create(1)


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
                "relatedentities":[]
            }
            '''
        entity = Entity(json_string)
        self.assertEqual(entity.entityid, '1234')
        self.assertEqual(entity.entitytypeid, 'TEST.E1')
        self.assertEqual(entity.property, 'P1')
        self.assertEqual(entity.value, '123')
        self.assertEqual(entity.relatedentities, [])

    def test_init_entity_from_python(self):
        """
        Test to see that a json string can be parsed into a Entity instance
        """
        python_object = {
            "entityid":"1234",
            "entitytypeid":"TEST.E1",
            "property":"P1",
            "value":"123",
            "relatedentities":[]
        }
        entity = Entity(python_object)
        self.assertEqual(entity.entityid, '1234')
        self.assertEqual(entity.entitytypeid, 'TEST.E1')
        self.assertEqual(entity.property, 'P1')
        self.assertEqual(entity.value, '123')
        self.assertEqual(entity.relatedentities, [])


class TestEntityFactory(object):
    @staticmethod
    def create(id='', value=''):
        entity = Entity()
        entity.entityid = id
        entity.entitytypeid = 'TEST.E1'
        entity.property = 'P1'
        entity.value = value
        entity.relatedentities = []
        return entity