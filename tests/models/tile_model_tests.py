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

from uuid import UUID, uuid4
from arches.app.utils.betterJSONSerializer import JSONSerializer
from tests.base_test import ArchesTestCase
from django.contrib.auth.models import User
from django.http import HttpRequest
from arches.app.const import DefaultLifecycleStates
from arches.app.models.graph import Graph
from arches.app.models.tile import Tile, TileCardinalityError, TileValidationError
from arches.app.models.resource import Resource
from arches.app.models.models import (
    CardModel,
    CardXNodeXWidget,
    Node,
    NodeGroup,
    ResourceInstance,
    ResourceXResource,
    TileModel,
    Widget,
)

from tests.constants import *

# these tests can be run from the command line via
# python manage.py test tests.models.tile_model_tests --settings="tests.test_settings"


class TileTests(ArchesTestCase):
    graph_fixtures = [
        "rdf_export_document_model",
        "rdf_export_object_model",
        "Cardinality Test Model",
        "All_Datatypes",
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_users()
        resources = [
            ResourceInstance(
                pk=CardinalityTestGraph.RESOURCE1.value,
                legacyid=CardinalityTestGraph.RESOURCE1.value,
                graph_id=CardinalityTestGraph.GRAPH_ID.value,
                createdtime="1/1/2000",
                resource_instance_lifecycle_state_id=DefaultLifecycleStates.PERPETUAL.value,
            ),
            ResourceInstance(
                pk=AllDatatypesTestGraph.RESOURCE1.value,
                legacyid=AllDatatypesTestGraph.RESOURCE1.value,
                graph_id=AllDatatypesTestGraph.GRAPH_ID.value,
                createdtime="1/1/2000",
                resource_instance_lifecycle_state_id=DefaultLifecycleStates.PERPETUAL.value,
            ),
        ]
        resources = ResourceInstance.objects.bulk_create(resources)
        nodegroups = [
            NodeGroup(pk=pk, cardinality="n")
            for pk in [
                "99999999-0000-0000-0000-000000000001",
                "32999999-0000-0000-0000-000000000000",
                "19999999-0000-0000-0000-000000000000",
                "21111111-0000-0000-0000-000000000000",
                "41111111-0000-0000-0000-000000000000",
            ]
        ]
        nodegroups = NodeGroup.objects.bulk_create(nodegroups)

    def create_tile(self):
        """Can't do this in setUpTestData given count assertions in other tests."""
        tileid = uuid4()
        nodegroupid = "99999999-0000-0000-0000-000000000001"
        tile = TileModel.objects.create(
            pk=tileid,
            resourceinstance_id=CardinalityTestGraph.RESOURCE1.value,
            nodegroup_id=nodegroupid,
        )
        grouping_node = Node.objects.create(
            pk=nodegroupid,
            graph=tile.resourceinstance.graph,
            nodegroup_id=nodegroupid,
            alias="Statement",
            datatype="semantic",
            istopnode=False,
        )
        nodegroup = grouping_node.nodegroup
        nodegroup.grouping_node = grouping_node
        nodegroup.save()
        return TileModel.objects.get(pk=tile.pk)

    def test_tile_str(self):
        sample_tile = self.create_tile()
        self.assertEqual(f"{sample_tile}", f"Statement ({sample_tile.pk})")

    def test_tile_str_no_nodegroup(self):
        sample_tile = self.create_tile()
        sample_tile.nodegroup = None
        self.assertEqual(f"{sample_tile}", f"None ({sample_tile.pk})")

    def test_load_from_python_dict(self):
        """
        Test that we can initialize a Tile object from a Python dictionary

        """

        json = {
            "tiles": [
                {
                    "tiles": [],
                    "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
                    "parenttile_id": "",
                    "nodegroup_id": "19999999-0000-0000-0000-000000000000",
                    "tileid": "",
                    "data": {
                        "20000000-0000-0000-0000-000000000004": {
                            "en": {"value": "TEST 1", "direction": "ltr"},
                            "es": {"value": "PRUEBA 1", "direction": "ltr"},
                        },
                        "20000000-0000-0000-0000-000000000002": {
                            "en": {"value": "TEST 2", "direction": "ltr"}
                        },
                        "20000000-0000-0000-0000-000000000003": {
                            "en": {"value": "TEST 3", "direction": "ltr"}
                        },
                    },
                },
                {
                    "tiles": [],
                    "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
                    "parenttile_id": "",
                    "nodegroup_id": "32999999-0000-0000-0000-000000000000",
                    "tileid": "",
                    "data": {
                        "20000000-0000-0000-0000-000000000004": {
                            "en": {"value": "TEST 4", "direction": "ltr"}
                        },
                        "20000000-0000-0000-0000-000000000002": {
                            "en": {"value": "TEST 5", "direction": "ltr"}
                        },
                    },
                },
            ],
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": "20000000-0000-0000-0000-000000000001",
            "tileid": "",
            "data": {},
        }

        t = Tile(json)

        self.assertEqual(t.resourceinstance_id, CardinalityTestGraph.RESOURCE1.value)
        self.assertEqual(t.data, {})
        self.assertEqual(
            t.tiles[0].data["20000000-0000-0000-0000-000000000004"]["en"]["value"],
            "TEST 1",
        )

    def test_save(self):
        """
        Test that we can save a Tile object back to the database

        """
        login = self.client.login(username="admin", password="admin")

        json = {
            "tiles": [
                {
                    "tiles": [],
                    "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
                    "parenttile_id": "",
                    "nodegroup_id": "72048cb3-adbc-11e6-9ccf-14109fd34195",
                    "tileid": "",
                    "data": {
                        "72048cb3-adbc-11e6-9ccf-14109fd34195": {
                            "en": {"value": "TEST 1", "direction": "ltr"},
                            "es": {"value": "PRUEBA 1", "direction": "ltr"},
                        }
                    },
                }
            ],
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": "7204869c-adbc-11e6-8bec-14109fd34195",
            "tileid": "",
            "data": {},
        }

        t = Tile(json)
        t.save(index=False)

        tiles = Tile.objects.filter(
            resourceinstance_id=CardinalityTestGraph.RESOURCE1.value
        )

        self.assertEqual(tiles.count(), 2)

    def test_simple_get(self):
        """
        Test that we can get a Tile object

        """

        json = {
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": "72048cb3-adbc-11e6-9ccf-14109fd34195",
            "tileid": "",
            "data": {
                "72048cb3-adbc-11e6-9ccf-14109fd34195": {
                    "en": {"value": "TEST 1", "direction": "ltr"},
                    "es": {"value": "PRUEBA 1", "direction": "ltr"},
                }
            },
        }

        t = Tile(json)
        t.save(index=False)

        t2 = Tile.objects.get(tileid=t.tileid)

        self.assertEqual(t.tileid, t2.tileid)
        self.assertEqual(
            t2.data["72048cb3-adbc-11e6-9ccf-14109fd34195"]["en"]["value"], "TEST 1"
        )
        self.assertEqual(
            t2.data["72048cb3-adbc-11e6-9ccf-14109fd34195"]["es"]["value"], "PRUEBA 1"
        )

    def test_create_new_authoritative(self):
        """
        Test that a new authoritative tile is created when a user IS a reviwer.

        """

        user = self.test_users["admin"]

        json = {
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": "72048cb3-adbc-11e6-9ccf-14109fd34195",
            "tileid": "",
            "data": {
                "72048cb3-adbc-11e6-9ccf-14109fd34195": {
                    "en": {"value": "AUTHORITATIVE", "direction": "ltr"}
                }
            },
        }

        authoritative_tile = Tile(json)
        request = HttpRequest()
        request.user = user
        authoritative_tile.save(index=False, request=request)

        self.assertEqual(authoritative_tile.is_provisional(), False)

    def test_create_new_provisional(self):
        """
        Test that a new provisional tile is created when a user IS NOT a reviwer.

        """

        json = {
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": "72048cb3-adbc-11e6-9ccf-14109fd34195",
            "tileid": "",
            "data": {
                "72048cb3-adbc-11e6-9ccf-14109fd34195": {
                    "en": {"value": "PROVISIONAL", "direction": "ltr"}
                }
            },
        }

        provisional_tile = Tile(json)
        request = HttpRequest()
        user = self.test_users["testuser"]
        request.user = user
        provisional_tile.save(index=False, request=request)

        self.assertEqual(provisional_tile.is_provisional(), True)

    def test_save_provisional_from_athoritative(self):
        """
        Test that a provisional edit is created when a user that is not a
        reviewer edits an athoritative tile

        """

        json = {
            "tiles": [
                {
                    "tiles": [],
                    "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
                    "parenttile_id": "",
                    "nodegroup_id": "72048cb3-adbc-11e6-9ccf-14109fd34195",
                    "tileid": "",
                    "data": {
                        "72048cb3-adbc-11e6-9ccf-14109fd34195": {
                            "en": {"value": "AUTHORITATIVE", "direction": "ltr"}
                        }
                    },
                }
            ],
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": "7204869c-adbc-11e6-8bec-14109fd34195",
            "tileid": "",
            "data": {},
        }

        t = Tile(json)
        t.save(index=False)
        user = self.test_users["testuser"]
        login = self.client.login(
            username=user.username,
            password=user.password,
        )
        tiles = Tile.objects.filter(
            resourceinstance_id=CardinalityTestGraph.RESOURCE1.value
        )

        provisional_tile = None
        for tile in tiles:
            provisional_tile = tile
            provisional_tile.data["72048cb3-adbc-11e6-9ccf-14109fd34195"] = {
                "en": {"value": "PROVISIONAL", "direction": "ltr"}
            }
        request = HttpRequest()
        request.user = user
        provisional_tile.save(index=False, request=request)
        tiles = Tile.objects.filter(
            resourceinstance_id=CardinalityTestGraph.RESOURCE1.value
        )

        provisionaledits = provisional_tile.provisionaledits
        self.assertEqual(tiles.count(), 2)
        self.assertIn(
            "72048cb3-adbc-11e6-9ccf-14109fd34195",
            provisional_tile.data,
            provisional_tile,
        )
        self.assertEqual(
            provisional_tile.data["72048cb3-adbc-11e6-9ccf-14109fd34195"]["en"][
                "value"
            ],
            "AUTHORITATIVE",
            provisional_tile,
        )
        self.assertEqual(provisionaledits[str(user.id)]["action"], "update")
        self.assertEqual(provisionaledits[str(user.id)]["status"], "review")

    def test_update_sortorder_provisional_tile(self):
        user = self.test_users["testuser"]
        json = {
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": "72048cb3-adbc-11e6-9ccf-14109fd34195",
            "tileid": "",
            "data": {
                "72048cb3-adbc-11e6-9ccf-14109fd34195": {
                    "en": {"value": "PROVISIONAL", "direction": "ltr"}
                }
            },
        }
        provisional_tile = Tile(json)
        request = HttpRequest()
        request.user = user
        provisional_tile.save(index=False, request=request)
        self.assertEqual(provisional_tile.sortorder, 0)

        with self.assertWarns(FutureWarning):
            obj, _ = TileModel.objects.update_or_create(
                pk=provisional_tile.pk, nodegroup_id=provisional_tile.nodegroup_id
            )
        obj.refresh_from_db()  # give test opportunity to fail on Django 4.2+

        self.assertEqual(obj.sortorder, 1)

    def test_is_fully_provisional(self):
        """
        Tests that a tile is marked as fully provisional even if it has falsey values in its data.
        """
        json = {
            "resourceinstance_id": AllDatatypesTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": AllDatatypesTestGraph.BOOLEAN_NODE_NODEGROUP.value,
            "tileid": "",
            "data": {
                str(AllDatatypesTestGraph.BOOLEAN_NODE_NODEGROUP.value): False,
                str(AllDatatypesTestGraph.BOOLEAN_SWITCH_NODE.value): None,
            },
        }

        tile = Tile(json)
        tile.save(index=False)

        user = self.test_users["testuser"]
        login = self.client.login(
            username=user.username,
            password=user.password,
        )

        tile.data[str(AllDatatypesTestGraph.BOOLEAN_SWITCH_NODE.value)] = True

        request = HttpRequest()
        request.user = user
        tile.save(index=False, request=request)
        self.assertIs(tile.is_fully_provisional(), False)

    def test_tile_cardinality(self):
        """
        Tests that the tile is not saved if the cardinality is violated
        by testing to save a tile with the same values as an existing one.

        """

        user = self.test_users["admin"]
        first_json = {
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": "72048cb3-adbc-11e6-9ccf-14109fd34195",
            "tileid": "",
            "data": {
                "72048cb3-adbc-11e6-9ccf-14109fd34195": {
                    "en": {"value": "AUTHORITATIVE", "direction": "ltr"}
                }
            },
        }
        first_tile = Tile(first_json)
        request = HttpRequest()
        request.user = user
        first_tile.save(index=False, request=request)

        second_json = {
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": "72048cb3-adbc-11e6-9ccf-14109fd34195",
            "tileid": "",
            "data": {
                "72048cb3-adbc-11e6-9ccf-14109fd34195": {
                    "en": {"value": "AUTHORITATIVE", "direction": "ltr"}
                }
            },
        }
        second_tile = Tile(second_json)

        with self.assertRaises(TileCardinalityError):
            second_tile.save(index=False, request=request)

    def test_apply_provisional_edit(self):
        """
        Tests that provisional edit data is properly created

        """

        json = {
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": "72048cb3-adbc-11e6-9ccf-14109fd34195",
            "tileid": "",
            "data": {
                "72048cb3-adbc-11e6-9ccf-14109fd34195": {
                    "en": {"value": "TEST 1", "direction": "ltr"}
                }
            },
        }

        user = self.test_users["testuser"]
        provisional_tile = Tile(json)
        request = HttpRequest()
        request.user = user
        provisional_tile.save(index=False, request=request)
        provisional_tile.apply_provisional_edit(user, {"test": "test"}, "update")
        provisionaledits = provisional_tile.provisionaledits
        userid = str(user.id)
        self.assertEqual(provisionaledits[userid]["action"], "update")
        self.assertEqual(provisionaledits[userid]["reviewer"], None)
        self.assertEqual(provisionaledits[userid]["value"], {"test": "test"})
        self.assertEqual(provisionaledits[userid]["status"], "review")
        self.assertEqual(provisionaledits[userid]["reviewtimestamp"], None)

    def test_user_owns_provisional(self):
        """
        Tests that a user is the owner of a provisional edit

        """

        json = {
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": "72048cb3-adbc-11e6-9ccf-14109fd34195",
            "tileid": "",
            "data": {
                "72048cb3-adbc-11e6-9ccf-14109fd34195": {
                    "en": {"value": "TEST 1", "direction": "ltr"}
                }
            },
        }

        user = self.test_users["testuser"]
        provisional_tile = Tile(json)
        request = HttpRequest()
        request.user = user
        provisional_tile.save(index=False, request=request)

        self.assertEqual(provisional_tile.user_owns_provisional(user), True)

    def test_tile_deletion(self):
        """
        Tests that a tile is deleted when a user is a reviewer or owner.

        """

        json = {
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": "72048cb3-adbc-11e6-9ccf-14109fd34195",
            "tileid": "",
            "data": {
                "72048cb3-adbc-11e6-9ccf-14109fd34195": {
                    "en": {"value": "TEST 1", "direction": "ltr"}
                }
            },
        }

        owner = self.test_users["testuser"]
        reviewer = self.test_users["admin"]

        tile1 = Tile(json)
        owner_request = HttpRequest()
        owner_request.user = owner
        tile1.save(index=False, request=owner_request)
        tile1.delete(request=owner_request)

        tile2 = Tile(json)
        reviewer_request = HttpRequest()
        reviewer_request.user = reviewer
        tile2.save(index=False, request=reviewer_request)
        tile2.delete(request=reviewer_request)

        self.assertEqual(len(Tile.objects.all()), 0)

    def test_delete_empty_tile(self):
        tile = Tile(
            {
                "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
                "parenttile_id": "",
                "nodegroup_id": "72048cb3-adbc-11e6-9ccf-14109fd34195",
                "tileid": "",
                "data": {},
            }
        )
        tile.delete()

    def test_provisional_deletion(self):
        """
        Tests that a tile is NOT deleted if a user does not have the
        privlages to delete a tile and that the proper provisionaledit is
        applied.

        """

        json = {
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": "72048cb3-adbc-11e6-9ccf-14109fd34195",
            "tileid": "",
            "data": {
                "72048cb3-adbc-11e6-9ccf-14109fd34195": {
                    "en": {"value": "TEST 1", "direction": "ltr"}
                }
            },
        }

        provisional_user = self.test_users["testuser"]
        reviewer = self.test_users["admin"]

        tile = Tile(json)
        reviewer_request = HttpRequest()
        reviewer_request.user = reviewer
        tile.save(index=False, request=reviewer_request)

        provisional_request = HttpRequest()
        provisional_request.user = provisional_user
        tile.delete(request=provisional_request)

        self.assertEqual(len(Tile.objects.all()), 1)

    def test_related_resources_managed(self):
        """
        Test that related resource data is managed correctly and that the accompanying table is
        managed correctly.  Test that default ontology and inverse ontology infomation is applied properly.

        """

        json = {
            "data": {
                "551a7785-e222-11e8-9baa-a4d18cec433a": None,
                "6d75ab63-e222-11e8-82a6-a4d18cec433a": None,
                "a4157df0-e222-11e8-9acb-a4d18cec433a": None,
                "eb115780-e222-11e8-aaed-a4d18cec433a": [
                    {
                        "inverseOntologyProperty": "",
                        "ontologyProperty": "",
                        "resourceId": "92b2db6a-d13f-4cc7-aec7-e4caf91b45f8",
                        "resourceXresourceId": "",
                    },
                    {
                        "inverseOntologyProperty": "http://www.cidoc-crm.org/cidoc-crm/P62i_is_depicted_by",
                        "ontologyProperty": "http://www.cidoc-crm.org/cidoc-crm/P62_depicts",
                        "resourceId": "e72844fc-7bc0-4851-89ca-5bb1c6b3ba22",
                        "resourceXresourceId": "5f418480-534a-4dba-87d9-67eb27f0cc6a",
                    },
                ],
            },
            "nodegroup_id": "487154e3-e222-11e8-be46-a4d18cec433a",
            "parenttile_id": None,
            "provisionaledits": None,
            "resourceinstance_id": "654bb228-37e7-4beb-b0f9-b59b61b53577",
            "sortorder": 0,
            "tileid": "edbdef07-77fd-4bb6-9fef-641d4a65abce",
        }

        main_resource = Resource(
            pk=json["resourceinstance_id"],
            graph_id="c35fe0a1-df30-11e8-b280-a4d18cec433a",
        )
        main_resource.save(index=False)
        related_resource = Resource(
            pk="e72844fc-7bc0-4851-89ca-5bb1c6b3ba22",
            graph_id="c35fe0a1-df30-11e8-b280-a4d18cec433a",
        )
        related_resource.save(index=False)
        related_resource2 = Resource(
            pk="92b2db6a-d13f-4cc7-aec7-e4caf91b45f8",
            graph_id="c35fe0a1-df30-11e8-b280-a4d18cec433a",
        )
        related_resource2.save(index=False)

        t = Tile(json)
        t.save(index=False)

        resource_instances = ResourceXResource.objects.filter(tile=t.tileid)
        self.assertEqual(2, len(resource_instances))

        for ri in resource_instances:
            ri_dict = JSONSerializer().serializeToPython(ri)
            if (
                str(ri.relationshiptype)
                == "http://www.cidoc-crm.org/cidoc-crm/P62_depicts"
            ):
                expected = {
                    "inverserelationshiptype": "http://www.cidoc-crm.org/cidoc-crm/P62i_is_depicted_by",
                    "node_id": UUID("eb115780-e222-11e8-aaed-a4d18cec433a"),
                    "notes": "",
                    "relationshiptype": "http://www.cidoc-crm.org/cidoc-crm/P62_depicts",
                    "from_resource_graph_id": UUID(
                        "c35fe0a1-df30-11e8-b280-a4d18cec433a"
                    ),
                    "from_resource_id": UUID("654bb228-37e7-4beb-b0f9-b59b61b53577"),
                    "to_resource_id": UUID("e72844fc-7bc0-4851-89ca-5bb1c6b3ba22"),
                    "to_resource_graph_id": UUID(
                        "c35fe0a1-df30-11e8-b280-a4d18cec433a"
                    ),
                    "tile_id": UUID("edbdef07-77fd-4bb6-9fef-641d4a65abce"),
                }
                self.assertTrue(
                    all(item in ri_dict.items() for item in expected.items())
                )
            else:
                expected = {
                    "inverserelationshiptype": "http://www.cidoc-crm.org/cidoc-crm/P10i_contains",
                    "node_id": UUID("eb115780-e222-11e8-aaed-a4d18cec433a"),
                    "notes": "",
                    "relationshiptype": "http://www.cidoc-crm.org/cidoc-crm/P10_falls_within",
                    "from_resource_graph_id": UUID(
                        "c35fe0a1-df30-11e8-b280-a4d18cec433a"
                    ),
                    "to_resource_id": UUID("92b2db6a-d13f-4cc7-aec7-e4caf91b45f8"),
                    "to_resource_graph_id": UUID(
                        "c35fe0a1-df30-11e8-b280-a4d18cec433a"
                    ),
                    "tile_id": UUID("edbdef07-77fd-4bb6-9fef-641d4a65abce"),
                }
                self.assertTrue(
                    all(item in ri_dict.items() for item in expected.items())
                )

        # now test that when we delete a related resource it
        json = {
            "data": {
                "551a7785-e222-11e8-9baa-a4d18cec433a": None,
                "6d75ab63-e222-11e8-82a6-a4d18cec433a": None,
                "a4157df0-e222-11e8-9acb-a4d18cec433a": None,
                "eb115780-e222-11e8-aaed-a4d18cec433a": [
                    {
                        "inverseOntologyProperty": "",
                        "ontologyProperty": "http://www.cidoc-crm.org/cidoc-crm/P62_depicts",
                        "resourceId": "85b2db6a-d13f-4cc7-aec7-e4caf91b45f7",
                        "resourceXresourceId": "",
                    }
                ],
            },
            "nodegroup_id": "487154e3-e222-11e8-be46-a4d18cec433a",
            "parenttile_id": None,
            "provisionaledits": None,
            "resourceinstance_id": "654bb228-37e7-4beb-b0f9-b59b61b53577",
            "sortorder": 0,
            "tileid": "edbdef07-77fd-4bb6-9fef-641d4a65abce",
        }

        related_resource3 = Resource(
            pk="85b2db6a-d13f-4cc7-aec7-e4caf91b45f7",
            graph_id="c35fe0a1-df30-11e8-b280-a4d18cec433a",
        )
        related_resource3.save(index=False)

        t = Tile(json)
        t.save(index=False)

        resource_instance = ResourceXResource.objects.get(tile=t.tileid)
        ri_dict = JSONSerializer().serializeToPython(resource_instance)
        expected = {
            "inverserelationshiptype": "http://www.cidoc-crm.org/cidoc-crm/P10i_contains",
            "node_id": UUID("eb115780-e222-11e8-aaed-a4d18cec433a"),
            "notes": "",
            "relationshiptype": "http://www.cidoc-crm.org/cidoc-crm/P62_depicts",
            "from_resource_graph_id": UUID("c35fe0a1-df30-11e8-b280-a4d18cec433a"),
            "to_resource_id": UUID("85b2db6a-d13f-4cc7-aec7-e4caf91b45f7"),
            "to_resource_graph_id": UUID("c35fe0a1-df30-11e8-b280-a4d18cec433a"),
            "tile_id": UUID("edbdef07-77fd-4bb6-9fef-641d4a65abce"),
        }
        self.assertTrue(all(item in ri_dict.items() for item in expected.items()))

        # def test_validation(self):
        #     """
        #     Test that we can get a Tile object

        #     """

        #     json = {
        #         "tiles": {},
        #         "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
        #         "parenttile_id": '',
        #         "nodegroup_id": "20000000-0000-0000-0000-000000000001",
        #         "tileid": "",
        #         "data": {
        #           "20000000-0000-0000-0000-000000000004": "TEST 1"
        #         }
        #     }

        #     t = Tile(json)
        #     self.assertTrue(t.validate()['is_valid'])

        #     json['data']['20000000-0000-0000-0000-000000000004'] = ''

        #     t2 = Tile(json)
        #     self.assertFalse(t2.validate()['is_valid'])

    def test_check_for_missing_nodes(self):
        # Required file list node.
        graph = Graph.objects.create_graph(name="Test Graph")
        node_group = NodeGroup.objects.get(
            pk=UUID("41111111-0000-0000-0000-000000000000")
        )
        required_file_list_node = Node(
            pk=node_group.pk,
            graph=graph,
            name="Required file list",
            datatype="file-list",
            nodegroup=node_group,
            isrequired=True,
            istopnode=False,
        )
        required_file_list_node.save()
        node_group.grouping_node = required_file_list_node
        node_group.save()

        json = {
            "resourceinstance_id": CardinalityTestGraph.RESOURCE1.value,
            "parenttile_id": "",
            "nodegroup_id": str(node_group.pk),
            "tileid": "",
            "data": {required_file_list_node.nodeid: []},
        }
        tile = Tile(json)

        with self.assertRaisesMessage(
            TileValidationError, "Required file list"
        ):  # node name
            tile.check_for_missing_nodes()

        # Add a widget label, should appear in error msg in lieu of node name
        card = CardModel.objects.create(
            nodegroup=node_group,
            graph_id=CardinalityTestGraph.GRAPH_ID.value,
        )
        CardXNodeXWidget.objects.create(
            card=card,
            node_id=required_file_list_node.nodeid,
            widget=Widget.objects.first(),
            label="Widget name",
        )

        with self.assertRaisesMessage(TileValidationError, "Widget name"):
            tile.check_for_missing_nodes()

    def test_save_blank_tile(self):
        data_collecting_grouping_node_id = "72048cb3-adbc-11e6-9ccf-14109fd34195"
        tile = Tile(
            resourceinstance_id=UUID("40000000-0000-0000-0000-000000000000"),
            nodegroup_id=UUID(data_collecting_grouping_node_id),
        )
        tile.save()

        self.assertEqual(tile.data, {data_collecting_grouping_node_id: None})
