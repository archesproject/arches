import csv
import pickle
import datetime
import json
import os
import sys
import uuid
import traceback
import logging
from time import time
from copy import deepcopy
from io import StringIO
from .format import Writer
from .format import Reader
from elasticsearch import TransportError
from arches.app.models.tile import Tile
from arches.app.models.concept import Concept
from arches.app.models.models import (
    Node,
    NodeGroup,
    ResourceXResource,
    ResourceInstance,
    FunctionXGraph,
    GraphXMapping,
)
from arches.app.models.card import Card
from arches.app.utils.data_management.resource_graphs import exporter as GraphExporter
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.datatypes.datatypes import DataTypeFactory
import arches.app.utils.task_management as task_management
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)


class MissingConfigException(Exception):
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConceptLookup:
    def __init__(self, create=False):
        self.lookups = {}
        self.create = create
        self.add_domain_values_to_lookups()

    def lookup_label(self, label, collectionid):
        ret = label
        collection_values = self.lookups[collectionid]
        for concept in collection_values:
            if label == concept[1]:
                ret = concept[2]
        return ret

    def lookup_labelid_from_label(self, value, collectionid):
        ret = []
        for val in csv.reader([value], delimiter=",", quotechar='"'):
            for v in val:
                v = v.strip()
                try:
                    ret.append(self.lookup_label(v, collectionid))
                except:
                    self.lookups[collectionid] = Concept().get_child_collections(collectionid)
                    ret.append(self.lookup_label(v, collectionid))
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(ret)
        for v in [output.getvalue()]:
            return v.strip("\r\n")

    def add_domain_values_to_lookups(self):
        for node in Node.objects.filter(Q(datatype="domain-value") | Q(datatype="domain-value-list")):
            domain_collection_id = str(node.nodeid)
            self.lookups[domain_collection_id] = []
            for val in node.config["options"]:
                self.lookups[domain_collection_id].append(("0", val["text"], val["id"]))


class CsvWriter(Writer):
    def __init__(self, **kwargs):
        super(CsvWriter, self).__init__(**kwargs)
        self.node_datatypes = {
            str(nodeid): datatype
            for nodeid, datatype in Node.objects.values_list("nodeid", "datatype").filter(~Q(datatype="semantic"), graph__isresource=True)
        }
        self.single_file = kwargs.pop("single_file", False)
        self.resource_export_configs = self.read_export_configs(kwargs.pop("configs", None))

        if len(self.resource_export_configs) == 0:
            raise MissingConfigException()

    def read_export_configs(self, configs):
        """
        Reads the export configuration file or object and adds an array for records to store property data
        """
        if configs:
            resource_export_configs = json.load(open(configs, "r"))
            configs = [resource_export_configs]
        else:
            configs = []
            for val in GraphXMapping.objects.values("mapping"):
                configs.append(val["mapping"])

        return configs

    def transform_value_for_export(self, datatype, value, concept_export_value_type, node):
        datatype_instance = self.datatype_factory.get_instance(datatype)
        value = datatype_instance.transform_export_values(value, concept_export_value_type=concept_export_value_type, node=node)
        return value

    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        # use the graph id from the mapping file, not the one passed in to the method
        graph_id = self.resource_export_configs[0]["resource_model_id"]
        super(CsvWriter, self).write_resources(graph_id=graph_id, resourceinstanceids=resourceinstanceids, **kwargs)

        csv_records = []
        other_group_records = []
        mapping = {}
        concept_export_value_lookup = {}
        for resource_export_config in self.resource_export_configs:
            for node in resource_export_config["nodes"]:
                if node["file_field_name"] != "" and node["export"] == True:
                    mapping[node["arches_nodeid"]] = node["file_field_name"]
                if "concept_export_value" in node:
                    concept_export_value_lookup[node["arches_nodeid"]] = node["concept_export_value"]
        csv_header = ["ResourceID"] + list(mapping.values())
        csvs_for_export = []

        for resourceinstanceid, tiles in self.resourceinstances.items():
            csv_record = {}
            csv_record["ResourceID"] = resourceinstanceid
            csv_record["populated_node_groups"] = []

            try:
                parents = [p for p in tiles if p.parenttile_id is None]
                children = [c for c in tiles if c.parenttile_id is not None]
                tiles = parents + sorted(children, key=lambda k: k.parenttile_id)
            except Exception as e:
                logger.exception(e)

            for tile in tiles:
                other_group_record = {}
                other_group_record["ResourceID"] = resourceinstanceid
                if tile.data != {}:
                    for k in list(tile.data.keys()):
                        if tile.data[k] != "" and k in mapping and tile.data[k] is not None:
                            if mapping[k] not in csv_record and tile.nodegroup_id not in csv_record["populated_node_groups"]:
                                concept_export_value_type = None
                                if k in concept_export_value_lookup:
                                    concept_export_value_type = concept_export_value_lookup[k]
                                if tile.data[k] is not None:
                                    value = self.transform_value_for_export(
                                        self.node_datatypes[k], tile.data[k], concept_export_value_type, k
                                    )
                                    csv_record[mapping[k]] = value
                                del tile.data[k]
                            else:
                                concept_export_value_type = None
                                if k in concept_export_value_lookup:
                                    concept_export_value_type = concept_export_value_lookup[k]
                                value = self.transform_value_for_export(self.node_datatypes[k], tile.data[k], concept_export_value_type, k,)
                                other_group_record[mapping[k]] = value
                        else:
                            del tile.data[k]

                    csv_record["populated_node_groups"].append(tile.nodegroup_id)

                if other_group_record != {"ResourceID": resourceinstanceid}:
                    other_group_records.append(other_group_record)

            if csv_record != {"ResourceID": resourceinstanceid}:
                csv_records.append(csv_record)

        csv_name = os.path.join("{0}.{1}".format(self.file_name, "csv"))

        if self.single_file is not True:
            dest = StringIO()
            csvwriter = csv.DictWriter(dest, delimiter=",", fieldnames=csv_header)
            csvwriter.writeheader()
            csvs_for_export.append({"name": csv_name, "outputfile": dest})
            for csv_record in csv_records:
                if "populated_node_groups" in csv_record:
                    del csv_record["populated_node_groups"]
                csvwriter.writerow({k: str(v) for k, v in list(csv_record.items())})

            dest = StringIO()
            csvwriter = csv.DictWriter(dest, delimiter=",", fieldnames=csv_header)
            csvwriter.writeheader()
            csvs_for_export.append(
                {
                    "name": csv_name.split(".")[0] + "_groups." + csv_name.split(".")[1],
                    "outputfile": dest,
                }
            )
            for csv_record in other_group_records:
                if "populated_node_groups" in csv_record:
                    del csv_record["populated_node_groups"]
                csvwriter.writerow({k: str(v) for k, v in list(csv_record.items())})
        elif self.single_file is True:
            all_records = csv_records + other_group_records
            all_records = sorted(all_records, key=lambda k: k["ResourceID"])
            dest = StringIO()
            csvwriter = csv.DictWriter(dest, delimiter=",", fieldnames=csv_header)
            csvwriter.writeheader()
            csvs_for_export.append({"name": csv_name, "outputfile": dest})
            for csv_record in all_records:
                if "populated_node_groups" in csv_record:
                    del csv_record["populated_node_groups"]
                csvwriter.writerow({k: str(v) for k, v in list(csv_record.items())})

        if self.graph_id is not None:
            csvs_for_export = csvs_for_export + self.write_resource_relations(file_name=self.file_name)

        return csvs_for_export

    def write_resource_relations(self, file_name):
        resourceids = list(self.resourceinstances.keys())
        relations_file = []

        if self.graph_id != settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID:
            dest = StringIO()
            csv_header = [
                "resourcexid",
                "resourceinstanceidfrom",
                "resourceinstanceidto",
                "relationshiptype",
                "resourceinstancefrom_graphid",
                "resourceinstanceto_graphid",
                "nodeid",
                "tileid",
                "datestarted",
                "dateended",
                "notes",
            ]
            csvwriter = csv.DictWriter(dest, delimiter=",", fieldnames=csv_header)
            csvwriter.writeheader()
            csv_name = os.path.join("{0}.{1}".format(file_name, "relations"))
            relations_file.append({"name": csv_name, "outputfile": dest})

            relations = ResourceXResource.objects.filter(
                Q(resourceinstanceidfrom__in=resourceids) | Q(resourceinstanceidto__in=resourceids), tileid__isnull=True
            ).values(*csv_header)
            for relation in relations:
                relation["datestarted"] = relation["datestarted"] if relation["datestarted"] is not None else ""
                relation["dateended"] = relation["dateended"] if relation["dateended"] is not None else ""
                relation["notes"] = relation["notes"] if relation["notes"] is not None else ""
                csvwriter.writerow({k: str(v) for k, v in list(relation.items())})

        return relations_file


