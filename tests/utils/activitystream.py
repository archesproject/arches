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

import os
from tests import test_settings
from tests.base_test import ArchesTestCase
from rdflib import Namespace
from arches.app.utils.activity_stream_jsonld import ActivityStreamCollection, ActivityStreamCollectionPage

# mocking libraries
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.models.models import ResourceInstance
from arches.app.utils.skos import SKOSReader
from mock import Mock
from uuid import uuid4
from itertools import cycle
from datetime import datetime
import json
from arches.app.models.models import ResourceInstance, GraphModel

ARCHES_NS = Namespace("https://arches.getty.edu/")
CIDOC_NS = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
COL_NS = Namespace(ARCHES_NS["history/"])

base_uris = {"root": COL_NS, "first": COL_NS["1"], "last": COL_NS["20"]}

page_1_uris = {"next": COL_NS["4"], "prev": COL_NS["2"], "root": COL_NS, "this": COL_NS["3"]}

totalItems = 1000


class editlog_fuzzer(object):
    def __init__(self):
        self.types = cycle(["create", "tile create", "tile edit", "tile delete", "delete"])
        self.resources = [str(uuid4())]
        self.classids = cycle([str(uuid4()) for x in range(3)])
        self.users = cycle(
            [
                {"userid": 1, "user_username": "admin", "user_firstname": "admin", "user_lastname": "admin"},
                {"userid": 2, "user_username": "benosteen", "user_firstname": "Ben", "user_lastname": "O'Steen"},
                {"userid": 3, "user_username": "rando", "user_firstname": "ran", "user_lastname": "do"},
            ]
        )
        self.gm = GraphModel.objects.get(pk="fd0a5907-e11b-11e8-821b-a4d18cec433a")

    def generate_event(self):
        e_type = next(self.types)
        user = next(self.users)
        e = Mock()
        e.editlogid = str(uuid4())
        e.resourcedisplayname = "Resource Display Name"
        e.resourceclassid = next(self.classids)
        if e_type == "create":
            self.resources.append(str(uuid4()))
            r = ResourceInstance(resourceinstanceid=self.resources[-1], graph=self.gm)
            r.save()
        e.resourceinstanceid = self.resources[-1]
        e.nodegroupid = str(uuid4())
        e.tileinstanceid = str(uuid4())
        e.edittype = e_type
        e.newvalue = []
        e.oldvalue = []
        e.newprovisionalvalue = []
        e.oldprovisionalvalue = []
        e.timestamp = datetime.now()
        e.userid = user["userid"]
        e.user_username = user["user_username"]
        e.user_firstname = user["user_firstname"]
        e.user_lastname = user["user_lastname"]
        return e

    def get_events(self, number_of):
        for x in range(number_of):
            yield self.generate_event()


class ActivityStreamCollectionTests(ArchesTestCase):
    """
    Unit tests for the `to_rdf` method on Datatype classes.
    """

    @classmethod
    def setUpClass(cls):
        ResourceInstance.objects.all().delete()

        for skospath in ["tests/fixtures/data/rdf_export_thesaurus.xml", "tests/fixtures/data/rdf_export_collections.xml"]:
            skos = SKOSReader()
            rdf = skos.read_file(skospath)
            ret = skos.save_concepts_from_skos(rdf)

        # Models
        for model_name in ["object_model", "document_model"]:
            with open(os.path.join("tests/fixtures/resource_graphs/rdf_export_{0}.json".format(model_name)), "rU") as f:
                archesfile = JSONDeserializer().deserialize(f)
            ResourceGraphImporter(archesfile["graph"])

    def setUp(self):
        # for RDF/JSON-LD export tests
        self.C = ActivityStreamCollection(base_uris, totalItems, base_uri_for_arches="https://arches.getty.edu")
        self.EF = editlog_fuzzer()

    def test_jsonld_export_function(self):
        jsontxt = self.C.to_jsonld()
        doc = json.loads(jsontxt)

    def test_obj(self):
        obj = self.C.to_obj()
        self.assertTrue(obj["id"] == base_uris["root"])
        self.assertTrue("first" in obj)
        self.assertTrue("last" in obj)

    def test_generate_page(self):
        collection_page = self.C.generate_page(page_1_uris, reversed([x for x in self.EF.get_events(10)]))
        outtxt = collection_page.to_jsonld()
