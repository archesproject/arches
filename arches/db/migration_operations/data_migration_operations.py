import json
import copy

from django.db.migrations.operations.base import Operation
from django.db.models import JSONField
from django.db.models.expressions import RawSQL
from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.models.system_settings import settings


class ArchesDataMigration(Operation):
    # If this is False, it means that this operation will be ignored by
    # sqlmigrate; if true, it will be run and the SQL collected for its output.
    reduces_to_sql = False

    # If this is False, Django will refuse to reverse past this operation.
    reversible = True

    @staticmethod
    def localize_json(input, language_code):
        if isinstance(input, dict):
            if language_code in input:
                input = input[language_code]
            else:
                for key, value in input.items():
                    input[key] = ArchesDataMigration.localize_json(value, language_code)
        elif isinstance(input, list):
            for item in input:
                ArchesDataMigration.localize_json(item, language_code)
        return input

    def __init__(self, arg1, arg2):
        # Operations are usually instantiated with arguments in migration
        # files. Store the values of them on self for later use.
        pass

    def state_forwards(self, app_label, state):
        # The Operation should take the 'state' parameter (an instance of
        # django.db.migrations.state.ProjectState) and mutate it to match
        # any schema changes that have occurred.
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # The Operation should use schema_editor to apply any changes it
        # wants to make to the database.
        pass

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        # If reversible is True, this is called when the operation is reversed.
        pass

    def describe(self):
        # This is used to describe what the operation does in console output.
        return "Custom Operation"

    @property
    def migration_name_fragment(self):
        # Optional. A filename part suitable for automatically naming a
        # migration containing this operation, or None if not applicable.
        return "custom_operation_%s_%s" % (self.arg1, self.arg2)


