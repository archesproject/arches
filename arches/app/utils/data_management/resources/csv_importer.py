import csv
import uuid
from arches.app.models.tile import Tile
from arches.app.models.models import ResourceInstance
from arches.app.models.models import NodeGroup
from arches.app.models.models import Node
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from copy import deepcopy

def column_names_to_targetids(row, mapping):
    new_row = []
    for key, value in row.iteritems():
        if value != '':
            for row in mapping:
                if key.upper() == row['sourceNodeName'].upper():
                    new_row.append({row['targetnodeid']: value})
    return new_row

def import_business_data(business_data, mapping=None):
    blanktilecache = {}
    target_nodegroup_cardinalities = {}
    for nodegroup in JSONSerializer().serializeToPython(NodeGroup.objects.all()):
        target_nodegroup_cardinalities[nodegroup['nodegroupid']] = nodegroup['cardinality']
    previous_row_resourceid = business_data[0]['ResourceID']
    resourceinstanceid = uuid.uuid4()
    populated_nodegroups = []

    def cache(blank_tile):
        if blank_tile.data != {}:
            for tile in blank_tile.tiles.values():
                if isinstance(tile, Tile):
                    for key in tile.data.keys():
                        blanktilecache[key] = blank_tile

    for row in business_data:
        populated_tiles = []
        if row['ResourceID'] != previous_row_resourceid:
            resourceinstanceid = uuid.uuid4()
            previous_row_resourceid = row['ResourceID']
        source_data = column_names_to_targetids(row, mapping)

        if source_data[0].keys():
            target_resource_model = Node.objects.get(nodeid=source_data[0].keys()[0]).graph_id

        for data in source_data:

            def get_blank_tile(source_data):
                if len(source_data) > 0:
                    if source_data[0] != {}:
                        if source_data[0].keys()[0] not in blanktilecache:
                            blank_tile = Tile.get_blank_tile(source_data[0].keys()[0], resourceid=resourceinstanceid)
                            cache(blank_tile)
                        else:
                            blank_tile = blanktilecache[source_data[0].keys()[0]]
                    else:
                        blank_tile = None
                else:
                    blank_tile = None
                return blank_tile

            blank_tile = get_blank_tile(source_data)

            def populate_tile(source_data, blank_tile):
                if blank_tile:
                    target_tile_cardinality = target_nodegroup_cardinalities[str(blank_tile.nodegroup_id)]
                    print str(blank_tile.nodegroup_id) not in populated_nodegroups
                    if str(blank_tile.nodegroup_id) not in populated_nodegroups:
                        if blank_tile.data:
                            for source_tile in source_data:
                                for source_key in source_tile.keys():
                                    if source_key in blank_tile.data:
                                        if blank_tile.data[source_key] == '':
                                            blank_tile.data[source_key] = source_tile[source_key]
                                            for key in source_tile.keys():
                                                if key == source_key:
                                                    del source_tile[source_key]

                        elif blank_tile.tiles != None:
                            populated_child_nodegroups = []
                            for nodegroupid, childtile in blank_tile.tiles.iteritems():
                                childtile_empty = True
                                child_tile_cardinality = target_nodegroup_cardinalities[str(childtile[0].nodegroup_id)]
                                prototype_tile = childtile.pop()
                                prototype_tile.tileid = None

                                for source_tile in source_data:
                                    if prototype_tile.nodegroup_id not in populated_child_nodegroups:
                                        prototype_tile_copy = deepcopy(prototype_tile)
                                        for nodeid in source_tile.keys():
                                            if nodeid in prototype_tile.data.keys():
                                                if prototype_tile.data[nodeid] == '':
                                                    prototype_tile_copy.data[nodeid] = source_tile[nodeid]
                                                    for key in source_tile.keys():
                                                        if key == nodeid:
                                                            del source_tile[nodeid]
                                                    if child_tile_cardinality == '1':
                                                        populated_child_nodegroups.append(prototype_tile.nodegroup_id)

                                    if prototype_tile_copy is not None:
                                        childtile.append(prototype_tile_copy)

                        if target_tile_cardinality == '1':
                            populated_nodegroups.append(str(blank_tile.nodegroup_id))
                            
                    else:
                        blank_tile = None

                    if blank_tile != None:
                        populated_tiles.append(blank_tile)

        populate_tile(source_data, blank_tile)

        newresourceinstance, created = ResourceInstance.objects.get_or_create(
            resourceinstanceid = resourceinstanceid,
            graph_id = target_resource_model,
            resourceinstancesecurity = None
        )

        for populated_tile in populated_tiles:
            populated_tile.resourceinstance = newresourceinstance
            saved_tile = populated_tile.save()
