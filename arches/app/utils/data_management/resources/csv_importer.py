import csv
import uuid
from arches.app.models.tile import Tile
from arches.app.models.models import ResourceInstance
from arches.app.models.models import NodeGroup
from arches.app.models.models import Node
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from copy import deepcopy
import cPickle

def column_names_to_targetids(row, mapping):
    new_row = []
    for key, value in row.iteritems():
        if value != '':
            for row in mapping['nodes']:
                print row
                if key.upper() == row['field_name'].upper():
                    new_row.append({row['nodeid']: value})
    return new_row

def import_business_data(business_data, mapping=None):
    blanktilecache = {}
    single_cardinality_nodegroups = []
    single_cardinality_nodegroups = [str(nodegroupid) for nodegroupid in NodeGroup.objects.values_list('nodegroupid', flat=True).filter(cardinality = '1')]
    previous_row_resourceid = business_data[0]['ResourceID']
    resourceinstanceid = uuid.uuid4()
    populated_nodegroups = {}
    populated_nodegroups[resourceinstanceid] = []

    def cache(blank_tile):
        if blank_tile.data != None:
            for key in blank_tile.data.keys():
                if key not in blanktilecache:
                    blanktilecache[str(key)] = blank_tile
        else:
            for nodegroup, tile in blank_tile.tiles.iteritems():
                for key in tile[0].data.keys():
                    if key not in blanktilecache:
                        blanktilecache[str(key)] = blank_tile

    def get_blank_tile(source_data):
        if len(source_data) > 0:
            if source_data[0] != {}:
                key = str(source_data[0].keys()[0])
                if key not in blanktilecache:
                    blank_tile = Tile.get_blank_tile(key)
                    cache(blank_tile)
                else:
                    blank_tile = blanktilecache[key]
            else:
                blank_tile = None
        else:
            blank_tile = None

        # return deepcopy(blank_tile)
        return cPickle.loads(cPickle.dumps(blank_tile, -1))

    for row in business_data:
        populated_tiles = []
        if row['ResourceID'] != previous_row_resourceid:
            resourceinstanceid = uuid.uuid4()
            previous_row_resourceid = row['ResourceID']
            populated_nodegroups[resourceinstanceid] = []
        source_data = column_names_to_targetids(row, mapping)

        if source_data[0].keys():
            target_resource_model = Node.objects.get(nodeid=source_data[0].keys()[0]).graph_id

        target_tile = get_blank_tile(source_data)

        def populate_tile(source_data, target_tile):
            need_new_tile = False
            target_tile.tileid = None
            if str(target_tile.nodegroup_id) in single_cardinality_nodegroups:
                target_tile_cardinality = '1'
            else:
                target_tile_cardinality = 'n'
            if str(target_tile.nodegroup_id) not in populated_nodegroups[resourceinstanceid]:
                if target_tile.data != None:
                    for target_key in target_tile.data.keys():
                        for source_tile in source_data:
                            for source_key in source_tile.keys():
                                if source_key == target_key:
                                    if target_tile.data[source_key] == '':
                                        target_tile.data[source_key] = source_tile[source_key]
                                        del source_tile[source_key]

                    source_data[:] = [item for item in source_data if item != {}]

                elif target_tile.tiles != None:
                    populated_child_nodegroups = []
                    for nodegroupid, childtile in target_tile.tiles.iteritems():
                        prototype_tile = childtile.pop()
                        prototype_tile.tileid = None
                        if str(prototype_tile.nodegroup_id) in single_cardinality_nodegroups:
                            child_tile_cardinality = '1'
                        else:
                            child_tile_cardinality = 'n'

                        def populate_child_tiles(source_data):
                            prototype_tile_copy = cPickle.loads(cPickle.dumps(prototype_tile, -1))
                            if str(prototype_tile_copy.nodegroup_id) not in populated_child_nodegroups:
                                for target_key in prototype_tile_copy.data.keys():
                                    for source_column in source_data:
                                        for source_key in source_column.keys():
                                            if source_key == target_key:
                                                if prototype_tile_copy.data[source_key] == '':
                                                    prototype_tile_copy.data[source_key] = source_column[source_key]
                                                    del source_column[source_key]
                                                else:
                                                    populate_child_tiles(source_data)


                            if prototype_tile_copy.data != {}:
                                if len([item for item in prototype_tile_copy.data.values() if item != '']) > 0:
                                    if str(prototype_tile_copy.nodegroup_id) not in populated_child_nodegroups:
                                        childtile.append(prototype_tile_copy)

                            if prototype_tile_copy != None:
                                if child_tile_cardinality == '1':
                                    populated_child_nodegroups.append(str(prototype_tile_copy.nodegroup_id))

                            source_data[:] = [item for item in source_data if item != {}]

                        populate_child_tiles(source_data)

                populated_tiles.append(target_tile)

                if len(source_data)>0:
                    need_new_tile = True

                if target_tile_cardinality == '1':
                    populated_nodegroups[resourceinstanceid].append(str(target_tile.nodegroup_id))

                if need_new_tile:
                    new_tile = get_blank_tile(source_data)
                    if new_tile != None:
                        populate_tile(source_data, new_tile)




        if target_tile != None and len(source_data) > 0:
            populate_tile(source_data, target_tile)


        newresourceinstance, created = ResourceInstance.objects.get_or_create(
            resourceinstanceid = resourceinstanceid,
            graph_id = target_resource_model,
            resourceinstancesecurity = None
        )

        for populated_tile in populated_tiles:
            populated_tile.resourceinstance = newresourceinstance
            populated_tile.resourceid = resourceinstanceid
            saved_tile = populated_tile.save()
