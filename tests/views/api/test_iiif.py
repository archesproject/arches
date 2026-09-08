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

import json
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from guardian.shortcuts import assign_perm

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.models.models import ResourceInstance
from arches.app.views.api.iiif import MAX_CANVASES_PER_BATCH

from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.views.api.test_iiif --settings="tests.test_settings"

FIRST_CANVAS = "https://iiif.test/iiif/2/first"
SECOND_CANVAS = "https://iiif.test/iiif/2/second"
UNANNOTATED_CANVAS = "https://iiif.test/iiif/2/unannotated"


class IIIFAnnotationsBatchTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_users()
        cls.user = User.objects.get(username="ben")

        cls.graph = Graph.objects.create_graph(
            name="IIIF_ANNOTATIONS_BATCH_TEST_GRAPH",
            is_resource=False,  # creates a nodegroup, undone below.
        )
        cls.graph.isresource = True
        cls.graph.resource_instance_lifecycle_id = (
            settings.DEFAULT_RESOURCE_INSTANCE_LIFECYCLE_ID
        )
        cls.graph.save(validate=False)
        cls.resource = ResourceInstance.objects.create(graph=cls.graph)

        cls.readable_node = cls.create_annotation_node("readable annotation")
        cls.unreadable_node = cls.create_annotation_node("unreadable annotation")
        assign_perm("no_access_to_nodegroup", cls.user, cls.unreadable_node.nodegroup)

        # Two annotations on the first canvas, one on the second, so that the
        # response has to group several annotations under the same canvas.
        cls.create_annotation_tile(
            cls.readable_node, [FIRST_CANVAS, FIRST_CANVAS, SECOND_CANVAS]
        )
        cls.create_annotation_tile(cls.unreadable_node, [FIRST_CANVAS])

    @classmethod
    def create_annotation_node(cls, name):
        nodeid = uuid.uuid4()
        nodegroup = models.NodeGroup.objects.create(pk=nodeid)
        node = models.Node.objects.create(
            pk=nodeid,
            graph=cls.graph,
            name=name,
            datatype="annotation",
            nodegroup=nodegroup,
            istopnode=False,
        )
        nodegroup.grouping_node = node
        nodegroup.save()
        return node

    @classmethod
    def create_annotation_tile(cls, node, canvases):
        return models.TileModel.objects.create(
            resourceinstance=cls.resource,
            nodegroup=node.nodegroup,
            data={
                str(node.pk): {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "id": str(uuid.uuid4()),
                            "type": "Feature",
                            "geometry": {"type": "Point", "coordinates": [0, 0]},
                            "properties": {"canvas": canvas},
                        }
                        for canvas in canvases
                    ],
                }
            },
        )

    def post_batch(self, body):
        return self.client.post(
            reverse("iiifannotations_batch"),
            data=body,
            content_type="application/json",
        )

    def test_body_is_not_valid_json(self):
        self.client.force_login(self.user)
        response = self.post_batch("this is not json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content)["error"], "Request body is not valid JSON"
        )

    def test_body_is_not_an_object(self):
        self.client.force_login(self.user)
        response = self.post_batch(json.dumps([FIRST_CANVAS]))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content)["error"], "Request body must be a JSON object"
        )

    def test_canvases_is_missing(self):
        self.client.force_login(self.user)
        response = self.post_batch(json.dumps({}))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content)["error"], "canvases must be an array"
        )

    def test_canvases_is_not_an_array(self):
        self.client.force_login(self.user)
        response = self.post_batch(json.dumps({"canvases": FIRST_CANVAS}))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content)["error"], "canvases must be an array"
        )

    def test_canvases_is_empty(self):
        self.client.force_login(self.user)
        response = self.post_batch(json.dumps({"canvases": []}))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content)["error"],
            "canvases must hold at least one canvas id",
        )

    def test_canvases_holds_no_usable_canvas_id(self):
        self.client.force_login(self.user)
        response = self.post_batch(json.dumps({"canvases": ["   ", "", 42, None]}))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content)["error"],
            "canvases must hold at least one canvas id",
        )

    def test_canvases_holds_too_many_canvas_ids(self):
        self.client.force_login(self.user)
        canvases = [
            "%s/%s" % (FIRST_CANVAS, index)
            for index in range(MAX_CANVASES_PER_BATCH + 1)
        ]
        response = self.post_batch(json.dumps({"canvases": canvases}))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content)["error"],
            "canvases must hold at most %s canvas ids" % MAX_CANVASES_PER_BATCH,
        )

    def test_canvas_without_annotations_is_absent_from_the_response(self):
        self.client.force_login(self.user)
        response = self.post_batch(json.dumps({"canvases": [UNANNOTATED_CANVAS]}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {
                "type": "AnnotationsByCanvas",
                "canvases": {},
                "total_annotations": 0,
                "total_canvases": 0,
            },
        )

    def test_annotations_are_grouped_by_canvas(self):
        self.client.force_login(self.user)
        response = self.post_batch(
            json.dumps({"canvases": [FIRST_CANVAS, SECOND_CANVAS, UNANNOTATED_CANVAS]})
        )

        self.assertEqual(response.status_code, 200)
        batch = json.loads(response.content)
        self.assertEqual(batch["type"], "AnnotationsByCanvas")
        self.assertEqual(sorted(batch["canvases"]), [FIRST_CANVAS, SECOND_CANVAS])
        self.assertEqual(len(batch["canvases"][FIRST_CANVAS]["features"]), 2)
        self.assertEqual(len(batch["canvases"][SECOND_CANVAS]["features"]), 1)
        self.assertEqual(batch["canvases"][FIRST_CANVAS]["type"], "FeatureCollection")
        self.assertEqual(batch["total_annotations"], 3)
        self.assertEqual(batch["total_canvases"], 2)

    def test_canvas_ids_are_stripped(self):
        self.client.force_login(self.user)
        response = self.post_batch(json.dumps({"canvases": ["  %s  " % SECOND_CANVAS]}))

        self.assertEqual(response.status_code, 200)
        batch = json.loads(response.content)
        self.assertEqual(list(batch["canvases"]), [SECOND_CANVAS])

    def test_annotations_of_an_unreadable_nodegroup_are_excluded(self):
        self.client.force_login(self.user)
        response = self.post_batch(json.dumps({"canvases": [FIRST_CANVAS]}))

        self.assertEqual(response.status_code, 200)
        batch = json.loads(response.content)
        node_ids = {
            feature["properties"]["nodeId"]
            for feature in batch["canvases"][FIRST_CANVAS]["features"]
        }
        self.assertEqual(node_ids, {str(self.readable_node.pk)})
        self.assertEqual(batch["total_annotations"], 2)

    def test_features_match_the_single_canvas_endpoint(self):
        self.client.force_login(self.user)
        batch = json.loads(
            self.post_batch(json.dumps({"canvases": [SECOND_CANVAS]})).content
        )
        single = json.loads(
            self.client.get(
                reverse("iiifannotations"),
                QUERY_STRING="canvas=%s&nodeid=%s"
                % (SECOND_CANVAS, self.readable_node.pk),
            ).content
        )

        self.assertEqual(batch["canvases"][SECOND_CANVAS], single)

    def test_get_is_not_allowed(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("iiifannotations_batch"))

        self.assertEqual(response.status_code, 405)
