import csv
import uuid
import cPickle
import json
import os
from copy import deepcopy
from django.db.models import Q
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File as DjangoFile
from django.http import HttpRequest
from django.contrib.gis.geos import GEOSGeometry
from arches.app.models.tile import Tile
from arches.app.models.models import ResourceInstance
from arches.app.models.models import NodeGroup
from arches.app.models.models import Node
from arches.app.models.models import File
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from mimetypes import MimeTypes
import distutils.util

def column_names_to_targetids(row, mapping):
    new_row = []
    for key, value in row.iteritems():
        if value != '':
            for row in mapping['nodes']:
                if key.upper() == row['file_field_name'].upper():
                    new_row.append({row['arches_nodeid']: value})
    return new_row

def import_business_data(business_data, mapping=None):
    resourceinstanceid = uuid.uuid4()
    blanktilecache = {}
    populated_nodegroups = {}
    populated_nodegroups[resourceinstanceid] = []
    single_cardinality_nodegroups = [str(nodegroupid) for nodegroupid in NodeGroup.objects.values_list('nodegroupid', flat=True).filter(cardinality = '1')]
    node_datatypes = {str(nodeid): datatype for nodeid, datatype in  Node.objects.values_list('nodeid', 'datatype').filter(~Q(datatype='semantic'), graph__isresource=True)}

    previous_row_resourceid = business_data[0]['ResourceID']

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

    def transform_value(datatype, value):
        '''
        Transforms values from probably string/wkt representation to specified datatype in arches.
        This code could probably move to somehwere where it can be accessed by other importers.
        '''
        request = ''
        if datatype != '':
            if datatype == 'string':
                pass
            elif datatype == 'number':
                value = float(value)
            elif datatype == 'date':
                # datetime.datetime.strptime(value, '%Y-%m-%d')
                pass
            elif datatype == 'boolean':
                value = bool(distutils.util.strtobool(value))
            elif datatype == 'concept' or datatype = 'domain value':
                pass
            elif datatype == 'concept-list' or datatype == 'domain-value-list':
                value = value.split(',')
            elif datatype == 'geojson-feature-collection':
                arches_geojson = {}
                arches_geojson['type'] = "FeatureCollection"
                arches_geojson['features'] = []

                geometry = GEOSGeometry(value, srid=4326)
                if geometry.num_geom > 1:
                    for geom in geometry:
                        arches_json_geometry = {}
                        arches_json_geometry['geometry'] = JSONDeserializer().deserialize(GEOSGeometry(geom, srid=4326).json)
                        arches_json_geometry['type'] = "Feature"
                        arches_json_geometry['id'] = str(uuid.uuid4())
                        arches_json_geometry['properties'] = {}
                        arches_geojson['features'].append(arches_json_geometry)
                else:
                    arches_json_geometry = {}
                    arches_json_geometry['geometry'] = JSONDeserializer().deserialize(geometry.json)
                    arches_json_geometry['type'] = "Feature"
                    arches_json_geometry['id'] = str(uuid.uuid4())
                    arches_json_geometry['properties'] = {}
                    arches_geojson['features'].append(arches_json_geometry)

                value = arches_geojson

            elif datatype == 'file-list':
                '''
                Following commented code can be used if user does not already have file in final location using django ORM
                '''
                # request = HttpRequest()
                # # request.FILES['file-list_' + str(nodeid)] = None
                # files = []
                # # request_list = []
                #
                # for val in value.split(','):
                #     val_dict = {}
                #     val_dict['content'] = val
                #     val_dict['name'] = val.split('/')[-1].split('.')[0]
                #     val_dict['url'] = None
                #     # val_dict['size'] = None
                #     # val_dict['width'] = None
                #     # val_dict['height'] = None
                #     files.append(val_dict)
                #
                #     f = open(val, 'rb')
                #     django_file = InMemoryUploadedFile(f,'file',val.split('/')[-1].split('.')[0],None,None,None)
                #     request.FILES.appendlist('file-list_' + str(nodeid), django_file)
                #
                # print request.FILES
                # value = files

                mime = MimeTypes()
                tile_data = []
                for file_path in value.split(','):
                    try:
                        file_stats = os.stat(file_path)
                        tile_file['lastModified'] = file_stats.st_mtime
                        tile_file['size'] =  file_stats.st_size
                    except:
                        pass
                    tile_file = {}
                    tile_file['file_id'] =  str(uuid.uuid4())
                    tile_file['status'] = ""
                    tile_file['name'] =  file_path.split('/')[-1]
                    tile_file['url'] =  settings.MEDIA_URL + 'uploadedfiles/' + str(tile_file['name'])
                    # tile_file['index'] =  0
                    # tile_file['height'] =  960
                    # tile_file['content'] =  None
                    # tile_file['width'] =  1280
                    # tile_file['accepted'] =  True

                    tile_file['type'] =  mime.guess_type(file_path)[0]
                    tile_file['type'] = '' if tile_file['type'] == None else file_tile['type']


                    tile_data.append(tile_file)

                    file_path = 'uploadedfiles/' + str(tile_file['name'])
                    fileid = tile_file['file_id']
                    File.objects.get_or_create(fileid=fileid, path=file_path)

                value = json.loads(json.dumps(tile_data))
        else:
            print 'No datatype detected for {0}'.format(value)

        return {'value': value, 'request': request}

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
            '''
            source_data = [{nodeid:value},{nodeid:value},{nodeid:value} . . .]
            A dictionary of nodeids would not allow for multiple values for the same nodeid.
            Grouping is enforced by having all grouped attributes in the same row.
            '''
            need_new_tile = False
            # Set target tileid to None because this will be a new tile, a new tileid will be created on save.
            target_tile.tileid = None
            # Check the cardinality of the tile and check if it has been populated.
            # If cardinality is one we want to know when the tile has been populated
            # because that will be the only occurence of this tile in this resource.
            if str(target_tile.nodegroup_id) in single_cardinality_nodegroups:
                target_tile_cardinality = '1'
            else:
                target_tile_cardinality = 'n'
            if str(target_tile.nodegroup_id) not in populated_nodegroups[resourceinstanceid]:
                # Check if we are populating a parent tile by inspecting the target_tile.data array.
                if target_tile.data != None:
                    # Iterate through the target_tile nodes and begin populating by iterating througth source_data array.
                    # The idea is to populate as much of the target_tile as possible, before moving on to the next target_tile.
                    for target_key in target_tile.data.keys():
                        for source_tile in source_data:
                            for source_key in source_tile.keys():
                                # Check for source and target key match.
                                if source_key == target_key:
                                    if target_tile.data[source_key] == '':
                                        # If match populate target_tile node with transformed value.
                                        value = transform_value(node_datatypes[source_key], source_tile[source_key])
                                        target_tile.data[source_key] = value['value']
                                        # target_tile.request = value['request']
                                        # Delete key from source_tile so we do not populate another tile based on the same data.
                                        del source_tile[source_key]
                    # Cleanup source_data array to remove source_tiles that are now '{}' from the code above.
                    source_data[:] = [item for item in source_data if item != {}]

                # Check if we are populating a child tile(s) by inspecting the target_tiles.tiles array.
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
                                                    value = transform_value(node_datatypes[source_key], source_column[source_key])
                                                    prototype_tile_copy.data[source_key] = value['value']
                                                    # target_tile.request = value['request']
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

        # mock_request_object = HttpRequest()

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
