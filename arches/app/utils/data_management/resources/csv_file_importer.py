'''
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
'''

import os
import sys
import csv
import json
import uuid
import cPickle
import distutils.util
from copy import deepcopy
from mimetypes import MimeTypes
from os.path import isfile, join
from django.conf import settings
from django.db.models import Q
from django.http import HttpRequest
from django.contrib.gis.geos import GEOSGeometry
from django.core.files import File as DjangoFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from arches.app.models.tile import Tile
from arches.app.models.resource import Resource
from arches.app.models.models import File
from arches.app.models.models import Node
from arches.app.models.models import NodeGroup
from arches.app.datatypes import datatypes
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


class CSVFileImporter(object):

    def import_business_data(self, business_data=None, mapping=None, bulk=False):
        errors = []
        # errors = businessDataValidator(self.business_data)
        if len(errors) == 0:
            resourceinstanceid = uuid.uuid4()
            blanktilecache = {}
            populated_nodegroups = {}
            populated_nodegroups[resourceinstanceid] = []
            single_cardinality_nodegroups = [str(nodegroupid) for nodegroupid in NodeGroup.objects.values_list('nodegroupid', flat=True).filter(cardinality = '1')]
            node_datatypes = {str(nodeid): datatype for nodeid, datatype in  Node.objects.values_list('nodeid', 'datatype').filter(~Q(datatype='semantic'), graph__isresource=True)}

            previous_row_resourceid = None # business_data[0]['ResourceID']
            #resourceinstanceid = uuid.uuid4()
            populated_tiles = []


            def cache(blank_tile):
                if blank_tile.data != {}:
                    for key in blank_tile.data.keys():
                        if key not in blanktilecache:
                            blanktilecache[str(key)] = blank_tile
                else:
                    for nodegroup, tile in blank_tile.tiles.iteritems():
                        for key in tile[0].data.keys():
                            if key not in blanktilecache:
                                blanktilecache[str(key)] = blank_tile

            def column_names_to_targetids(row, mapping):
                new_row = []
                for key, value in row.iteritems():
                    if value != '':
                        for row in mapping['nodes']:
                            if key.upper() == row['file_field_name'].upper():
                                new_row.append({row['arches_nodeid']: value})
                return new_row

            def transform_value(datatype, value):
                '''
                Transforms values from probably string/wkt representation to specified datatype in arches.
                This code could probably move to somehwere where it can be accessed by other importers.
                '''
                request = ''
                if datatype != '':
                    datatype_instance = datatypes.get_datatype_instance(datatype)
                    value = datatype_instance.transform_import_values(value)
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


            def save_resource(populated_tiles, resourceinstanceid):
                # create the resource instance
                newresourceinstance, created = Resource.objects.get_or_create(
                    resourceinstanceid=resourceinstanceid,
                    defaults={'graph_id': target_resource_model, 'resourceinstancesecurity': None}
                )

                # save all the tiles related to the resource instance
                if bulk:
                    tiles = populated_tiles
                    for populated_tile in populated_tiles:
                        for tile in populated_tile.tiles.itervalues():
                            if len(tiles) > 0:
                                tiles = tiles + tile
                    Tile.objects.bulk_create(tiles)
                else:
                    for populated_tile in populated_tiles:
                        saved_tile = populated_tile.save(index=False)
                newresourceinstance.index()


            for row in business_data:
                if row['ResourceID'] != previous_row_resourceid and previous_row_resourceid is not None:

                    save_resource(populated_tiles, resourceinstanceid)

                    # reset values for next resource instance
                    populated_tiles = []
                    resourceinstanceid = uuid.uuid4()
                    populated_nodegroups[resourceinstanceid] = []

                source_data = column_names_to_targetids(row, mapping)

                if source_data[0].keys():
                    target_resource_model = Node.objects.get(nodeid=source_data[0].keys()[0]).graph_id

                target_tile = get_blank_tile(source_data)

                def populate_tile(source_data, target_tile):
                    '''
                    source_data = [{nodeid:value},{nodeid:value},{nodeid:value} . . .]
                    All nodes in source_data belong to the same resource.
                    A dictionary of nodeids would not allow for multiple values for the same nodeid.
                    Grouping is enforced by having all grouped attributes in the same row.
                    '''
                    need_new_tile = False
                    # Set target tileid to None because this will be a new tile, a new tileid will be created on save.
                    target_tile.tileid = uuid.uuid4()
                    target_tile.resourceinstance_id = resourceinstanceid
                    # Check the cardinality of the tile and check if it has been populated.
                    # If cardinality is one and the tile is populated the tile should not be populated again.
                    if str(target_tile.nodegroup_id) in single_cardinality_nodegroups:
                        target_tile_cardinality = '1'
                    else:
                        target_tile_cardinality = 'n'
                    if str(target_tile.nodegroup_id) not in populated_nodegroups[resourceinstanceid]:
                        # Check if we are populating a parent tile by inspecting the target_tile.data array.
                        if target_tile.data != {}:
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
                                prototype_tile.parenttile = target_tile
                                prototype_tile.resourceinstance_id = resourceinstanceid
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

                previous_row_resourceid = row['ResourceID']

            save_resource(populated_tiles, resourceinstanceid)

        else:
            for error in errors:
                print "{0} {1}".format(error[0], error[1])
