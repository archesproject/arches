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

from django.test import TestCase
from arches.app.models import models

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"

def setUpModule():
    pass

def tearDownModule():
    pass

class ArchesTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @classmethod
    def deleteGraph(cls, root):
        def delete_children(node):
            if node.nodegroup:
                node.nodegroup.delete()
            for edge in models.Edge.objects.filter(rangenode=node):
                edge.delete()
                delete_children(edge.rangenode)
         
        delete_children(root)
        root.delete()

    def setUp(self):
        pass

    def tearDown(self):
        pass