import csv
import os
import sys
import json
import uuid
import csv
import zipfile
from io import StringIO
from io import BytesIO
from django.utils.translation import get_language

from arches.app.models.graph import Graph
from arches.app.models.concept import Concept
from arches.app.models.system_settings import settings
from arches.app.models.models import (
    CardXNodeXWidget,
    Node,
    Resource2ResourceConstraint,
    FunctionXGraph,
    Value,
    GraphXPublishedGraph,
    ResourceInstanceLifecycle,
)
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from collections import OrderedDict
from operator import itemgetter


def export(export_dir):
    """
    Exports existing graphs as Gephi nodes and edges files to a directory
    """
    write_nodes(export_dir)
    write_edges(export_dir)


def write_nodes(export_dir):
    nodes = Node.objects.all()
    entitytypeids = {}
    for node in nodes:
        if node.assettype not in entitytypeids:
            entitytypeids[node.assettype] = []
        entitytypeids[node.assettype].append(
            [node.id, node.label, node.mergenode, node.businesstablename]
        )

    for k, v in entitytypeids.items():
        with open(os.path.join(export_dir, k + "_nodes.csv"), "w") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(["Id", "Label", "mergenode", "businesstablename"])
            writer.writerow([k + ":" + k, k, k, ""])
            for node in v:
                writer.writerow(node)


def write_edges(export_dir):
    edges = Edge.objects.all()
    entitytypeids = {}
    for edge in edges:
        if edge.assettype not in entitytypeids:
            entitytypeids[edge.assettype] = []
        entitytypeids[edge.assettype].append(
            [edge.source, edge.target, "Directed", edge.target, edge.label, 1.0]
        )

    for k, v in entitytypeids.items():
        with open(os.path.join(export_dir, k + "_edges.csv"), "w") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(["Source", "Target", "Type", "Id", "Label", "Weight"])
            for node in v:
                writer.writerow(node)


def r2r_constraints_for_export(resource_graph):
    r2r_constraints = []
    r2r_constraints = Resource2ResourceConstraint.objects.filter(
        resourceclassfrom=resource_graph["graphid"]
    )
    return r2r_constraints


def get_card_x_node_x_widget_data_for_export(resource_graph):
    cards_x_nodes_x_widgets = []
    nodeids = [node["nodeid"] for node in resource_graph["nodes"]]
    cards_x_nodes_x_widgets = CardXNodeXWidget.objects.filter(node_id__in=nodeids)
    return cards_x_nodes_x_widgets


def get_function_x_graph_data_for_export(functionids, graphid):
    return FunctionXGraph.objects.filter(function_id__in=functionids, graph_id=graphid)


def sort(object, dict_key=None):
    """
    This is meant realy just to sort graph data for export
    """

    def handle_dictionary(d):
        """Called to handle a Dictionary"""
        obj = {}
        for key, value in d.items():
            obj[str(key)] = sort(value, key)
        return obj

    def handle_list(l, sort_key=None):
        """Called to handle a list"""
        arr = []
        for item in l:
            arr.append(sort(item))
        if sort_key:
            try:
                arr = sorted(arr, key=lambda k: k[sort_key])
            except:
                pass
        return arr

    if isinstance(object, dict):
        return handle_dictionary(object)
    elif isinstance(object, list):
        if dict_key == "cards":
            return handle_list(object, "cardid")
        elif dict_key == "cards_x_nodes_x_widgets":
            return handle_list(object, "id")
        elif dict_key == "functions_x_graphs":
            return handle_list(object, "id")
        elif dict_key == "nodegroups":
            return handle_list(object, "nodegroupid")
        elif dict_key == "nodes":
            return handle_list(object, "nodeid")
        elif dict_key == "edges":
            return handle_list(object, "edgeid")
        else:
            return handle_list(object)
    else:
        return object


