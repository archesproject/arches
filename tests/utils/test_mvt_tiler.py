import json
import time
import uuid

from django.urls import reverse
from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.mvt_tiler import MVTTiler
from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.db import connection
from django.test import Client, TestCase

from arches.app.utils.permission_backend import assign_perm
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.utils.test_mvt_tiler --settings="tests.test_settings"


class MvtTilerTests(ArchesTestCase):
    graph_fixtures = ["Resource Test Model"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.client = Client()
        cls.client.login(username="admin", password="admin")

        cls.search_model_graphid = uuid.UUID("c9b37a14-17b3-11eb-a708-acde48001122")
        cls.search_model_cultural_period_nodeid = "c9b3882e-17b3-11eb-a708-acde48001122"
        cls.search_model_creation_date_nodeid = "c9b38568-17b3-11eb-a708-acde48001122"
        cls.search_model_destruction_date_nodeid = (
            "c9b3828e-17b3-11eb-a708-acde48001122"
        )
        cls.search_model_name_nodeid = "c9b37b7c-17b3-11eb-a708-acde48001122"
        cls.search_model_sensitive_info_nodeid = "c9b38aea-17b3-11eb-a708-acde48001122"
        cls.search_model_geom_nodeid = "c9b37f96-17b3-11eb-a708-acde48001122"

        cls.user = User.objects.create_user(
            "test", "test@archesproject.org", "password"
        )
        cls.user.groups.add(Group.objects.get(name="Guest"))

        graph = Graph.objects.get(pk=cls.search_model_graphid)
        graph.publish(user=cls.user)

        nodegroup = models.NodeGroup.objects.get(
            pk=cls.search_model_destruction_date_nodeid
        )
        assign_perm("no_access_to_nodegroup", cls.user, nodegroup)

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
                            "value": "Mock concept",
                            "language": "en",
                            "category": "label",
                            "type": "prefLabel",
                            "id": "",
                            "conceptid": "",
                        },
                        {
                            "value": "1950",
                            "language": "en",
                            "category": "note",
                            "type": "min_year",
                            "id": "",
                            "conceptid": "",
                        },
                        {
                            "value": "1980",
                            "language": "en",
                            "category": "note",
                            "type": "max_year",
                            "id": "",
                            "conceptid": "",
                        },
                    ],
                    "relationshiptype": "hasTopConcept",
                    "nodetype": "Concept",
                    "id": "",
                    "legacyoid": "",
                    "subconcepts": [],
                    "parentconcepts": [],
                    "relatedconcepts": [],
                }
            ],
        }

        post_data = JSONSerializer().serialize(concept)
        content_type = "application/x-www-form-urlencoded"
        response = cls.client.post(
            reverse(
                "concept", kwargs={"conceptid": "00000000-0000-0000-0000-000000000001"}
            ),
            post_data,
            content_type,
        )
        response_json = json.loads(response.content)
        valueid = response_json["subconcepts"][0]["values"][0]["id"]
        cls.conceptid = response_json["subconcepts"][0]["id"]

        # Add resource with Name, Cultural Period, Creation Date and Geometry
        cls.test_resource = Resource(graph_id=cls.search_model_graphid)

        # Add Name
        tile = Tile(
            data={
                cls.search_model_name_nodeid: {
                    "en": {"value": "Test Name 1"},
                    "es": {"value": "Prueba Nombre 1"},
                }
            },
            nodegroup_id=cls.search_model_name_nodeid,
        )
        cls.test_resource.tiles.append(tile)

        # Add Cultural Period
        tile = Tile(
            data={cls.search_model_cultural_period_nodeid: [valueid]},
            nodegroup_id=cls.search_model_cultural_period_nodeid,
        )
        cls.test_resource.tiles.append(tile)

        # Add Creation Date
        tile = Tile(
            data={cls.search_model_creation_date_nodeid: "1941-01-01"},
            nodegroup_id=cls.search_model_creation_date_nodeid,
        )
        cls.test_resource.tiles.append(tile)

        # Add Geometry
        cls.geom = {
            "type": "FeatureCollection",
            "features": [
                {
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "type": "Feature",
                    "properties": {},
                }
            ],
        }
        tile = Tile(
            data={cls.search_model_geom_nodeid: cls.geom},
            nodegroup_id=cls.search_model_geom_nodeid,
        )
        cls.test_resource.tiles.append(tile)

        cls.test_resource.save()

        # add delay to allow for indexes to be updated
        time.sleep(1)

    def test_create_tile(self):
        user = self.user
        viewable_nodegroup = user.userprofile.viewable_nodegroups

        tile = MVTTiler().createTile(
            "c9b37f96-17b3-11eb-a708-acde48001122", viewable_nodegroup, user, 10, 90, 40
        )

        self.assertEqual(len(tile), 0)

    def test_clustered_tile_feature_ids_are_unique(self):
        def point(lon, lat):
            return {
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "type": "Feature",
                "properties": {},
            }

        # four nearby points cluster; two far-apart points stay unclustered
        points = [(10, 10), (10.001, 10), (10, 10.001), (10.001, 10.001)]
        points += [(50, 40), (80, 60)]
        resource = Resource(graph_id=self.search_model_graphid)
        resource.tiles.append(
            Tile(
                data={
                    self.search_model_geom_nodeid: {
                        "type": "FeatureCollection",
                        "features": [point(*p) for p in points],
                    }
                },
                nodegroup_id=self.search_model_geom_nodeid,
            )
        )
        resource.save()
        with connection.cursor() as cursor:
            cursor.execute("SELECT refresh_geojson_geometries();")

        node = models.Node.objects.get(pk=self.search_model_geom_nodeid)
        node.config = {
            **node.config,
            "clusterMaxZoom": 5,
            "clusterDistance": 1,
            "clusterMinPoints": 3,
        }
        node.save()
        cache.clear()

        admin = User.objects.get(username="admin")
        tile = MVTTiler().createTile(
            self.search_model_geom_nodeid,
            admin.userprofile.viewable_nodegroups,
            admin,
            2,
            2,
            1,
        )
        ids = self.mvt_feature_ids(tile)

        real_ids = set(
            models.GeoJSONGeometry.objects.filter(
                node_id=self.search_model_geom_nodeid
            ).values_list("id", flat=True)
        )
        cluster_ids = [i for i in ids if i >= 2**31]
        point_ids = [i for i in ids if i < 2**31]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(cluster_ids), 1)
        # setUpTestData's point at (0, 0) may sit on this tile's corner
        self.assertGreaterEqual(len(point_ids), 2)
        self.assertTrue(set(point_ids) <= real_ids)

    @staticmethod
    def mvt_feature_ids(tile):
        """Minimal protobuf walk: Tile.layers(3) -> Layer.features(2) -> Feature.id(1)."""

        def varint(buf, pos):
            result = shift = 0
            while True:
                byte = buf[pos]
                pos += 1
                result |= (byte & 0x7F) << shift
                if not byte & 0x80:
                    return result, pos
                shift += 7

        def fields(buf):
            pos = 0
            while pos < len(buf):
                key, pos = varint(buf, pos)
                field, wire = key >> 3, key & 7
                if wire == 0:
                    value, pos = varint(buf, pos)
                elif wire == 2:
                    length, pos = varint(buf, pos)
                    value, pos = buf[pos : pos + length], pos + length
                elif wire == 1:
                    value, pos = buf[pos : pos + 8], pos + 8
                else:
                    value, pos = buf[pos : pos + 4], pos + 4
                yield field, value

        ids = []
        for field, layer in fields(tile):
            if field != 3:
                continue
            for lfield, feature in fields(layer):
                if lfield == 2:
                    ids += [v for f, v in fields(feature) if f == 1]
        return ids
