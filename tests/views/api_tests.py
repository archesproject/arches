"""
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
"""

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import os
from tests import test_settings
from tests.base_test import ArchesTestCase
from django.urls import reverse
from django.test.client import RequestFactory, Client
from arches.app.views.api import APIBase
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

# these tests can be run from the command line via
# python manage.py test tests/views/api_tests.py --pattern="*.py" --settings="tests.test_settings"


class APITests(ArchesTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        geojson_nodeid = "3ebc6785-fa61-11e6-8c85-14109fd34195"
        cls.loadOntology()
        with open(os.path.join("tests/fixtures/resource_graphs/unique_graph_shape.json"), "rU") as f:
            json = JSONDeserializer().deserialize(f)
            cls.unique_graph = Graph(json["graph"][0])
            cls.unique_graph.save()

        with open(os.path.join("tests/fixtures/resource_graphs/ambiguous_graph_shape.json"), "rU") as f:
            json = JSONDeserializer().deserialize(f)
            cls.ambiguous_graph = Graph(json["graph"][0])
            cls.ambiguous_graph.save()

        with open(os.path.join("tests/fixtures/resource_graphs/phase_type_assignment.json"), "rU") as f:
            json = JSONDeserializer().deserialize(f)
            cls.phase_type_assignment_graph = Graph(json["graph"][0])
            cls.phase_type_assignment_graph.save()

    def test_api_base_view(self):
        """
        Test that our custom header parameters get pushed on to the GET QueryDict

        """

        factory = RequestFactory(HTTP_X_ARCHES_VER="2.1")
        view = APIBase.as_view()

        request = factory.get(reverse("mobileprojects", kwargs={}), {"ver": "2.0"})
        request.user = None
        response = view(request)
        self.assertEqual(request.GET.get("ver"), "2.0")

        request = factory.get(reverse("mobileprojects"), kwargs={})
        request.user = None
        response = view(request)
        self.assertEqual(request.GET.get("ver"), "2.1")