def get_graphs_for_export(graphids=None):
    def get_original_graphs(graphs):
        for i in range(len(graphs)):
            if graphs[i].source_identifier_id is not None:
                graphs[i] = Graph.objects.get(pk=graphs[i].source_identifier_id)
        return graphs

    graphs = {}
    graphs["graph"] = []
    if graphids is None or graphids[0] == "all" or graphids == [""]:
        resource_graphs = (
            Graph.objects.all()
            .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(source_identifier__isnull=True)
        )
    elif graphids[0] == "resource_models":
        resource_graphs = (
            Graph.objects.filter(isresource=True)
            .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(source_identifier__isnull=True)
        )
    elif graphids[0] == "branches":
        resource_graphs = (
            Graph.objects.filter(isresource=False)
            .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(source_identifier__isnull=True)
        )
    else:
        try:
            resource_graphs = get_original_graphs(
                list(Graph.objects.filter(graphid__in=graphids))
            )
        except:
            # this warning should never get thrown while doing an export from the UI, but maybe it should be moved somewhere else.
            print("*" * 80)
            print(
                '"{0}" contains/is not a valid graphid or option for this command.'.format(
                    ",".join(graphids)
                )
            )
            print("*" * 80)
            sys.exit()
    for resource_graph in resource_graphs:
        resource_graph.refresh_from_database()

    resource_graph_query = JSONSerializer().serializeToPython(
        resource_graphs,
        exclude=["widgets"],
        force_recalculation=True,
        use_raw_i18n_json=True,
    )

    for resource_graph in resource_graph_query:
        function_ids = []
        for function in resource_graph["functions"]:
            function_ids.append(function["function_id"])
        resource_graph["functions_x_graphs"] = JSONSerializer().serializeToPython(
            get_function_x_graph_data_for_export(
                function_ids, resource_graph["graphid"]
            )
        )
        del resource_graph["functions"]
        del resource_graph["domain_connections"]
        resource_graph["cards_x_nodes_x_widgets"] = JSONSerializer().serializeToPython(
            get_card_x_node_x_widget_data_for_export(resource_graph),
            use_raw_i18n_json=True,
        )
        resource_graph[
            "resource_2_resource_constraints"
        ] = JSONSerializer().serializeToPython(
            r2r_constraints_for_export(resource_graph)
        )

        # Replace `publication_id` with `publication`
        publication_id = resource_graph.get("publication_id")
        publication = None

        if publication_id:
            publication = JSONDeserializer().deserialize(
                JSONSerializer().serialize(
                    GraphXPublishedGraph.objects.get(pk=publication_id)
                )
            )
            del publication["user_id"]

        resource_graph["publication"] = publication
        del resource_graph["publication_id"]

        # Replace `resource_instance_lifecycle_id` with `resource_instance_lifecycle`
        resource_instance_lifecycle_id = resource_graph.get(
            "resource_instance_lifecycle_id"
        )
        resource_instance_lifecycle = None

        if resource_instance_lifecycle_id:
            resource_instance_lifecycle = JSONDeserializer().deserialize(
                JSONSerializer().serialize(
                    ResourceInstanceLifecycle.objects.get(
                        pk=resource_instance_lifecycle_id
                    )
                )
            )

        resource_graph["resource_instance_lifecycle"] = resource_instance_lifecycle
        del resource_graph["resource_instance_lifecycle_id"]

        graphs["graph"].append(resource_graph)
    return sort(graphs)