class CreateGraph(ArchesDataMigration):
    # If this is False, it means that this operation will be ignored by
    # sqlmigrate; if true, it will be run and the SQL collected for its output.
    reduces_to_sql = False

    # If this is False, Django will refuse to reverse past this operation.
    reversible = True

    def __init__(
        self,
        graphid,
        graph_slug,
        name="",
        is_resource=False,
    ):
        self.graphid = graphid
        self.graph_slug = graph_slug
        self.name = name
        self.is_resource = is_resource

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        Graph.objects.create_graph(
            graphid=self.graphid,
            slug=self.graph_slug,
            name=self.name,
            is_resource=self.is_resource,
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        Graph.objects.filter(graphid=self.graphid).delete()

    def describe(self):
        # This is used to describe what the operation does in console output.
        return "Creates a graph with id %s" % self.graphid


class UpdateResourceInstancesPublicationId(ArchesDataMigration):
    # If this is False, it means that this operation will be ignored by
    # sqlmigrate; if true, it will be run and the SQL collected for its output.
    reduces_to_sql = False

    # If this is False, Django will refuse to reverse past this operation.
    reversible = True

    def __init__(self, current_publication_id, updated_publication_id):
        self.current_publication_id = current_publication_id
        self.updated_publication_id = updated_publication_id

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(
            "UPDATE resource_instances SET graphpublicationid = '%s' WHERE graphpublicationid = '%s'"
            % (self.updated_publication_id, self.current_publication_id)
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(
            "UPDATE resource_instances SET graphpublicationid = '%s' WHERE graphpublicationid = '%s'"
            % (self.current_publication_id, self.updated_publication_id)
        )

    def describe(self):
        # This is used to describe what the operation does in console output.
        return "Updates resources' publication_id from %s to %s" % (
            self.current_publication_id,
            self.updated_publication_id,
        )


class AddNodeToTileData(ArchesDataMigration):
    # If this is False, it means that this operation will be ignored by
    # sqlmigrate; if true, it will be run and the SQL collected for its output.
    reduces_to_sql = False

    # If this is False, Django will refuse to reverse past this operation.
    reversible = True

    def __init__(self, publication_id, nodegroup_id, node_id, value):
        self.publication_id = publication_id
        self.nodegroup_id = nodegroup_id
        self.node_id = node_id
        self.value = value

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        models.TileModel.objects.filter(
            nodegroup_id=self.nodegroup_id,
            resourceinstance__graph_publication_id=self.publication_id,
        ).exclude(
            data__has_key=self.node_id,
        ).update(
            data=RawSQL(
                "jsonb_set(tiledata, ARRAY[%s], %s::jsonb)",
                [self.node_id, json.dumps(self.value)],
                output_field=JSONField(),
            )
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        models.TileModel.objects.filter(
            nodegroup_id=self.nodegroup_id,
            resourceinstance__graph_publication_id=self.publication_id,
            data__has_key=self.node_id,
        ).update(
            data=RawSQL(
                "tiledata - %s",
                [self.node_id],
                output_field=JSONField(),
            )
        )

    def describe(self):
        # This is used to describe what the operation does in console output.
        return "Updates resources' publication_id from"


class DeleteNodeFromTileData(ArchesDataMigration):
    # If this is False, it means that this operation will be ignored by
    # sqlmigrate; if true, it will be run and the SQL collected for its output.
    reduces_to_sql = False

    # If this is False, Django will refuse to reverse past this operation.
    reversible = True

    def __init__(self, publication_id, nodegroup_id, node_id, value):
        self.publication_id = publication_id
        self.nodegroup_id = nodegroup_id
        self.node_id = node_id
        self.value = value

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        models.TileModel.objects.filter(
            nodegroup_id=self.nodegroup_id,
            resourceinstance__graph_publication_id=self.publication_id,
        ).filter(
            data__has_key=self.node_id,
        ).update(
            data=RawSQL(
                "tiledata - %s",
                [self.node_id],
                output_field=JSONField(),
            )
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        models.TileModel.objects.filter(
            nodegroup_id=self.nodegroup_id,
            resourceinstance__graph_publication_id=self.publication_id,
        ).exclude(
            data__has_key=self.node_id,
        ).update(
            data=RawSQL(
                "jsonb_set(tiledata, ARRAY[%s], %s::jsonb)",
                [self.node_id, json.dumps(self.value)],
                output_field=JSONField(),
            )
        )

    def describe(self):
        # This is used to describe what the operation does in console output.
        return "Deletes node %s from tile data for nodegroup %s" % (
            self.node_id,
            self.nodegroup_id,
        )


class UpdateGraphFromJSON(ArchesDataMigration):
    # If this is False, it means that this operation will be ignored by
    # sqlmigrate; if true, it will be run and the SQL collected for its output.
    reduces_to_sql = False

    # If this is False, Django will refuse to reverse past this operation.
    reversible = True

    def __init__(self, json_path):
        self.json_path = json_path

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        with open(self.json_path, "r") as f:
            data = json.load(f)

        graph_data = data["graph"][0]
        previous_graph = Graph.objects.get(pk=graph_data["graphid"])

        # first, update the json structure to the system default language
        # and create a GraphXPublishedGraph entry
        system_default_language_localized_graph_data = self.localize_json(
            copy.deepcopy(graph_data), settings.LANGUAGE_CODE
        )

        # using previous_graph here because all we need is a graph_id for the foriegn key
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

        previous_graph.restore_state_from_serialized_graph(
            system_default_language_localized_graph_data
        )

        # then create a PublishedGraph entry for all languages in the json structure
        for language_tuple in settings.LANGUAGES:
            published_graph = models.PublishedGraph.objects.create(
                publication=publication,
                serialized_graph=self.localize_json(
                    copy.deepcopy(graph_data), language_tuple[0]
                ),
                language=models.Language.objects.get(code=language_tuple[0]),
            )
            published_graph.save()

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
        # This is used to describe what the operation does in console output.
        return "Updates a graph from exported JSON"