class TileCsvWriter(Writer):
    def __init__(self, **kwargs):
        super(TileCsvWriter, self).__init__(**kwargs)

    def group_tiles(self, tiles, key):
        new_tiles = {}

        for tile in tiles:
            new_tiles[str(tile[key])] = []

        for tile in tiles:
            if str(tile[key]) in new_tiles.keys():
                new_tiles[str(tile[key])].append(tile)

        return new_tiles

    def lookup_node_name(self, nodeid):
        try:
            node_name = Node.objects.get(nodeid=nodeid).name
        except Node.DoesNotExist:
            node_name = nodeid

        return node_name

    node_datatypes = {}

    def lookup_node_value(self, value, nodeid):
        if nodeid in self.node_datatypes:
            datatype = self.node_datatypes[nodeid]
        else:
            datatype = DataTypeFactory().get_instance(Node.objects.get(nodeid=nodeid).datatype)
            self.node_datatypes[nodeid] = datatype

        if value is not None:
            value = self.node_datatypes[nodeid].transform_export_values(value, concept_export_value_type="label", node=nodeid)

        return value

    def flatten_tile(self, tile, semantic_nodes):
        for nodeid in tile["data"]:
            if nodeid not in semantic_nodes:
                node_name = self.lookup_node_name(nodeid)
                node_value = self.lookup_node_value(tile["data"][nodeid], nodeid)
                tile[node_name] = node_value
        del tile["data"]

        return tile

    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        super(TileCsvWriter, self).write_resources(graph_id=graph_id, resourceinstanceids=resourceinstanceids, **kwargs)

        csvs_for_export = []

        tiles = self.group_tiles(
            list(Tile.objects.filter(resourceinstance__graph_id=graph_id).order_by("nodegroup_id").values()), "nodegroup_id"
        )
        semantic_nodes = [str(n[0]) for n in Node.objects.filter(datatype="semantic").values_list("nodeid")]

        for nodegroupid, nodegroup_tiles in tiles.items():
            flattened_tiles = []
            fieldnames = []
            for tile in nodegroup_tiles:
                tile["tileid"] = str(tile["tileid"])
                tile["resourceinstance_id"] = str(tile["resourceinstance_id"])
                tile["parenttile_id"] = str(tile["parenttile_id"])
                tile["nodegroup_id"] = str(tile["nodegroup_id"])
                flattened_tile = self.flatten_tile(tile, semantic_nodes)
                flattened_tiles.append(flattened_tile)

                for fieldname in flattened_tile:
                    if fieldname not in fieldnames:
                        fieldnames.append(fieldname)

            tiles[nodegroupid] = sorted(flattened_tiles, key=lambda k: k["resourceinstance_id"])

            ncsv_file = []
            dest = StringIO()
            csvwriter = csv.DictWriter(dest, delimiter=",", fieldnames=fieldnames)
            csvwriter.writeheader()
            csv_name = os.path.join("{0}.{1}".format(Card.objects.get(nodegroup_id=nodegroupid).name, "csv"))
            for v in tiles[nodegroupid]:
                csvwriter.writerow(v)
            csvs_for_export.append({"name": csv_name, "outputfile": dest})

        return csvs_for_export


