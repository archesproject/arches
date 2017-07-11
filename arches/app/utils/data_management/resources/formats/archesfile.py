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
import datetime
from time import time
from os.path import isfile, join
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as resourceGraphImporter
from arches.app.models.tile import Tile
from arches.app.models.models import ResourceInstance
from arches.app.models.models import FunctionXGraph
from arches.app.models.models import ResourceXResource
from arches.app.models.models import NodeGroup
from arches.app.models.models import Value
from django.core.exceptions import ValidationError
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from copy import deepcopy
from format import Writer
from format import Reader
from format import ResourceImportReporter


class ArchesFileReader(Reader):

    def pre_import(self, tile, graph_id):
        for function in self.get_function_class_instances(tile, graph_id):
            try:
                function.on_import(tile)
            except NotImplementedError:
                pass
        return tile

    def get_function_class_instances(self, tile, graph_id):
        ret = []
        functions = FunctionXGraph.objects.filter(graph_id=graph_id, config__triggering_nodegroups__contains=[tile['nodegroup_id']])
        for function in functions:
            mod_path = function.function.modulename.replace('.py', '')
            module = importlib.import_module('arches.app.functions.%s' % mod_path)
            func = getattr(module, function.function.classname)(function.config, tile['nodegroup_id'])
            ret.append(func)
        return ret

    def validate_business_data(self, business_data):
        errors = []
        if type(business_data) == dict and business_data['resources']:
            for resource in business_data['resources']:
                graph_id = resource['resourceinstance']['graph_id']
                for tile in resource['tiles']:
                    try:
                        self.pre_import(tile, graph_id)
                    except ValidationError as e:
                        errors.append(e.args)
        return errors

    def import_graphs(self):
        """
        Wrapper around arches.app.utils.data_management.resource_graphs.importer method.
        """
        resourceGraphImporter(self.graphs)

    def import_reference_data(self):
        """
        Wrapper around arches.app.utils.data_management.concepts.importer method.
        """
        conceptImporter(self.reference_data)

    def import_business_data(self, business_data, mapping=None):
        reporter = ResourceImportReporter(business_data)
        try:
            if mapping == None or mapping == '':
                for resource in business_data['resources']:
                    if resource['resourceinstance'] != None:

                        resourceinstance, created = ResourceInstance.objects.update_or_create(
                            resourceinstanceid = uuid.UUID(str(resource['resourceinstance']['resourceinstanceid'])),
                            graph_id = uuid.UUID(str(resource['resourceinstance']['graph_id'])),
                            legacyid = resource['resourceinstance']['legacyid']
                        )
                        if len(ResourceInstance.objects.filter(resourceinstanceid=resource['resourceinstance']['resourceinstanceid'])) == 1:
                            reporter.update_resources_saved()

                    if resource['tiles'] != []:
                        reporter.update_tiles(len(resource['tiles']))
                        for tile in resource['tiles']:
                            tile['parenttile_id'] = uuid.UUID(str(tile['parenttile_id'])) if tile['parenttile_id'] else None

                            tile, created = Tile.objects.update_or_create(
                                resourceinstance = resourceinstance,
                                parenttile = Tile(uuid.UUID(str(tile['parenttile_id']))) if tile['parenttile_id'] else None,
                                nodegroup = NodeGroup(uuid.UUID(str(tile['nodegroup_id']))) if tile['nodegroup_id'] else None,
                                tileid = uuid.UUID(str(tile['tileid'])),
                                data = tile['data']
                            )
                            if len(Tile.objects.filter(tileid=tile.tileid)) == 1:
                                reporter.update_tiles_saved()
            else:

                blanktilecache = {}
                target_nodegroup_cardinalities = {}
                for nodegroup in JSONSerializer().serializeToPython(NodeGroup.objects.all()):
                    target_nodegroup_cardinalities[nodegroup['nodegroupid']] = nodegroup['cardinality']

                def replace_source_nodeid(tiles, mapping):
                    for tile in tiles:
                        new_data = []
                        for sourcekey in tile['data'].keys():
                            for row in mapping['nodes']:
                                if row['file_field_name'] == sourcekey:
                                    d = {}
                                    d[row['arches_nodeid']] =  tile['data'][sourcekey]
                                    new_data.append(d)
                                    # tile['data'][row['targetnodeid']] = tile['data'][sourcekey]
                                    # del tile['data'][sourcekey]
                        tile['data'] = new_data
                    return tiles

                def cache(blank_tile):
                    if blank_tile.data != {}:
                        for tile in blank_tile.tiles.values():
                            if isinstance(tile, Tile):
                                for key in tile.data.keys():
                                    blanktilecache[key] = blank_tile
                    # else:
                    #     print blank_tile

                for resource in business_data['resources']:
                    reporter.update_tiles(len(resource['tiles']))
                    parenttileids = []
                    populated_tiles = []
                    resourceinstanceid = uuid.uuid4()
                    populated_nodegroups = []

                    target_resource_model = mapping['resource_model_id']

                    for tile in resource['tiles']:
                        if tile['data'] != {}:

                            def get_tiles(tile):
                                if tile['parenttile_id'] != None:
                                    if tile['parenttile_id'] not in parenttileids:
                                        parenttileids.append(tile['parenttile_id'])
                                        ret = []
                                        for sibling_tile in resource['tiles']:
                                            if sibling_tile['parenttile_id'] == tile['parenttile_id']:
                                                ret.append(sibling_tile)
                                    else:
                                        ret = None
                                else:
                                    ret = [tile]

                                #deletes nodes that don't have values
                                if ret is not None:
                                    for tile in ret:
                                        for key, value in tile['data'].iteritems():
                                            if value == "":
                                                del tile['data'][key]
                                return ret

                            def get_blank_tile(sourcetilegroup):
                                if len(sourcetilegroup[0]['data']) > 0:
                                    if sourcetilegroup[0]['data'][0] != {}:
                                        if sourcetilegroup[0]['data'][0].keys()[0] not in blanktilecache:
                                            blank_tile = Tile.get_blank_tile(tiles[0]['data'][0].keys()[0], resourceid=resourceinstanceid)
                                            cache(blank_tile)
                                        else:
                                            blank_tile = blanktilecache[tiles[0]['data'][0].keys()[0]]
                                    else:
                                        blank_tile = None
                                else:
                                    blank_tile = None
                                return blank_tile

                            tiles = get_tiles(tile)
                            if tiles is not None:
                                mapped_tiles = replace_source_nodeid(tiles, mapping)
                                blank_tile = get_blank_tile(tiles)

                                def populate_tile(sourcetilegroup, target_tile):
                                    need_new_tile = False
                                    target_tile_cardinality = target_nodegroup_cardinalities[str(target_tile.nodegroup_id)]
                                    if str(target_tile.nodegroup_id) not in populated_nodegroups:
                                        if target_tile.data != {}:
                                            for source_tile in sourcetilegroup:
                                                for tiledata in source_tile['data']:
                                                    for nodeid in tiledata.keys():
                                                        if nodeid in target_tile.data:
                                                            if target_tile.data[nodeid] == None:
                                                                target_tile.data[nodeid] = tiledata[nodeid]
                                                                for key in tiledata.keys():
                                                                    if key == nodeid:
                                                                        del tiledata[nodeid]
                                                for tiledata in source_tile['data']:
                                                    if tiledata == {}:
                                                        source_tile['data'].remove(tiledata)

                                        elif target_tile.tiles != None:
                                            populated_child_nodegroups = []
                                            for nodegroupid, childtile in target_tile.tiles.iteritems():
                                                childtile_empty = True
                                                child_tile_cardinality = target_nodegroup_cardinalities[str(childtile[0].nodegroup_id)]
                                                if str(childtile[0].nodegroup_id) not in populated_child_nodegroups:
                                                    prototype_tile = childtile.pop()
                                                    prototype_tile.tileid = None

                                                    for source_tile in sourcetilegroup:
                                                        if prototype_tile.nodegroup_id not in populated_child_nodegroups:
                                                            prototype_tile_copy = deepcopy(prototype_tile)

                                                            for data in source_tile['data']:
                                                                for nodeid in data.keys():
                                                                    if nodeid in prototype_tile.data.keys():
                                                                        if prototype_tile.data[nodeid] == None:
                                                                            prototype_tile_copy.data[nodeid] = data[nodeid]
                                                                            for key in data.keys():
                                                                                if key == nodeid:
                                                                                    del data[nodeid]
                                                                            if child_tile_cardinality == '1':
                                                                                populated_child_nodegroups.append(prototype_tile.nodegroup_id)
                                                            for data in source_tile['data']:
                                                                if data == {}:
                                                                    source_tile['data'].remove(data)

                                                            for key in prototype_tile_copy.data.keys():
                                                                if prototype_tile_copy.data[key] != None:
                                                                    childtile_empty = False
                                                            if prototype_tile_copy.data == {} or childtile_empty:
                                                                prototype_tile_copy = None
                                                            if prototype_tile_copy is not None:
                                                                childtile.append(prototype_tile_copy)
                                                        else:
                                                            break

                                        if target_tile.data:
                                            if target_tile.data == {} and target_tile.tiles == {}:
                                                target_tile = None

                                        populated_tiles.append(target_tile)

                                        for source_tile in sourcetilegroup:
                                            if source_tile['data']:
                                                for data in source_tile['data']:
                                                    if len(data) > 0:
                                                        need_new_tile = True

                                        if need_new_tile:
                                            if get_blank_tile(sourcetilegroup) != None:
                                                populate_tile(sourcetilegroup, get_blank_tile(sourcetilegroup))

                                        if target_tile_cardinality == '1':
                                            populated_nodegroups.append(str(target_tile.nodegroup_id))
                                    else:
                                        target_tile = None

                                if blank_tile != None:
                                    populate_tile(mapped_tiles, blank_tile)

                    newresourceinstance = ResourceInstance.objects.create(
                        resourceinstanceid = resourceinstanceid,
                        graph_id = target_resource_model,
                        legacyid = None
                    )
                    if len(ResourceInstance.objects.filter(resourceinstanceid=resourceinstanceid)) == 1:
                        reporter.update_resources_saved()

                    # print JSONSerializer().serialize(populated_tiles)
                    for populated_tile in populated_tiles:
                        populated_tile.resourceinstance = newresourceinstance
                        saved_tile = populated_tile.save()
                        # tile_saved = count parent tile and count of tile array if tile array != {}
                        # reporter.update_tiles_saved(tile_saved)

        except (KeyError, TypeError) as e:
            print e

        finally:
            reporter.report_results()

    def import_all(self):
        errors = []
        conceptImporter(self.reference_data)
        resource_graph_errors, resource_graph_reporter = resourceGraphImporter(self.graphs)
        resource_graph_reporter.report_results()
        errors = self.validate_business_data(self.business_data)
        if len(errors) == 0:
            if self.business_data not in ('',[]):
                self.import_business_data(self.business_data, self.mapping)
        else:
            for error in errors:
                print "{0} {1}".format(error[0], error[1])