def create_mapping_configuration_file(graphid, include_concepts=True, data_dir=None):
    files_for_export = []
    graphid = uuid.UUID(graphid)
    nodes = []
    values = {}
    export_json = OrderedDict()
    language = get_language()
    if graphid != False:
        if graphid is None or graphid == "all" or graphid == [""]:
            node_query = (
                Node.objects.filter(graph_id__isresource=True)
                .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
                .order_by("name")
            )
        else:
            node_query = (
                Node.objects.filter(graph_id=graphid)
                .exclude(datatype="semantic")
                .order_by("name")
            )

        export_json["resource_model_id"] = str(node_query[0].graph_id)
        export_json["resource_model_name"] = JSONSerializer().serializeToPython(
            Graph.objects.filter(graphid=export_json["resource_model_id"])
        )[0]["name"]
        export_json["nodes"] = []
        file_name_prefix = export_json["resource_model_name"]

        for node in node_query:
            export_node = OrderedDict()
            export_node["arches_nodeid"] = str(node.nodeid)
            export_node["arches_node_name"] = node.name
            export_node["file_field_name"] = node.name
            export_node["data_type"] = node.datatype
            if node.datatype in [
                "concept",
                "concept-list",
                "domain-value",
                "domain-value-list",
            ]:
                export_node["concept_export_value"] = "label"
            # export_node['value_type'] = ""
            # export_node['data_length'] = ""
            export_node["export"] = True

            export_json["nodes"].append(export_node)

            if include_concepts == True:
                concept_export = {}

                def get_values(concept, values):
                    for subconcept in concept.subconcepts:
                        for value in subconcept.values:
                            if value.type == "prefLabel":
                                values[value.id] = value.value
                        get_values(subconcept, values)
                    return values

                if node.datatype in [
                    "concept",
                    "concept-list",
                    "domain-value",
                    "domain-value-list",
                ]:
                    if node.datatype in ["concept", "concept-list"]:
                        if node.config["rdmCollection"] is not None:
                            rdmCollection = node.config["rdmCollection"]
                        try:
                            concept = Concept().get(
                                node.config["rdmCollection"],
                                include_subconcepts=True,
                                semantic=False,
                            )
                            rdmCollectionLabel = concept.get_preflabel().value
                            collection_values = {}
                            concepts = OrderedDict(
                                sorted(
                                    list(
                                        get_values(concept, collection_values).items()
                                    ),
                                    key=itemgetter(1),
                                )
                            )
                            values[rdmCollectionLabel] = concepts
                        except:
                            values[node.name] = (
                                node.name
                                + " does not appear to be configured with a valid concept collectionid"
                            )
                    elif node.datatype in ["domain-value", "domain-value-list"]:
                        concepts = {}
                        if node.config["options"]:
                            for concept in node.config["options"]:
                                concepts[concept["id"]] = concept["text"]

                        values[node.name] = OrderedDict(concepts.items())

        if include_concepts == True:
            try:
                relation_concepts = OrderedDict(
                    sorted(
                        list(
                            get_values(
                                Concept().get(
                                    "00000000-0000-0000-0000-000000000005",
                                    include_subconcepts=True,
                                    semantic=False,
                                ),
                                {},
                            ).items()
                        ),
                        key=itemgetter(1),
                    )
                )
            except:
                relations_concepts = "You do not appear to have values for resource to resource relationships in your rdm."
            values["Resource to Resource Relationship Types"] = relation_concepts

    # Concept lookup file
    if include_concepts == True:
        file_name = os.path.join(
            "{0}_{1}.{2}".format(file_name_prefix, "concepts", "json")
        )
        dest = StringIO()
        dest.write(json.dumps(values, indent=4))
        files_for_export.append({"name": file_name, "outputfile": dest})

    # Import/Export mapping file
    file_name = os.path.join("{0}.{1}".format(file_name_prefix, "mapping"))
    dest = StringIO()
    dest.write(json.dumps(export_json, indent=4))
    files_for_export.append({"name": file_name, "outputfile": dest})

    if data_dir is not None:
        file_name = Graph.objects.get(graphid=graphid).name
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip:
            for f in files_for_export:
                f["outputfile"].seek(0)
                zip.writestr(f["name"], f["outputfile"].read())

        zip.close()
        buffer.flush()
        zip_stream = buffer.getvalue()
        buffer.close()
        with open(
            os.path.join(data_dir, file_name[language] + ".zip"), "wb"
        ) as archive:
            archive.write(zip_stream)
    else:
        return files_for_export
