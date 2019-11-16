import json
import csv

json_data = open("logical_model.json")
logical_model = json.load(json_data)


def name_to_id(entity_json):
    suffix = "E1"
    if entity_json["type"] == "domains":
        suffix = "E55"
    if entity_json["type"] == "authority document":
        suffix = "E32"
    if "crm_class" in list(entity_json.keys()):
        suffix = entity_json["crm_class"]
    ret = str.upper(entity_json["name"])
    ret = str.replace(ret, " ", "_")
    return ret + "." + suffix


def get_type(entity_json):
    ret = entity_json["type"]
    if ret == "authority document":
        ret = "strings"
    if ret == "foreign key":
        ret = "strings"
    return ret


def add_entity(nodes_writer, edges_writer, entity_json, parent_id, current_node_id, current_edge_id, resource_id, add_edge):
    next_node_id = current_node_id + 1
    next_edge_id = current_edge_id + 1
    mergenode = resource_id
    if "mergenode" in list(entity_json.keys()):
        mergenode = entity_json["mergenode"]
    relationship = "P1"
    if "relationship" in list(entity_json.keys()):
        relationship = entity_json["relationship"]
    nodes_writer.writerow([current_node_id, name_to_id(entity_json), mergenode, get_type(entity_json)])
    if add_edge:
        edges_writer.writerow([parent_id, current_node_id, "Directed", current_edge_id, relationship, "1.0"])
    if "entities" in list(entity_json.keys()):
        for child_json in entity_json["entities"]:
            if (
                child_json["type"] not in ["primary key", "foreign key"]
                or "entities" in list(child_json.keys())
                and len(child_json["entities"]) > 0
            ):
                next_ids = add_entity(
                    nodes_writer, edges_writer, child_json, current_node_id, next_node_id, next_edge_id, resource_id, True
                )
                next_node_id = next_ids["next_node_id"] + 1
                next_edge_id = next_ids["next_edge_id"] + 1
    return {"next_node_id": next_node_id, "next_edge_id": next_edge_id}


for resource in logical_model["resources"]:
    resource_id = name_to_id(resource)

    with open(resource_id + "_nodes.csv", "wb") as nodes_file:
        with open(resource_id + "_edges.csv", "wb") as edges_file:
            nodes_writer = csv.writer(nodes_file)
            nodes_writer.writerow(["Id", "Label", "mergenode", "businesstable"])
            edges_writer = csv.writer(edges_file)
            edges_writer.writerow(["Source", "Target", "Type", "Id", "Label", "Weight"])
            add_entity(nodes_writer, edges_writer, resource, 1, 1, 1, resource_id, False)
