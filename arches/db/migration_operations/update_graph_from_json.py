import copy
import json

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.models.system_settings import settings

from .base import ArchesDataMigration


class UpdateGraphFromJSON(ArchesDataMigration):
    reduces_to_sql = False
    reversible = True

    def __init__(self, json_path):
        self.json_path = json_path

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        with open(self.json_path, "r") as f:
            data = json.load(f)

        graph_data = data["graph"][0]
        previous_graph = Graph.objects.get(pk=graph_data["graphid"])

        system_default_language_localized_graph_data = self.localize_json(
            copy.deepcopy(graph_data), settings.LANGUAGE_CODE
        )

        publication = models.GraphXPublishedGraph.objects.create(
            graph=previous_graph,
            notes=system_default_language_localized_graph_data["publication"]["notes"],
            published_time=system_default_language_localized_graph_data["publication"][
                "published_time"
            ],
            publicationid=system_default_language_localized_graph_data["publication"][
                "publicationid"
            ],
        )
        publication.save()

        for language_tuple in settings.LANGUAGES:
            published_graph = models.PublishedGraph.objects.create(
                publication=publication,
                serialized_graph=self.localize_json(
                    copy.deepcopy(graph_data), language_tuple[0]
                ),
                language=models.Language.objects.get(code=language_tuple[0]),
            )
            published_graph.save()

        previous_graph.restore_state_from_serialized_graph(
            system_default_language_localized_graph_data
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        with open(self.json_path, "r") as f:
            data = json.load(f)

        graph_data = data["graph"][0]
        current_publication_id = graph_data["publication"]["publicationid"]
        current_graph = Graph.objects.get(pk=graph_data["graphid"])

        previous_publication = (
            models.GraphXPublishedGraph.objects.filter(graph=current_graph)
            .exclude(publicationid=current_publication_id)
            .order_by("-published_time")
            .first()
        )

        published_graph = models.PublishedGraph.objects.get(
            publication=previous_publication,
            language=settings.LANGUAGE_CODE,
        )

        previous_graph = Graph.objects.get(
            pk=published_graph.serialized_graph["graphid"]
        )
        previous_graph.restore_state_from_serialized_graph(
            published_graph.serialized_graph
        )

        models.GraphXPublishedGraph.objects.get(
            publicationid=current_publication_id
        ).delete()

    def describe(self):
        return "Updates a graph from exported JSON"
