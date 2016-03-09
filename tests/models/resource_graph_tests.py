# coding: utf-8

import os
from tests import test_settings
from tests import test_setup
# from django.core import management
from django.test import SimpleTestCase, TestCase
# from arches.app.search.search_engine_factory import SearchEngineFactory
# from arches.app.utils.data_management.resources.importer import ResourceLoader
# import arches.app.utils.data_management.resources.remover as resource_remover
# from arches.management.commands.package_utils import resource_graphs
# from arches.management.commands.package_utils import authority_files
from arches.app.models import models
# from arches.app.models.resource import Resource
from arches.app.models.concept import Concept
from arches.app.models.concept import ConceptValue
# from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"

# def setUpModule():
#     test_setup.install()

class ResourceGraphTests(TestCase):

    def test_initial_node_import(self):
        """
        Test that correct number of nodes load

        """
        from arches.management.commands.package_utils import resource_graphs
        from arches.app.models.models import Node

        resource_graphs.load_graphs(os.path.join(test_settings.RESOURCE_GRAPH_LOCATIONS))

        self.assertEqual(Node.objects.count(), 117)


    # def test_intial_edge_import(self):
    #     """
    #     Test that correct number of edges load

    #     """
