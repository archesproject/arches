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
from tests.base_test import ArchesTestCase
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.formats.rdffile import JsonLdReader
from arches.app.models.graph import Graph

# these tests can be run from the command line via
# python manage.py test tests/utils/rdffile_tests.py --pattern="*.py" --settings="tests.test_settings"


class APITests(ArchesTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
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

    def test_find_unique_branch_from_jsonld(self):
        """
        Test that we can find the correct branch in the graph that matches the supplied json-ld
        The graph is partially unique (the children of the root are not unique)

        """

        jsonld_graph = {
            "@id": "http://localhost:8000/resource/9f2f0a94-95ea-11e8-8317-14109fd34195",
            "@type": [
                "http://localhost:8000/graph/1065d6de-95e6-11e8-9ddd-14109fd34195",
                "http://www.cidoc-crm.org/cidoc-crm/E82_Actor_Appellation",
            ],
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": {
                "@id": "http://localhost:8000/tile/6cb9c535-30fc-40f6-af83-ce14b45d671b/node/3e1e65dc-95e6-11e8-9de9-14109fd34195",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E41_Appellation",
                "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": {
                    "@id": "http://localhost:8000/tile/6cb9c535-30fc-40f6-af83-ce14b45d671b/node/839b0e4c-95e6-11e8-aada-14109fd34195",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E82_Actor_Appellation",
                    "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "Will",
                },
                "http://www.cidoc-crm.org/cidoc-crm/P1i_identifies": {
                    "@id": "http://localhost:8000/tile/6cb9c535-30fc-40f6-af83-ce14b45d671b/node/e5823357-95e6-11e8-8ab0-14109fd34195",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E41_Appellation",
                    "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "Smith",
                },
            },
        }
        graphtree = self.unique_graph.get_tree()
        reader = JsonLdReader()
        branch = reader.findBranch(
            graphtree["children"],
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            jsonld_graph["http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by"],
        )
        self.assertEqual(str(branch["node"].pk), "3e1e65dc-95e6-11e8-9de9-14109fd34195")

    def test_find_other_unique_branch_from_jsonld(self):
        """
        Test that we can find the correct branch in the graph that matches the supplied json-ld
        The graph is partially unique (the children of the root are not unique)

        """

        jsonld_graph = {
            "@id": "http://localhost:8000/resource/9f2f0a94-95ea-11e8-8317-14109fd34195",
            "@type": [
                "http://www.cidoc-crm.org/cidoc-crm/E82_Actor_Appellation",
                "http://localhost:8000/graph/1065d6de-95e6-11e8-9ddd-14109fd34195",
            ],
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": [
                {
                    "@id": "http://localhost:8000/tile/a8db6210-4fda-4711-beeb-cc0da639535d/node/91679e1e-95e6-11e8-a166-14109fd34195",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E41_Appellation",
                    "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": {
                        "@id": "http://localhost:8000/tile/a8db6210-4fda-4711-beeb-cc0da639535d/node/2cf3598a-95e7-11e8-88da-14109fd34195",
                        "@type": "http://www.ics.forth.gr/isl/CRMdig/D21_Person_Name",
                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "The Shadow",
                    },
                }
            ],
        }

        graphtree = self.unique_graph.get_tree()
        reader = JsonLdReader()
        branch = reader.findBranch(
            graphtree["children"],
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            jsonld_graph["http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by"],
        )
        self.assertEqual(str(branch["node"].pk), "91679e1e-95e6-11e8-a166-14109fd34195")

    def test_cant_find_branch_from_jsonld(self):
        """
        Test that we raise the appropriate error when we can't find the correct branch in the graph that matches the supplied json-ld
        The graph is partially unique (the children of the root are not unique)

        """

        incorrect_jsonld_graph = {
            "@id": "http://localhost:8000/resource/9f2f0a94-95ea-11e8-8317-14109fd34195",
            "@type": [
                "http://www.cidoc-crm.org/cidoc-crm/E82_Actor_Appellation",
                "http://localhost:8000/graph/1065d6de-95e6-11e8-9ddd-14109fd34195",
            ],
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": [
                {
                    "@id": "http://localhost:8000/tile/a8db6210-4fda-4711-beeb-cc0da639535d/node/91679e1e-95e6-11e8-a166-14109fd34195",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E41_Appellation",
                    "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": {
                        "@id": "http://localhost:8000/tile/a8db6210-4fda-4711-beeb-cc0da639535d/node/2cf3598a-95e7-11e8-88da-14109fd34195",
                        "@type": "---THIS TYPE IS INCORRECT AND SHOULN'T MATCH---",
                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "The Shadow",
                    },
                }
            ],
        }

        graphtree = self.unique_graph.get_tree()
        reader = JsonLdReader()
        with self.assertRaises(reader.DataDoesNotMatchGraphException) as cm:
            branch = reader.findBranch(
                graphtree["children"],
                "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
                incorrect_jsonld_graph["http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by"],
            )

    def test_cant_find_branch_from_ambiguous_jsonld(self):
        """
        Test that we raise the appropriate error when we can't find the correct branch in the graph given that the supplied
        json-ld could match more than one branch
        The graph is partially unique (the children of the root are not unique)

        """

        ambiguous_jsonld_graph = {
            "@id": "http://localhost:8000/resource/9f2f0a94-95ea-11e8-8317-14109fd34195",
            "@type": [
                "http://www.cidoc-crm.org/cidoc-crm/E82_Actor_Appellation",
                "http://localhost:8000/graph/1065d6de-95e6-11e8-9ddd-14109fd34195",
            ],
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": [
                {
                    "@id": "http://localhost:8000/tile/a8db6210-4fda-4711-beeb-cc0da639535d/node/91679e1e-95e6-11e8-a166-14109fd34195",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E41_Appellation",
                    "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": {
                        "@id": "http://localhost:8000/tile/a8db6210-4fda-4711-beeb-cc0da639535d/node/3f40dad1-9693-11e8-8a3b-14109fd34195",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E82_Actor_Appellation",
                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "Will - Ambiguous",
                    },
                }
            ],
        }

        graphtree = self.ambiguous_graph.get_tree()
        reader = JsonLdReader()
        with self.assertRaises(reader.AmbiguousGraphException) as cm:
            branch = reader.findBranch(
                graphtree["children"],
                "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
                ambiguous_jsonld_graph["http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by"],
            )

    def test_find_branch_from_jsonld_2(self):
        """
        The same test as above except that we now add an additional node to the supplied json which now will match a branch in the graph
        The graph is partially unique (the children of the root are not unique)

        """

        ambiguous_jsonld_graph = {
            "@id": "http://localhost:8000/resource/9f2f0a94-95ea-11e8-8317-14109fd34195",
            "@type": [
                "http://www.cidoc-crm.org/cidoc-crm/E82_Actor_Appellation",
                "http://localhost:8000/graph/1065d6de-95e6-11e8-9ddd-14109fd34195",
            ],
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": [
                {
                    "@id": "http://localhost:8000/tile/a8db6210-4fda-4711-beeb-cc0da639535d/node/91679e1e-95e6-11e8-a166-14109fd34195",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E41_Appellation",
                    "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": {
                        "@id": "http://localhost:8000/tile/a8db6210-4fda-4711-beeb-cc0da639535d/node/3f40dad1-9693-11e8-8a3b-14109fd34195",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E82_Actor_Appellation",
                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "Will",
                    },
                    "http://www.cidoc-crm.org/cidoc-crm/P1i_identifies": {
                        "@id": "http://localhost:8000/tile/6cb9c535-30fc-40f6-af83-ce14b45d671b/node/e5823357-95e6-11e8-8ab0-14109fd34195",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E41_Appellation",
                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "Smith",
                    },
                }
            ],
        }

        graphtree = self.ambiguous_graph.get_tree()
        reader = JsonLdReader()
        branch = reader.findBranch(
            graphtree["children"],
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            ambiguous_jsonld_graph["http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by"],
        )
        self.assertEqual(str(branch["node"].pk), "3f40c4c0-9693-11e8-8a0f-14109fd34195")

    def test_find_branch_from_complex_jsonld(self):
        """
        Given a more complicated json structure find the branch in the graph

        """

        complex_jsonld_graph = {
            "@id": "http://localhost:8000/resource/29fe34e8-9746-11e8-b5a2-14109fd34195",
            "@type": [
                "http://www.cidoc-crm.org/cidoc-crm/E12_Production",
                "http://localhost:8000/graph/049fc0c8-fa36-11e6-9e3e-026d961c88e6",
            ],
            "http://www.cidoc-crm.org/cidoc-crm/P41i_was_classified_by": [
                {
                    "@id": "http://localhost:8000/tile/267e874e-0242-45bf-b8b3-ce5a463119df/node/049fc0c9-fa36-11e6-9e3e-026d961c88e6",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E17_Type_Assignment",
                    "http://www.cidoc-crm.org/cidoc-crm/P42_assigned": {
                        "@id": "http://localhost:8000/tile/267e874e-0242-45bf-b8b3-ce5a463119df/node/049fc0d9-fa36-11e6-9e3e-026d961c88e6",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "None",
                    },
                    "http://www.cidoc-crm.org/cidoc-crm/P2_has_type": {
                        "@id": "http://localhost:8000/tile/267e874e-0242-45bf-b8b3-ce5a463119df/node/049fc0df-fa36-11e6-9e3e-026d961c88e6",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "51cbfba6-34ee-4fbd-8b6e-10ef73fd4083",
                    },
                    "http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span": {
                        "@id": "http://localhost:8000/tile/267e874e-0242-45bf-b8b3-ce5a463119df/node/049fc0db-fa36-11e6-9e3e-026d961c88e6",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E52_Time-Span",
                        "http://www.cidoc-crm.org/cidoc-crm/P78_is_identified_by": [
                            {
                                "@id": "http://localhost:8000/tile/267e874e-0242-45bf-b8b3-ce5a463119df/node/049fc0de-fa36-11e6-9e3e-026d961c88e6",
                                "@type": "http://www.cidoc-crm.org/cidoc-crm/E49_Time_Appellation",
                                "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "2018-08-05",
                            },
                            {
                                "@id": "http://localhost:8000/tile/267e874e-0242-45bf-b8b3-ce5a463119df/node/049fc0e1-fa36-11e6-9e3e-026d961c88e6",
                                "@type": "http://www.cidoc-crm.org/cidoc-crm/E49_Time_Appellation",
                                "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "2018-08-06",
                            },
                        ],
                    },
                }
            ],
        }

        graphtree = self.phase_type_assignment_graph.get_tree()
        reader = JsonLdReader()
        branch = reader.findBranch(
            graphtree["children"],
            "http://www.cidoc-crm.org/cidoc-crm/P41i_was_classified_by",
            complex_jsonld_graph["http://www.cidoc-crm.org/cidoc-crm/P41i_was_classified_by"],
        )
        self.assertEqual(str(branch["node"].pk), "049fc0c9-fa36-11e6-9e3e-026d961c88e6")

    def test_cant_find_branch_from_complex_ambigious_jsonld(self):
        """
        The same test as above except that we now supply a jsonld structure that matches more then one branch in the graph (it's ambiguous)

        """

        complex_jsonld_graph = {
            "@id": "http://localhost:8000/resource/29fe34e8-9746-11e8-b5a2-14109fd34195",
            "@type": [
                "http://www.cidoc-crm.org/cidoc-crm/E12_Production",
                "http://localhost:8000/graph/049fc0c8-fa36-11e6-9e3e-026d961c88e6",
            ],
            "http://www.cidoc-crm.org/cidoc-crm/P41i_was_classified_by": [
                {
                    "@id": "http://localhost:8000/tile/91ac5ea1-11d0-457a-b5ba-fc122159178e/node/049fc0cc-fa36-11e6-9e3e-026d961c88e6",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E17_Type_Assignment",
                    "http://www.cidoc-crm.org/cidoc-crm/P42_assigned": [
                        {
                            "@id": "http://localhost:8000/tile/91ac5ea1-11d0-457a-b5ba-fc122159178e/node/049fc0d7-fa36-11e6-9e3e-026d961c88e6",
                            "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                            "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "174e9486-0663-4c9d-ab78-c7e441720c26",
                        },
                        {
                            "@id": "http://localhost:8000/tile/91ac5ea1-11d0-457a-b5ba-fc122159178e/node/049fc0d5-fa36-11e6-9e3e-026d961c88e6",
                            "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                            "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "None",
                        },
                    ],
                    "http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span": {
                        "@id": "http://localhost:8000/tile/91ac5ea1-11d0-457a-b5ba-fc122159178e/node/049fc0e3-fa36-11e6-9e3e-026d961c88e6",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E52_Time-Span",
                        "http://www.cidoc-crm.org/cidoc-crm/P78_is_identified_by": [
                            {
                                "@id": "http://localhost:8000/tile/91ac5ea1-11d0-457a-b5ba-fc122159178e/node/049fc0dc-fa36-11e6-9e3e-026d961c88e6",
                                "@type": "http://www.cidoc-crm.org/cidoc-crm/E49_Time_Appellation",
                                "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "2018-08-06",
                            },
                            {
                                "@id": "http://localhost:8000/tile/91ac5ea1-11d0-457a-b5ba-fc122159178e/node/049fc0d6-fa36-11e6-9e3e-026d961c88e6",
                                "@type": "http://www.cidoc-crm.org/cidoc-crm/E49_Time_Appellation",
                                "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "2018-09-20",
                            },
                        ],
                    },
                }
            ],
        }

        graphtree = self.phase_type_assignment_graph.get_tree()
        reader = JsonLdReader()
        with self.assertRaises(reader.AmbiguousGraphException) as cm:
            branch = reader.findBranch(
                graphtree["children"],
                "http://www.cidoc-crm.org/cidoc-crm/P41i_was_classified_by",
                complex_jsonld_graph["http://www.cidoc-crm.org/cidoc-crm/P41i_was_classified_by"],
            )

    def test_find_leaf_branch(self):
        """
        Given a list of leaf nodes, find the appropriate node from the given jsonld

        """

        jsonld_graph = {
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": {
                "@id": "http://localhost:8000/tile/6cb9c535-30fc-40f6-af83-ce14b45d671b/node/839b0e4c-95e6-11e8-aada-14109fd34195",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E82_Actor_Appellation",
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "Will",
            }
        }

        graphtree = self.unique_graph.get_tree()
        for child in graphtree["children"]:
            if child["node"].name == "Name":
                node = child
        reader = JsonLdReader()
        branch = reader.findBranch(
            node["children"],
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            jsonld_graph["http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by"],
        )
        self.assertEqual(str(branch["node"].pk), "839b0e4c-95e6-11e8-aada-14109fd34195")