class CsvReader(Reader):
    def __init__(self):
        self.errors = []
        super(CsvReader, self).__init__()

    def verify_flattened_tiles(self, tiles):
        return [t for tile in tiles for t in tile.get_flattened_tiles()]

    def save_resource(
        self,
        populated_tiles,
        resourceinstanceid,
        legacyid,
        resources,
        target_resource_model,
        bulk,
        save_count,
        row_number,
        prevent_indexing,
    ):
        # create a resource instance only if there are populated_tiles
        errors = []
        if len(populated_tiles) > 0:
            newresourceinstance = Resource(
                resourceinstanceid=resourceinstanceid,
                graph_id=target_resource_model,
                legacyid=legacyid,
                createdtime=datetime.datetime.now(),
            )
            # add the tiles to the resource instance
            newresourceinstance.tiles = [t for t in populated_tiles]
            populated_tiles.clear()

            # if bulk saving then append the resources to a list otherwise just save the resource
            if bulk:
                resources.append(newresourceinstance)
                if len(resources) >= settings.BULK_IMPORT_BATCH_SIZE:
                    Resource.bulk_save(resources=resources, flat=True)
                    del resources[:]  # clear out the array
            else:
                try:
                    newresourceinstance.save(index=(not prevent_indexing))

                except TransportError as e:

                    cause = json.dumps(e.info["error"]["reason"], indent=1)
                    msg = "%s: WARNING: failed to index document in resource: %s %s. Exception detail:\n%s\n" % (
                        datetime.datetime.now(),
                        resourceinstanceid,
                        row_number,
                        cause,
                    )
                    errors.append({"type": "WARNING", "message": msg})
                    newresourceinstance.delete()
                    save_count = save_count - 1
                except Exception as e:
                    msg = "%s: WARNING: failed to save document in resource: %s %s. Exception detail:\n%s\n" % (
                        datetime.datetime.now(),
                        resourceinstanceid,
                        row_number,
                        e,
                    )
                    errors.append({"type": "WARNING", "message": msg})
                    newresourceinstance.delete()
                    save_count = save_count - 1

        else:
            errors.append(
                {
                    "type": "WARNING",
                    "message": f"No resource created for legacyid: {legacyid}. Make sure there is data to be imported \
                    for this resource and it is mapped properly in your mapping file.",
                }
            )

        if len(errors) > 0:
            self.errors += errors

        if save_count % (settings.BULK_IMPORT_BATCH_SIZE / 4) == 0:
            print("%s resources processed" % str(save_count))

    def import_business_data(
        self,
        business_data=None,
        mapping=None,
        overwrite="append",
        bulk=False,
        create_concepts=False,
        create_collections=False,
        prevent_indexing=False,
    ):
        # errors = businessDataValidator(self.business_data)
        celery_worker_running = task_management.check_if_celery_available()
        mapping_filefieldname_to_nodeid_dict = {n["file_field_name"].upper(): n["arches_nodeid"] for n in mapping["nodes"]}
        headers = [k.upper() for k in business_data[0].keys() if k.upper() != "RESOURCEID"]
        non_unique_col_headers = False
        unique_nodeids = set(list(mapping_filefieldname_to_nodeid_dict.values()))
        evaluation_nodegroupid = "a271c31e-1037-11ec-b65f-31043b30bbcd"  # parent tiledata IS semantic, parenttile=null
        component_nodegroupid = "a271c312-1037-11ec-b65f-31043b30bbcd"  # tiledata is not semantic, parenttile=null
        component_type_nodeid = "a271c374-1037-11ec-b65f-31043b30bbcd"
        place_nodegroupid = "a271c336-1037-11ec-b65f-31043b30bbcd"
        address_nodegroupid = "a271c321-1037-11ec-b65f-31043b30bbcd"
        hist_dist_eval_nodegroupid = "bb6de9e8-98a2-11eb-b28f-5f1901ec6b3b"
        if len(unique_nodeids) != len(list(mapping_filefieldname_to_nodeid_dict.keys())):
            non_unique_col_headers = True
        non_unique_col_headers = False
        try:
            col_header_to_nodeid_dict = {header: mapping_filefieldname_to_nodeid_dict[header.upper()] for header in headers}
        except KeyError as e:
            missing_headers_from_mapping = [header for header in headers if header.upper() not in mapping_filefieldname_to_nodeid_dict]
            self.errors.append(
                {
                    "type": "WARNING",
                    "message": f"""Some data unable to be imported: {str(len(missing_headers_from_mapping))} column names
                    from .csv could not be found as file_field_name values in your .mapping file:\n {missing_headers_from_mapping}.""",
                }
            )
            col_header_to_nodeid_dict = {
                header: mapping_filefieldname_to_nodeid_dict[header.upper()]
                for header in headers
                if header.upper() in mapping_filefieldname_to_nodeid_dict
            }

        print("Starting import of business data")
        self.start = time()

        def get_display_nodes(graphid):
            display_nodeids = []
            functions = FunctionXGraph.objects.filter(function_id="60000000-0000-0000-0000-000000000001", graph_id=graphid)
            for function in functions:
                f = function.config
                del f["triggering_nodegroups"]

                for k, v in f.items():
                    v["node_ids"] = []
                    v["string_template"] = v["string_template"].replace("<", "").replace(">", "").split(", ")
                    if "nodegroup_id" in v and v["nodegroup_id"] != "":
                        nodes = Node.objects.filter(nodegroup_id=v["nodegroup_id"])
                        for node in nodes:
                            if node.name in v["string_template"]:
                                display_nodeids.append(str(node.nodeid))

                for k, v in f.items():
                    if "string_template" in v and v["string_template"] != [""]:
                        print(
                            "The {0} {1} in the {2} display function.".format(
                                ", ".join(v["string_template"]),
                                "nodes participate" if len(v["string_template"]) > 1 else "node participates",
                                k,
                            )
                        )
                    else:
                        print("No nodes participate in the {0} display function.".format(k))

            return display_nodeids

        def process_resourceid(resourceid, legacyid, overwrite):
            # Test if resourceid is a UUID.
            try:
                resourceinstanceid = uuid.UUID(resourceid)
                # If resourceid is a UUID check if it is already an arches resource.
                if overwrite == "overwrite":
                    try:
                        Resource.objects.get(pk=resourceid).delete(index=False)
                    except:
                        ret = list(Resource.objects.filter(legacyid=resourceid))
                        if legacyid:
                            ret.extend(list(Resource.objects.filter(legacyid=legacyid)))
                        for r in ret:
                            r.delete(index=False)
            except:
                # Get resources with the given legacyid
                ret = list(Resource.objects.filter(legacyid=resourceid))
                if legacyid:
                    ret.extend(list(Resource.objects.filter(legacyid=legacyid)))

                # If more than one resource is returned than make resource = None. This should never actually happen.
                if len(ret) > 1:
                    resourceinstanceid = None
                # If no resource is returned with the given legacyid then create an archesid for the resource.
                elif len(ret) == 0:
                    resourceinstanceid = uuid.uuid4()
                # If a resource is returned with the give legacyid then return its archesid
                else:
                    if overwrite == "overwrite":
                        Resource.objects.get(pk=str(ret[0].resourceinstanceid)).delete(index=False)
                    resourceinstanceid = ret[0].resourceinstanceid

            return resourceinstanceid

        try:
            with transaction.atomic():
                save_count = 0
                legacyid = business_data[0]["LegacyID"] if "LegacyID" in business_data[0] else None
                try:
                    resourceinstanceid = process_resourceid(business_data[0]["ResourceID"], legacyid, overwrite)
                except KeyError:
                    print("*" * 80)
                    print(
                        "ERROR: No column 'ResourceID' found in business data file. \
                        Please add a 'ResourceID' column with a unique resource identifier."
                    )
                    print("*" * 80)
                    if celery_worker_running is False:  # prevents celery chord from breaking on WorkerLostError
                        sys.exit()
                graphid = mapping["resource_model_id"]
                blanktilecache = {}
                populated_cardinality_1_nodegroups = {}
                populated_cardinality_1_nodegroups[resourceinstanceid] = []
                previous_row_resourceid = None
                group_no_to_tileids = {}
                populated_tiles = []
                target_resource_model = None
                single_cardinality_nodegroups = [
                    str(nodegroupid) for nodegroupid in NodeGroup.objects.values_list("nodegroupid", flat=True).filter(cardinality="1")
                ]
                node_datatypes = {
                    str(nodeid): datatype
                    for nodeid, datatype in Node.objects.values_list("nodeid", "datatype").filter(
                        ~Q(datatype="semantic"), graph__isresource=True
                    )
                }
                display_nodes = get_display_nodes(graphid)
                all_nodes = Node.objects.filter(graph_id=graphid)
                node_dict = {str(node.pk): node for node in all_nodes}
                datatype_factory = DataTypeFactory()
                concepts_to_create = {}
                new_concepts = {}
                required_nodes = {}
                for node in Node.objects.filter(~Q(datatype="semantic"), isrequired=True, graph_id=graphid).values_list("nodeid", "name"):
                    required_nodes[str(node[0])] = node[1]

                # This code can probably be moved into it's own module.
                resourceids = set()
                non_contiguous_resource_ids = []
                previous_row_for_validation = None

                for row_number, row in enumerate(business_data):
                    # Check contiguousness of csv file.
                    if row["ResourceID"] != previous_row_for_validation and row["ResourceID"] in resourceids:
                        non_contiguous_resource_ids.append(row["ResourceID"])
                    else:
                        resourceids.add(row["ResourceID"])
                    previous_row_for_validation = row["ResourceID"]

                    if create_concepts == True:
                        for node in mapping["nodes"]:
                            if node["data_type"] in ["concept", "concept-list", "domain-value", "domain-value-list"] and node[
                                "file_field_name"
                            ] in list(row.keys()):

                                concept = []
                                for val in csv.reader([row[node["file_field_name"]]], delimiter=",", quotechar='"'):
                                    concept.append(val)
                                concept = concept[0]

                                # check if collection is in concepts_to_create,
                                # add collection to concepts_to_create if it's not and add first child concept
                                if node["arches_nodeid"] not in concepts_to_create:
                                    concepts_to_create[node["arches_nodeid"]] = {}
                                    for concept_value in concept:
                                        concepts_to_create[node["arches_nodeid"]][str(uuid.uuid4())] = concept_value
                                # if collection in concepts to create then add child concept to collection
                                elif row[node["file_field_name"]] not in list(concepts_to_create[node["arches_nodeid"]].values()):
                                    for concept_value in concept:
                                        concepts_to_create[node["arches_nodeid"]][str(uuid.uuid4())] = concept_value

                if len(non_contiguous_resource_ids) > 0:
                    print("*" * 80)
                    for non_contiguous_resource_id in non_contiguous_resource_ids:
                        print("ResourceID: " + non_contiguous_resource_id)
                    print(
                        "ERROR: The preceding ResourceIDs are non-contiguous in your csv file. \
                        Please sort your csv file by ResourceID and try import again."
                    )
                    print("*" * 80)
                    if celery_worker_running is False:  # prevents celery chord from breaking on WorkerLostError
                        sys.exit()

                def create_reference_data(new_concepts, create_collections):
                    errors = []
                    candidates = Concept().get(id="00000000-0000-0000-0000-000000000006")
                    for arches_nodeid, concepts in new_concepts.items():
                        collectionid = str(uuid.uuid4())
                        topconceptid = str(uuid.uuid4())
                        node = self.lookup_node(arches_nodeid)

                        # if node.datatype is concept or concept-list create concepts and collections
                        if node.datatype in ["concept", "concept-list"]:
                            # create collection if create_collections = create, otherwise append to collection already assigned to node
                            if create_collections == True:
                                collection_legacyoid = node.name + "_" + str(node.graph_id) + "_import"
                                # check to see that there is not already a collection for this node
                                if node.config["rdmCollection"] is not None:
                                    errors.append(
                                        {
                                            "type": "WARNING",
                                            "message": f"A collection already exists for the {node.name} node. \
                                            Use the add option to add concepts to this collection.",
                                        }
                                    )
                                    if len(errors) > 0:
                                        self.errors += errors
                                    collection = None
                                else:
                                    # if there is no collection assigned to this node, create one and assign it to the node
                                    try:
                                        # check to see that a collection with this legacyid does not already exist
                                        collection = Concept().get(legacyoid=collection_legacyoid)
                                        errors.append(
                                            {
                                                "type": "WARNING",
                                                "message": "A collection with the legacyid {0} already exists.".format(
                                                    node.name + "_" + str(node.graph_id) + "_import"
                                                ),
                                            }
                                        )
                                        if len(errors) > 0:
                                            self.errors += errors
                                    except:
                                        collection = Concept(
                                            {"id": collectionid, "legacyoid": collection_legacyoid, "nodetype": "Collection"}
                                        )
                                        collection.addvalue(
                                            {
                                                "id": str(uuid.uuid4()),
                                                "value": node.name + "_import",
                                                "language": settings.LANGUAGE_CODE,
                                                "type": "prefLabel",
                                            }
                                        )
                                        node.config["rdmCollection"] = collectionid
                                        node.save()
                                        collection.save()
                            else:
                                # if create collection = add check that there is a collection associated with node,
                                # if no collection associated with node create a collection and associated with the node
                                try:
                                    collection = Concept().get(id=node.config["rdmCollection"])
                                except:
                                    collection = Concept(
                                        {
                                            "id": collectionid,
                                            "legacyoid": node.name + "_" + str(node.graph_id) + "_import",
                                            "nodetype": "Collection",
                                        }
                                    )
                                    collection.addvalue(
                                        {
                                            "id": str(uuid.uuid4()),
                                            "value": node.name + "_import",
                                            "language": settings.LANGUAGE_CODE,
                                            "type": "prefLabel",
                                        }
                                    )
                                    node.config["rdmCollection"] = collectionid
                                    node.save()
                                    collection.save()

                            if collection is not None:
                                topconcept_legacyoid = node.name + "_" + str(node.graph_id)
                                # Check if top concept already exists, if not create it and add to candidates scheme
                                try:
                                    topconcept = Concept().get(legacyoid=topconcept_legacyoid)
                                except:
                                    topconcept = Concept({"id": topconceptid, "legacyoid": topconcept_legacyoid, "nodetype": "Concept"})
                                    topconcept.addvalue(
                                        {
                                            "id": str(uuid.uuid4()),
                                            "value": node.name + "_import",
                                            "language": settings.LANGUAGE_CODE,
                                            "type": "prefLabel",
                                        }
                                    )
                                    topconcept.save()
                                candidates.add_relation(topconcept, "narrower")

                                # create child concepts and relate to top concept and collection accordingly
                                for conceptid, value in concepts.items():
                                    concept_legacyoid = value + "_" + node.name + "_" + str(node.graph_id)
                                    # check if concept already exists, if not create and add to topconcept and collection
                                    try:
                                        conceptid = [
                                            concept for concept in topconcept.get_child_concepts(topconcept.id) if concept[1] == value
                                        ][0][0]
                                        concept = Concept().get(id=conceptid)
                                    except:
                                        concept = Concept({"id": conceptid, "legacyoid": concept_legacyoid, "nodetype": "Concept"})
                                        concept.addvalue(
                                            {
                                                "id": str(uuid.uuid4()),
                                                "value": value,
                                                "language": settings.LANGUAGE_CODE,
                                                "type": "prefLabel",
                                            }
                                        )
                                        concept.save()
                                    collection.add_relation(concept, "member")
                                    topconcept.add_relation(concept, "narrower")

                        # if node.datatype is domain or domain-list create options array in node.config
                        elif node.datatype in ["domain-value", "domain-value-list"]:
                            for domainid, value in new_concepts[arches_nodeid].items():
                                # check if value already exists in domain
                                if value not in [t["text"] for t in node.config["options"]]:
                                    domainvalue = {"text": value, "selected": False, "id": domainid}
                                    node.config["options"].append(domainvalue)
                                    node.save()

                if create_concepts == True:
                    create_reference_data(concepts_to_create, create_collections)
                # if concepts are created on import concept_lookup must be instatiated afterward
                concept_lookup = ConceptLookup()

                def cache(blank_tile):
                    if blank_tile.data != {}:
                        for key in list(blank_tile.data.keys()):
                            if key not in blanktilecache:
                                blanktilecache[str(key)] = blank_tile
                    else:
                        for tile in blank_tile.tiles:
                            for key in list(tile.data.keys()):
                                if key not in blanktilecache:
                                    blanktilecache[str(key)] = blank_tile

                def column_names_to_targetids(row, mapping, row_number):
                    errors = []
                    if "ADDITIONAL" in row or "MISSING" in row:
                        errors.append(
                            {
                                "type": "WARNING",
                                "message": "No resource created for ResourceID {0}. Line {1} has additional or missing columns.".format(
                                    row["ResourceID"], str(int(row_number.split("on line ")[1]))
                                ),
                            }
                        )
                        if len(errors) > 0:
                            self.errors += errors
                    return [
                        {col_header_to_nodeid_dict[key.upper()]: value}
                        for key, value in row.items()
                        if value != "" and key.upper() != "RESOURCEID" and key.upper() in col_header_to_nodeid_dict
                    ]

                def transform_value(datatype, value, source, nodeid):
                    """
                    Transforms values from probably string/wkt representation to specified datatype in arches.
                    This code could probably move to somehwere where it can be accessed by other importers.
                    """
                    request = ""
                    if datatype != "":
                        errors = []
                        datatype_instance = self.datatype_factory.get_instance(datatype)
                        if datatype in ["concept", "domain-value", "concept-list", "domain-value-list"]:
                            try:
                                uuid.UUID(value)
                            except:
                                if datatype in ["domain-value", "domain-value-list"]:
                                    collection_id = nodeid
                                else:
                                    collection_id = self.lookup_node(nodeid).config["rdmCollection"]
                                if collection_id is not None:
                                    value = concept_lookup.lookup_labelid_from_label(value, collection_id)
                        try:
                            value = datatype_instance.transform_value_for_tile(value)
                            errors = datatype_instance.validate(value, row_number=row_number, source=source, nodeid=nodeid)
                        except Exception as e:
                            errors.append(
                                {
                                    "type": "ERROR",
                                    "message": "datatype: {0} value: {1} {2} - {3}".format(
                                        datatype_instance.datatype_model.classname,
                                        value,
                                        source,
                                        str(e) + " or is not a prefLabel in the given collection.",
                                    ),
                                }
                            )
                        if len(errors) > 0:
                            error_types = [error["type"] for error in errors]
                            if "ERROR" in error_types:
                                value = None
                            self.errors += errors
                    else:
                        print(_("No datatype detected for {0}".format(value)))

                    return {"value": value, "request": request}

                def get_blank_tile(source_data, child_only=False):
                    if len(source_data) > 0:
                        if source_data[0] != {}:
                            key = str(list(source_data[0].keys())[0])
                            source_node = node_dict[key]
                            if child_only:
                                blank_tile = Tile.get_blank_tile_from_nodegroup_id(str(source_node.nodegroup_id))
                            elif key not in blanktilecache:
                                blank_tile = Tile.get_blank_tile(key)
                                cache(blank_tile)
                            else:
                                blank_tile = blanktilecache[key]
                                blank_tile.tileid = uuid.uuid4()
                        else:
                            blank_tile = None
                    else:
                        blank_tile = None
                    # return deepcopy(blank_tile)
                    return pickle.loads(pickle.dumps(blank_tile, -1))

                def get_preexisting_tile(target_tile, populated_tiles, resourceid, parenttileid=None, tileid=None):
                    # finds a pre-existing tile for a particular nodegroup on a resource_instance
                    # assumes tiles are flat/un-nested, otherwise recurses through child tiles
                    if tileid:
                        preexisting_tile_for_nodegroup = list(filter(lambda t: str(t.tileid) == str(tileid), populated_tiles))
                    elif parenttileid:
                        preexisting_tile_for_nodegroup = list(
                            filter(
                                lambda t: str(t.resourceinstance_id) == str(resourceid)
                                and str(t.nodegroup_id) == str(target_tile.nodegroup_id)
                                and str(t.parenttile.tileid) == str(parenttileid),
                                populated_tiles,
                            )
                        )
                    else:
                        preexisting_tile_for_nodegroup = list(
                            filter(
                                lambda t: str(t.resourceinstance_id) == str(resourceid)
                                and str(t.nodegroup_id) == str(target_tile.nodegroup_id),
                                populated_tiles,
                            )
                        )
                    if len(preexisting_tile_for_nodegroup) > 0:
                        return preexisting_tile_for_nodegroup[0]
                    for t in populated_tiles:
                        get_preexisting_tile(target_tile, t.tiles, resourceid, parenttileid, tileid)

                def get_preexisting_parenttileid(tileid, populated_tiles):
                    preexisting_parenttile = list(
                        filter(
                            lambda t: str(t.tileid) == str(tileid),
                            populated_tiles,
                        )
                    )
                    if len(preexisting_parenttile) > 0:
                        return str(preexisting_parenttile[0].tileid)
                    for t in populated_tiles:
                        get_preexisting_parenttileid(tileid, t.tiles)

                def check_required_nodes(tile, parent_tile, required_nodes):
                    # Check that each required node in a tile is populated.
                    if settings.BYPASS_REQUIRED_VALUE_TILE_VALIDATION:
                        return
                    errors = []
                    if len(required_nodes) > 0:
                        if bool(tile.data):
                            for target_k, target_v in tile.data.items():
                                if target_k in list(required_nodes.keys()) and target_v is None:
                                    if parent_tile in populated_tiles:
                                        populated_tiles.pop(populated_tiles.index(parent_tile))
                                    errors.append(
                                        {
                                            "type": "WARNING",
                                            "message": "The {0} node ({1}) is required and must be populated. \
                                            This data was not imported.".format(
                                                required_nodes[target_k],
                                                target_k,
                                            ),
                                        }
                                    )
                        elif bool(tile.tiles):
                            for tile in tile.tiles:
                                check_required_nodes(tile, parent_tile, required_nodes)
                    if len(errors) > 0:
                        self.errors += errors

                def populate_tile(
                    source_data,
                    tile_to_populate,
                    row,
                    row_number,
                    resourceinstanceid,
                    populated_tiles,
                    group_no,
                    group_valid,
                    group_no_to_tileids,
                    non_unique_col_headers,
                    populated_cardinality_1_nodegroups,
                    node_datatypes,
                    appending_to_parent=False,
                    prefix="",
                ):
                    """
                    source_data = [{nodeid:value},{nodeid:value},{nodeid:value} . . .]
                    All nodes in source_data belong to the same resource.
                    A dictionary of nodeids would not allow for multiple values for the same nodeid.
                    Grouping is enforced by having all grouped attributes in the same row.
                    """
                    need_new_tile = False
                    if group_valid:
                        if str(tile_to_populate.nodegroup_id) == component_nodegroupid:
                            group_no = row["GROUP_NO"] + "-" + str(prefix)
                        elif str(tile_to_populate.nodegroup_id) in [evaluation_nodegroupid, hist_dist_eval_nodegroupid]:
                            group_no = row["GROUP_NO"]
                    # Set target tileid to None because this will be a new tile, a new tileid will be created on save.
                    if tile_to_populate.tileid is None:
                        tile_to_populate.tileid = uuid.uuid4()
                    if "TileID" in row and row["TileID"] is not None:
                        tile_to_populate.tileid = row["TileID"]
                    tile_to_populate.resourceinstance_id = resourceinstanceid
                    # if first time seeing this nodegroup for this group
                    if (
                        group_valid
                        and group_no
                        and group_no in group_no_to_tileids
                        and str(tile_to_populate.nodegroup_id) not in group_no_to_tileids[group_no]
                    ):
                        group_no_to_tileids[group_no][str(tile_to_populate.nodegroup_id)] = {}
                        group_no_to_tileids[group_no][str(tile_to_populate.nodegroup_id)]["tileid"] = str(tile_to_populate.tileid)
                        try:
                            group_no_to_tileids[group_no][str(target_tile.nodegroup_id)]["parenttileid"] = str(
                                target_tile.parenttile.tileid
                            )
                        except:
                            group_no_to_tileids[group_no][str(target_tile.nodegroup_id)]["parenttileid"] = None

                    # Check the cardinality of the tile and check if it has been populated.
                    # If cardinality is one and the tile is populated the tile should not be populated again.
                    if str(tile_to_populate.nodegroup_id) in single_cardinality_nodegroups and "TileiD" not in row:
                        target_tile_cardinality = "1"
                    else:
                        target_tile_cardinality = "n"

                    def populate_child_tiles(source_data):
                        prototype_tile_copy = pickle.loads(pickle.dumps(childtile, -1))
                        tileid = row["TileID"] if "TileID" in row else uuid.uuid4()
                        prototype_tile_copy.tileid = tileid
                        prototype_tile_copy.parenttile = tile_to_populate
                        parenttileid = row["ParentTileID"] if "ParentTileID" in row and row["ParentTileID"] is not None else None
                        if parenttileid is not None:
                            prototype_tile_copy.parenttile.tileid = parenttileid
                        prototype_tile_copy.resourceinstance_id = resourceinstanceid
                        # if (
                        #     row["GROUP_NO"]
                        #     and row["GROUP_NO"] != ""
                        #     and row["GROUP_NO"] in group_no_to_tileids[row["ResourceID"]]
                        #     and str(prototype_tile_copy.nodegroup_id)
                        #     not in group_no_to_tileids[row["ResourceID"]][row["GROUP_NO"]]
                        # ):
                        #     group_no_to_tileids[row["ResourceID"]][row["GROUP_NO"]][
                        #         str(prototype_tile_copy.nodegroup_id)
                        #     ] = str(prototype_tile_copy.tileid)
                        if str(prototype_tile_copy.nodegroup_id) not in populated_child_nodegroups:
                            prototype_tile_copy.nodegroup_id = str(prototype_tile_copy.nodegroup_id)
                            for target_key in list(prototype_tile_copy.data.keys()):
                                if non_unique_col_headers:
                                    for source_column in source_data:
                                        for source_key in list(source_column.keys()):
                                            if source_key == target_key:
                                                if prototype_tile_copy.data[source_key] is None:
                                                    value = transform_value(
                                                        node_datatypes[source_key],
                                                        source_column[source_key],
                                                        row_number,
                                                        source_key,
                                                    )
                                                    prototype_tile_copy.data[source_key] = value["value"]
                                                    # print(prototype_tile_copy.data[source_key]
                                                    # print('&'*80
                                                    # target_tile.request = value['request']
                                                    del source_column[source_key]
                                                else:
                                                    populate_child_tiles(source_data)
                                else:
                                    s_tile_value = source_dict.get(target_key, None)
                                    if s_tile_value is not None and prototype_tile_copy.data[target_key] is None:
                                        try:
                                            value = transform_value(node_datatypes[target_key], s_tile_value, row_number, target_key)
                                            prototype_tile_copy.data[target_key] = value["value"]
                                            found = list(filter(lambda x: x.get(target_key, "not found") != "not found", source_data))
                                            if len(found) > 0:
                                                found = found[0]
                                                i = source_data.index(found)
                                                del source_dict[target_key]
                                                del source_data[i]
                                        except KeyError:  # semantic datatype
                                            pass
                                    elif (
                                        s_tile_value
                                        and prototype_tile_copy.data[target_key]
                                        and isinstance(prototype_tile_copy.data[target_key], list)
                                    ):  # weve found a pre-existing value for this node on tile
                                        try:
                                            value = transform_value(node_datatypes[target_key], s_tile_value, row_number, target_key)
                                            value = value["value"]
                                            if (isinstance(value, str) is False or isinstance(value, uuid) is False) and isinstance(
                                                value, list
                                            ):
                                                value = value[0]

                                            prototype_tile_copy.data[target_key].append(value)
                                            found = list(filter(lambda x: x.get(target_key, "not found") != "not found", source_data))
                                            if len(found) > 0:
                                                found = found[0]
                                                i = source_data.index(found)
                                                del source_dict[target_key]
                                                del source_data[i]
                                        except KeyError:  # semantic datatype
                                            pass

                                    elif s_tile_value is None:
                                        found = list(filter(lambda x: x.get(target_key, "not found") != "not found", source_data))
                                        if len(found) > 0:
                                            found = found[0]
                                            i = source_data.index(found)
                                            del source_dict[target_key]
                                            del source_data[i]
                                    elif prototype_tile_copy.data[target_key] is not None:
                                        populate_child_tiles(source_data)

                        if prototype_tile_copy.data != {}:
                            if (
                                group_valid
                                and group_no
                                and group_no in group_no_to_tileids
                                and str(prototype_tile_copy.nodegroup_id) not in group_no_to_tileids[group_no]
                            ):
                                group_no_to_tileids[group_no][str(prototype_tile_copy.nodegroup_id)] = {}
                                group_no_to_tileids[group_no][str(prototype_tile_copy.nodegroup_id)]["tileid"] = str(
                                    prototype_tile_copy.tileid
                                )
                                try:
                                    group_no_to_tileids[group_no][str(prototype_tile_copy.nodegroup_id)]["parenttileid"] = str(
                                        prototype_tile_copy.parenttile.tileid
                                    )
                                except:
                                    group_no_to_tileids[group_no][str(prototype_tile_copy.nodegroup_id)]["parenttileid"] = None
                            if len([item for item in list(prototype_tile_copy.data.values()) if item is not None]) > 0:
                                if str(prototype_tile_copy.nodegroup_id) not in populated_child_nodegroups:
                                    if bulk:
                                        prototype_tile_copy.tiles = []
                                        populated_tiles.append(prototype_tile_copy)
                                    else:
                                        populated_child_tiles.append(prototype_tile_copy)

                        if prototype_tile_copy is not None:
                            if child_tile_cardinality == "1" and "NodeGroupID" not in row:
                                populated_child_nodegroups.append(str(prototype_tile_copy.nodegroup_id))

                        source_data[:] = [item for item in source_data if item != {}]

                    if (
                        str(tile_to_populate.nodegroup_id) not in populated_cardinality_1_nodegroups[resourceinstanceid]
                        or appending_to_parent
                    ):
                        tile_to_populate.nodegroup_id = str(tile_to_populate.nodegroup_id)
                        # Check if we are populating a parent tile by inspecting the tile_to_populate.data array.
                        source_data_has_target_tile_nodes = (
                            len({list(obj.keys())[0] for obj in source_data} & set(tile_to_populate.data.keys())) > 0
                        )
                        source_dict = {k: v for s in source_data for k, v in s.items()}

                        if source_data_has_target_tile_nodes:
                            # Iterate through the tile nodes and begin populating by iterating through source_data array.
                            # The idea is to populate as much of the tile_to_populate as possible,
                            # before moving on to the next tile_to_populate.
                            for target_key in list(tile_to_populate.data.keys()):
                                if non_unique_col_headers:
                                    for source_tile in source_data:
                                        for source_key in list(source_tile.keys()):
                                            # Check for source and target key match.
                                            if source_key == target_key:
                                                if tile_to_populate.data[source_key] is None:
                                                    # If match populate tile_to_populate node with transformed value.
                                                    value = transform_value(
                                                        node_datatypes[source_key], source_tile[source_key], row_number, source_key
                                                    )
                                                    tile_to_populate.data[source_key] = value["value"]
                                                    # tile_to_populate.request = value['request']
                                                    # Delete key from source_tile so
                                                    # we do not populate another tile based on the same data.
                                                    del source_tile[source_key]
                                else:
                                    s_tile_value = source_dict.get(target_key, None)
                                    if s_tile_value is not None and tile_to_populate.data[target_key] is None:
                                        # If match populate tile_to_populate node with transformed value.
                                        try:
                                            value = transform_value(node_datatypes[target_key], s_tile_value, row_number, target_key)

                                            tile_to_populate.data[target_key] = value["value"]
                                            found = list(filter(lambda x: x.get(target_key, "not found") != "not found", source_data))
                                            if len(found) > 0:
                                                found = found[0]
                                                i = source_data.index(found)
                                                del source_dict[target_key]
                                                del source_data[i]
                                        except KeyError:  # semantic datatype
                                            pass
                                    elif (
                                        s_tile_value
                                        and tile_to_populate.data[target_key]
                                        and isinstance(tile_to_populate.data[target_key], list)
                                    ):  # weve found a pre-existing value for this node on tile
                                        try:
                                            value = transform_value(node_datatypes[target_key], s_tile_value, row_number, target_key)
                                            value = value["value"]
                                            if (isinstance(value, str) is False or isinstance(value, uuid) is False) and isinstance(
                                                value, list
                                            ):
                                                value = value[0]

                                            tile_to_populate.data[target_key].append(value)
                                            found = list(filter(lambda x: x.get(target_key, "not found") != "not found", source_data))
                                            if len(found) > 0:
                                                found = found[0]
                                                i = source_data.index(found)
                                                del source_dict[target_key]
                                                del source_data[i]
                                        except KeyError:  # semantic datatype
                                            pass
                                    elif s_tile_value is None:
                                        found = list(filter(lambda x: x.get(target_key, "not found") != "not found", source_data))
                                        if len(found) > 0:
                                            found = found[0]
                                            i = source_data.index(found)
                                            del source_dict[target_key]
                                            del source_data[i]
                            # Cleanup source_data array to remove source_tiles that are now '{}' from the code above.
                            source_data[:] = [item for item in source_data if item != {}]

                        # Check if we are populating a child tile(s) by inspecting the target_tiles.tiles array.
                        elif tile_to_populate.tiles is not None:
                            populated_child_tiles = []
                            populated_child_nodegroups = []
                            for childtile in tile_to_populate.tiles:
                                if str(childtile.nodegroup_id) in single_cardinality_nodegroups:
                                    child_tile_cardinality = "1"
                                else:
                                    child_tile_cardinality = "n"

                                populate_child_tiles(source_data)

                            if not bulk:
                                tile_to_populate.tiles = populated_child_tiles

                        # bulk alone being true here is because a parent tile without children would fail (not tile.is_blank())
                        if bulk or (not tile_to_populate.is_blank() and not appending_to_parent):
                            if bulk:
                                tile_to_populate.tiles = []
                            dupe = False
                            for i, t in enumerate(populated_tiles):
                                if str(t.tileid) == str(tile_to_populate.tileid):
                                    # if t.data == tile_to_populate.data: # we mutated a pre-existing tile, don't re-add
                                    dupe = True
                                    break

                            if not dupe:
                                populated_tiles.append(tile_to_populate)

                        if len(source_data) > 0 and component_type_nodeid not in source_data[0]:
                            need_new_tile = True
                        elif len(source_data) > 0 and component_type_nodeid in source_data[0]:
                            if len(source_data) == 1 and component_type_nodeid in source_data[0] and len(list(source_data[0].keys())) == 1:
                                source_data.pop(0)  # TODO TEMPORARY: remove Details components that have a component type

                        if target_tile_cardinality == "1" and "NodeGroupID" not in row:
                            populated_cardinality_1_nodegroups[resourceinstanceid].append(str(tile_to_populate.nodegroup_id))

                        if need_new_tile:
                            new_tile = get_blank_tile(source_data)
                            if new_tile is not None:
                                populate_tile(
                                    source_data,
                                    new_tile,
                                    row,
                                    row_number,
                                    resourceinstanceid,
                                    populated_tiles,
                                    group_no,
                                    group_valid,
                                    group_no_to_tileids,
                                    non_unique_col_headers,
                                    populated_cardinality_1_nodegroups,
                                    node_datatypes,
                                    appending_to_parent=False,
                                    prefix=prefix,
                                )

                resources = []
                missing_display_values = {}
                group_no = False
                # if some rows have a ResourceID and not a LegacyID while others a LegacyID and no ResourceID, this import breaks
                legacyids_only = (
                    business_data[0]["ResourceID"] is None or business_data[0]["ResourceID"] == ""
                ) and "LegacyID" in business_data[0]

                for row_number, row in enumerate(business_data):
                    i = int(row_number)
                    if "LegacyID" not in row:
                        row["LegacyID"] = None
                    row_number = "on line " + str(row_number + 2)  # to represent the row in a csv accounting for the header and 0 index
                    if legacyids_only and i > 0:
                        resource_changed = business_data[i - 1]["LegacyID"] != row["LegacyID"]
                    else:
                        resource_changed = str(resourceinstanceid) != str(row["ResourceID"]) and i > 0
                    if resource_changed:
                        # print(legacyid)
                        group_no_to_tileids.clear()  # garbage collection of past resource groups

                        save_count = save_count + 1
                        self.save_resource(
                            populated_tiles,
                            resourceinstanceid,
                            legacyid,
                            resources,
                            target_resource_model,
                            bulk,
                            save_count,
                            row_number,
                            prevent_indexing,
                        )

                        # reset values for next resource instance
                        resourceinstanceid = process_resourceid(row["ResourceID"], legacyid, overwrite)
                        populated_cardinality_1_nodegroups.clear()
                        populated_cardinality_1_nodegroups[resourceinstanceid] = []

                    legacyid = row["LegacyID"] if row["LegacyID"] else resourceinstanceid
                    if "SPATIAL_GEO" in row and row["SPATIAL_GEO"] and row["SPATIAL_GEO"] != '':
                        slice_at = row["SPATIAL_GEO"].index('(')
                        geom = row["SPATIAL_GEO"][slice_at:]
                        counter = 0
                        for char in  geom:
                            if char == '(':
                                counter += 1
                            elif char == ')':
                                counter -= 1
                        if counter != 0:
                            print(f"ERROR at {legacyid}")
                            row["SPATIAL_GEO"] = ''
                    source_data = column_names_to_targetids(row, mapping, row_number)
                    group_no = False
                    group_valid = "GROUP_NO" in row and row["GROUP_NO"] and row["GROUP_NO"] != ""
                    prefix = None

                    # row_keys = [list(b) for b in zip(*[list(a.keys()) for a in source_data])]

                    # missing_display_nodes = [n for n in display_nodes if n not in row_keys]
                    # if len(missing_display_nodes) > 0:
                    #     errors = []
                    #     for mdn in missing_display_nodes:
                    #         mdn_name = self.lookup_node(mdn).name
                    #         try:
                    #             missing_display_values[mdn_name].append(row_number.split("on line ")[-1])
                    #         except:
                    #             missing_display_values[mdn_name] = [row_number.split("on line ")[-1]]

                    if len(source_data) > 0:
                        if list(source_data[0].keys()):
                            try:
                                nodeid = list(source_data[0].keys())[0]
                                target_resource_model = self.lookup_node(nodeid).graph_id
                            except ObjectDoesNotExist as e:
                                print("*" * 80)
                                print(
                                    "ERROR: No resource model found. Please make sure the resource model \
                                    this business data is mapped to has been imported into Arches."
                                )
                                print(e)
                                print("*" * 80)
                                if celery_worker_running is False:  # prevents celery chord from breaking on WorkerLostError
                                    sys.exit()

                        # IF GROUP_NO IS SAME AND PREFIX IS SAME, PARENT_TILE REMAINS SAME, i.e. AGGREGATE ON PARENT_TILE:
                        preexisting_tile_for_nodegroup = False
                        target_tile = get_blank_tile(source_data)  # Heres our parent tile, i.e. a semantic Evaluation or a Semantic
                        target_tile.tileid = uuid.uuid4()

                        # group_no = False
                        # group_valid = row["GROUP_NO"] and row["GROUP_NO"] != ""
                        if group_valid and not isinstance(row["GROUP_NO"], str):
                            row["GROUP_NO"] = str(row["GROUP_NO"])

                        if group_valid and str(target_tile.nodegroup_id) in [evaluation_nodegroupid, hist_dist_eval_nodegroupid]:
                            group_no = row["GROUP_NO"]

                        # {
                        #   group_no: {
                        #       nodegroupid: {
                        #           tileid: tileid,
                        #           parenttileid: parenttileid
                        #       }
                        #   }
                        # }

                        # all the tiles should be flat except for the first appearance of a NG on a resource???

                        # if there's an object in source_data that is node integiry, elgibility, or one of the component concept-list nodes, then aggregate on tile
                        # TODO: figure out how to aggregate values without changing tiles (maybe don't append to populated_tiles later?)
                        # append what we need to to the source data
                        # if row['COMP_SORTORDER']
                        # nodegroup_type = 'other'
                        preexisting_tile_for_resource_group_nodegroup = False
                        preexisting_parenttile = False
                        sort_str = False

                        last_prefix = None
                        prefix_same = False

                        if "COMP_SORTORDER" in row and row["COMP_SORTORDER"] and row["COMP_SORTORDER"] != "":
                            sort_str = row["COMP_SORTORDER"]

                        if sort_str and "DETAILS" in sort_str:  # TODO NOT ADVISABLE TO JUST SKIP, TESTING PURPOSES ONLY
                            continue

                        if (
                            str(target_tile.nodegroup_id) in [evaluation_nodegroupid, hist_dist_eval_nodegroupid, component_nodegroupid]
                            and group_valid
                        ):

                            if str(target_tile.nodegroup_id) in [evaluation_nodegroupid, hist_dist_eval_nodegroupid]:
                                if group_no not in group_no_to_tileids:
                                    group_no_to_tileids[group_no] = {}
                                # checks for whether a parent tile exists since get_blank_tile starts out getting parent
                                preexisting_parenttile_for_resource_group_nodegroup = (
                                    group_no in group_no_to_tileids and str(target_tile.nodegroup_id) in group_no_to_tileids[group_no]
                                )
                                if preexisting_parenttile_for_resource_group_nodegroup:
                                    preexisting_parenttile = get_preexisting_tile(
                                        target_tile,
                                        populated_tiles,
                                        resourceinstanceid,
                                        tileid=group_no_to_tileids[group_no][str(target_tile.nodegroup_id)]["tileid"],
                                    )
                                    # we know theres a parenttile for this group already
                                if preexisting_parenttile:  # lets see if theres a child for our source_data's nodegroup
                                    prototype_child_tile = get_blank_tile(source_data, child_only=True)

                                    # we could also ask if a tile exists for this group in the group dict
                                    # {group_no: {nodegroupid: {tileid: tileid, parenttileid: parenttileid } } }
                                    preexisting_childtile_for_resource_group_nodegroup = (
                                        group_no in group_no_to_tileids
                                        and str(prototype_child_tile.nodegroup_id) in group_no_to_tileids[group_no]
                                    )
                                    if preexisting_childtile_for_resource_group_nodegroup:
                                        test_tile = get_preexisting_tile(
                                            target_tile,
                                            populated_tiles,
                                            resourceinstanceid,
                                            tileid=str(group_no_to_tileids[group_no][str(prototype_child_tile.nodegroup_id)]["tileid"]),
                                        )
                                        if test_tile:
                                            target_tile = test_tile
                                    else:
                                        target_tile = prototype_child_tile
                                        target_tile.tileid = uuid.uuid4()
                                        target_tile.parenttile = preexisting_parenttile
                                        group_no_to_tileids[group_no][str(target_tile.nodegroup_id)] = {}
                                        group_no_to_tileids[group_no][str(target_tile.nodegroup_id)]["tileid"] = str(target_tile.tileid)
                                        try:
                                            group_no_to_tileids[group_no][str(target_tile.nodegroup_id)]["parenttileid"] = str(
                                                target_tile.parenttile.tileid
                                            )
                                        except:
                                            group_no_to_tileids[group_no][str(target_tile.nodegroup_id)]["parenttileid"] = None

                            elif str(target_tile.nodegroup_id) == component_nodegroupid:
                                # TODO: Comp_sortorder must be used for Components so that all component tiles for a resource/group don't get merged into a single one
                                # only need to know if prefix_changed, prefix functions same way as group

                                if sort_str and "-" in sort_str and group_valid:  # component or eval
                                    prefix = sort_str[0:2]
                                    group_no = row["GROUP_NO"] + "-" + str(prefix)
                                    if group_no not in group_no_to_tileids:
                                        group_no_to_tileids[group_no] = {}
                                    if "-" in business_data[i - 1]["COMP_SORTORDER"]:
                                        last_prefix = business_data[i - 1]["COMP_SORTORDER"][0:2]

                                    prefix_same = prefix == last_prefix and previous_row_resourceid == resourceinstanceid

                                    # we want to look for an original tile with the same group if the group is the same
                                    # if the group is different, defintely just make a new tile, i.e. prevent an existing tile from being looked up
                                    preexisting_tile_for_resource_group_nodegroup = (
                                        group_no in group_no_to_tileids and str(target_tile.nodegroup_id) in group_no_to_tileids[group_no]
                                    )

                                    if prefix_same and preexisting_tile_for_resource_group_nodegroup:
                                        preexisting_tile_for_nodegroup = get_preexisting_tile(
                                            target_tile,
                                            populated_tiles,
                                            resourceinstanceid,
                                            tileid=group_no_to_tileids[group_no][str(target_tile.nodegroup_id)]["tileid"],
                                        )
                                        if preexisting_tile_for_nodegroup:
                                            target_tile = preexisting_tile_for_nodegroup

                        if "TileID" in row and row["TileID"] is not None:
                            target_tile.tileid = row["TileID"]
                        if "NodeGroupID" in row and row["NodeGroupID"] is not None:
                            target_tile.nodegroupid = row["NodeGroupID"]

                        # mock_request_object = HttpRequest()

                        # identify whether a tile for this nodegroup on this resource already exists
                        if not preexisting_tile_for_nodegroup and not preexisting_parenttile:
                            preexisting_tile_for_nodegroup = get_preexisting_tile(target_tile, populated_tiles, resourceinstanceid)

                        # aggregates a tile of the nodegroup associated with source_data (via get_blank_tile)
                        # onto the pre-existing tile who would be its parent
                        if target_tile.nodegroup.cardinality == "1" and preexisting_tile_for_nodegroup and len(source_data) > 0:
                            target_tile = get_blank_tile(source_data, child_only=True)
                            target_tile.parenttile = preexisting_tile_for_nodegroup
                            populate_tile(
                                source_data,
                                target_tile,
                                row,
                                row_number,
                                resourceinstanceid,
                                populated_tiles,
                                group_no,
                                group_valid,
                                group_no_to_tileids,
                                non_unique_col_headers,
                                populated_cardinality_1_nodegroups,
                                node_datatypes,
                                appending_to_parent=True,
                                prefix=prefix,
                            )
                            if not bulk:
                                preexisting_tile_for_nodegroup.tiles.append(target_tile)
                            while len(source_data) > 0:
                                target_tile = get_blank_tile(source_data)
                                preexisting_tile_for_nodegroup = get_preexisting_tile(target_tile, populated_tiles, resourceinstanceid)
                                if preexisting_tile_for_nodegroup:
                                    target_tile = get_blank_tile(source_data, child_only=True)
                                    target_tile.parenttile = preexisting_tile_for_nodegroup
                                    populate_tile(
                                        source_data,
                                        target_tile,
                                        row,
                                        row_number,
                                        resourceinstanceid,
                                        populated_tiles,
                                        group_no,
                                        group_valid,
                                        group_no_to_tileids,
                                        non_unique_col_headers,
                                        populated_cardinality_1_nodegroups,
                                        node_datatypes,
                                        appending_to_parent=True,
                                        prefix=prefix,
                                    )
                                else:
                                    target_tile = get_blank_tile(source_data)
                                    populate_tile(
                                        source_data,
                                        target_tile,
                                        row,
                                        row_number,
                                        resourceinstanceid,
                                        populated_tiles,
                                        group_no,
                                        group_valid,
                                        group_no_to_tileids,
                                        non_unique_col_headers,
                                        populated_cardinality_1_nodegroups,
                                        node_datatypes,
                                        prefix=prefix,
                                    )

                                if not bulk and preexisting_tile_for_nodegroup:
                                    preexisting_tile_for_nodegroup.tiles.append(target_tile)

                        # populates a tile from parent-level nodegroup because
                        # parent cardinality is N or because none exists yet on resource
                        elif target_tile is not None and len(source_data) > 0:
                            populate_tile(
                                source_data,
                                target_tile,
                                row,
                                row_number,
                                resourceinstanceid,
                                populated_tiles,
                                group_no,
                                group_valid,
                                group_no_to_tileids,
                                non_unique_col_headers,
                                populated_cardinality_1_nodegroups,
                                node_datatypes,
                                prefix=prefix,
                            )
                            if len(source_data) == 1 and component_type_nodeid in source_data[0] and len(list(source_data[0].keys())) == 1:
                                source_data.pop(0)  # TODO TEMPORARY: remove Details components that have a component type
                            while len(source_data) > 0:
                                target_tile = get_blank_tile(source_data)
                                preexisting_tile_for_nodegroup = get_preexisting_tile(target_tile, populated_tiles, resourceinstanceid)
                                if preexisting_tile_for_nodegroup and str(target_tile.nodegroup_id) != component_nodegroupid:
                                    target_tile = get_blank_tile(source_data, child_only=True)
                                    target_tile.parenttile = preexisting_tile_for_nodegroup
                                    populate_tile(
                                        source_data,
                                        target_tile,
                                        row,
                                        row_number,
                                        resourceinstanceid,
                                        populated_tiles,
                                        group_no,
                                        group_valid,
                                        group_no_to_tileids,
                                        non_unique_col_headers,
                                        populated_cardinality_1_nodegroups,
                                        node_datatypes,
                                        appending_to_parent=True,
                                        prefix=prefix,
                                    )
                                elif preexisting_tile_for_nodegroup and str(target_tile.nodegroup_id) == component_nodegroupid:
                                    populate_tile(
                                        source_data,
                                        target_tile,
                                        row,
                                        row_number,
                                        resourceinstanceid,
                                        populated_tiles,
                                        group_no,
                                        group_valid,
                                        group_no_to_tileids,
                                        non_unique_col_headers,
                                        populated_cardinality_1_nodegroups,
                                        node_datatypes,
                                        prefix=prefix,
                                    )
                                else:
                                    target_tile = get_blank_tile(source_data)
                                    populate_tile(
                                        source_data,
                                        target_tile,
                                        row,
                                        row_number,
                                        resourceinstanceid,
                                        populated_tiles,
                                        group_no,
                                        group_valid,
                                        group_no_to_tileids,
                                        non_unique_col_headers,
                                        populated_cardinality_1_nodegroups,
                                        node_datatypes,
                                        prefix=prefix,
                                    )
                                if not bulk and preexisting_tile_for_nodegroup:
                                    preexisting_tile_for_nodegroup.tiles.append(target_tile)
                            # Check that required nodes are populated. If not remove tile from populated_tiles array.
                            check_required_nodes(target_tile, target_tile, required_nodes)

                    previous_row_resourceid = resourceinstanceid

                # check for missing display value nodes.
                # errors = []
                # for k, v in missing_display_values.items():
                #     if len(v) > 0:
                #         errors.append(
                #             {
                #                 "type": "WARNING",
                #                 "message": "{0} is null or not mapped on rows {1} and \
                #                 participates in a display value function.".format(
                #                     k, ",".join(v)
                #                 ),
                #             }
                #         )
                # if len(errors) > 0:
                #     self.errors += errors

                if "legacyid" in locals():
                    self.save_resource(
                        populated_tiles,
                        resourceinstanceid,
                        legacyid,
                        resources,
                        target_resource_model,
                        bulk,
                        save_count,
                        row_number,
                        prevent_indexing,
                    )

                if bulk:
                    Resource.bulk_save(resources=resources, flat=True)
                    del resources[:]  # clear out the array
                    print("Time to create resource and tile objects: %s" % datetime.timedelta(seconds=time() - self.start))
                save_count = save_count + 1
                print(_("Total resources saved: {save_count}").format(**locals()))

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            formatted = traceback.format_exception(exc_type, exc_value, exc_traceback)
            if len(formatted):
                for message in formatted:
                    logger.error(message)

        finally:
            for e in self.errors:
                if e["type"] == "WARNING":
                    logger.warn(e["message"])
                elif e["type"] == "ERROR":
                    logger.error(e["message"])
                else:
                    logger.info(e["message"])


class TileCsvReader(Reader):
    def __init__(self, business_data):
        super(TileCsvReader, self).__init__()
        self.csv_reader = CsvReader()
        self.business_data = business_data

    def import_business_data(self, overwrite=None):
        resource_model_id = str(self.business_data[0]["ResourceModelID"])
        mapping = json.loads(
            GraphExporter.create_mapping_configuration_file(resource_model_id, include_concepts=False)[0]["outputfile"].getvalue()
        )

        self.csv_reader.import_business_data(self.business_data, mapping, overwrite=overwrite)
