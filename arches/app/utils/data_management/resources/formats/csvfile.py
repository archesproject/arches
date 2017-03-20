import csv
import codecs
import cPickle
import datetime
import json
import os
import sys
import uuid
import distutils.util
import traceback
from copy import deepcopy
from mimetypes import MimeTypes
from os.path import isfile, join
from format import Writer
from format import Reader
from format import ResourceImportReporter
from arches.app.models.tile import Tile
from arches.app.models.concept import Concept
from arches.app.models.models import Node, Value
from arches.app.models.models import File
from arches.app.models.models import Node
from arches.app.models.models import NodeGroup
from arches.app.models.resource import Resource
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.betterJSONSerializer import JSONSerializer
from django.db import connection
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, GeometryCollection
from django.http import HttpRequest
from django.core.files import File as DjangoFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import ugettext as _

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class CsvWriter(Writer):

    def __init__(self):
        super(CsvWriter, self).__init__()
        self.datatype_factory = DataTypeFactory()
        self.node_datatypes = {str(nodeid): datatype for nodeid, datatype in  Node.objects.values_list('nodeid', 'datatype').filter(~Q(datatype='semantic'), graph__isresource=True)}

    def transform_value_for_export(self, datatype, value, concept_export_value_type):
        datatype_instance = self.datatype_factory.get_instance(datatype)
        value = datatype_instance.transform_export_values(value, concept_export_value_type=concept_export_value_type)
        return value

    def write_resources(self, resources, resource_export_configs=None):
        csv_records = []
        other_group_records = []
        mapping = {}
        concept_export_value_lookup = {}
        for resource_export_config in resource_export_configs:
            for node in resource_export_config['nodes']:
                if node['file_field_name'] != '':
                    mapping[node['arches_nodeid']] = node['file_field_name']
                if 'concept_export_value' in node:
                    concept_export_value_lookup[node['arches_nodeid']] = node['concept_export_value']
        csv_header = ['ResourceID'] + mapping.values()
        csvs_for_export = []

        for resource in resources:
            csv_record = {}
            other_group_record = {}
            resourceid = resource['_source']['resourceinstanceid']
            resource_graphid = resource['_source']['graph_id']
            legacyid = resource['_source']['legacyid']
            csv_record['ResourceID'] = resourceid
            other_group_record['ResourceID'] = resourceid

            for tile in resource['_source']['tiles']:
                if tile['data'] != {}:
                    for k in tile['data'].keys():
                            if tile['data'][k] != '' and k in mapping:
                                if mapping[k] not in csv_record:
                                    concept_export_value_type = None
                                    if k in concept_export_value_lookup:
                                        concept_export_value_type = concept_export_value_lookup[k]
                                    value = self.transform_value_for_export(self.node_datatypes[k], tile['data'][k], concept_export_value_type)
                                    csv_record[mapping[k]] = value
                                    del tile['data'][k]
                                else:
                                    value = self.transform_value_for_export(self.node_datatypes[k], tile['data'][k], concept_export_value_type)
                                    other_group_record[mapping[k]] = value
                            else:
                                del tile['data'][k]

            csv_records.append(csv_record)
            if other_group_record != {}:
                other_group_records.append(other_group_record)


        csv_name_prefix = resource_export_configs[0]['resource_model_name']
        iso_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        csv_name = os.path.join('{0}_{1}.{2}'.format(csv_name_prefix, iso_date, 'csv'))
        dest = StringIO()
        csvwriter = csv.DictWriter(dest, delimiter=',', fieldnames=csv_header)
        csvwriter.writeheader()
        csvs_for_export.append({'name':csv_name, 'outputfile': dest})
        for csv_record in csv_records:
            csvwriter.writerow({k:str(v) for k,v in csv_record.items()})

        dest = StringIO()
        csvwriter = csv.DictWriter(dest, delimiter=',', fieldnames=csv_header)
        csvwriter.writeheader()
        csvs_for_export.append({'name':csv_name + '_groups', 'outputfile': dest})
        for csv_record in other_group_records:
            csvwriter.writerow({k:str(v) for k,v in csv_record.items()})

        return csvs_for_export

class CsvReader(Reader):

    def save_resource(self, populated_tiles, resourceinstanceid, legacyid, resources, target_resource_model, bulk, save_count):
        # create a resource instance only if there are populated_tiles
        errors = []
        if len(populated_tiles) > 0:
            newresourceinstance = Resource(
                resourceinstanceid=resourceinstanceid,
                graph_id=target_resource_model,
                legacyid=legacyid,
                createdtime=datetime.datetime.now()
            )
            # add the tiles to the resource instance
            newresourceinstance.tiles = populated_tiles
            # if bulk saving then append the resources to a list otherwise just save the resource
            if bulk:
                resources.append(newresourceinstance)
                if len(resources) == settings.BULK_IMPORT_BATCH_SIZE:
                    Resource.bulk_save(resources=resources)
                    del resources[:]  #clear out the array
            else:
                newresourceinstance.save()
        else:
            errors.append({'type': 'WARNING', 'message': 'No resource created for legacyid: {0}. Make sure there is data to be imported for this resource and it is mapped properly in your mapping file.'.format(legacyid)})
            if len(errors) > 0:
                self.errors += errors


        if save_count % (settings.BULK_IMPORT_BATCH_SIZE/4) == 0:
            print '%s resources processed' % str(save_count)


    def import_business_data(self, business_data=None, mapping=None, overwrite='append', bulk=False):
        # errors = businessDataValidator(self.business_data)

        def process_resourceid(resourceid, overwrite):
            # Test if resourceid is a UUID.
            try:
                resourceinstanceid = uuid.UUID(resourceid)
                # If resourceid is a UUID check if it is already an arches resource.
                try:
                    ret = Resource.objects.filter(resourceinstanceid=resourceid)
                    # If resourceid is an arches resource and overwrite is true, delete the existing arches resource.
                    if overwrite == 'overwrite':
                        Resource(str(ret[0].resourceinstanceid)).delete()
                    resourceinstanceid = resourceinstanceid
                # If resourceid is not a UUID create one.
                except:
                    resourceinstanceid = resourceinstanceid
            except:
                # Get resources with the given legacyid
                ret = Resource.objects.filter(legacyid=resourceid)
                # If more than one resource is returned than make resource = None. This should never actually happen.
                if len(ret) > 1:
                    resourceinstanceid = None
                # If no resource is returned with the given legacyid then create an archesid for the resource.
                elif len(ret) == 0:
                    resourceinstanceid = uuid.uuid4()
                # If a resource is returned with the give legacyid then return its archesid
                else:
                    if overwrite == 'overwrite':
                        Resource(str(ret[0].resourceinstanceid)).delete()
                    resourceinstanceid = ret[0].resourceinstanceid

            return resourceinstanceid

        try:
            with transaction.atomic():
                save_count = 0
                try:
                    resourceinstanceid = process_resourceid(business_data[0]['ResourceID'], overwrite)
                except KeyError:
                    print '*'*80
                    print 'ERROR: No column \'ResourceID\' found in business data file. Please add a \'ResourceID\' column with a unique resource identifier.'
                    print '*'*80
                    sys.exit()
                blanktilecache = {}
                populated_nodegroups = {}
                populated_nodegroups[resourceinstanceid] = []
                previous_row_resourceid = None
                populated_tiles = []
                single_cardinality_nodegroups = [str(nodegroupid) for nodegroupid in NodeGroup.objects.values_list('nodegroupid', flat=True).filter(cardinality = '1')]
                node_datatypes = {str(nodeid): datatype for nodeid, datatype in  Node.objects.values_list('nodeid', 'datatype').filter(~Q(datatype='semantic'), graph__isresource=True)}
                all_nodes = Node.objects.all()
                datatype_factory = DataTypeFactory()

                # This code can probably be moved into it's own module.
                resourceids = []
                non_contiguous_resource_ids = []
                previous_row_for_validation = None

                for row_number, row in enumerate(business_data):
                    # Check contiguousness of csv file.
                    if row['ResourceID'] != previous_row_for_validation and row['ResourceID'] in resourceids:
                        non_contiguous_resource_ids.append(row['ResourceID'])
                    else:
                        resourceids.append(row['ResourceID'])
                    previous_row_for_validation = row['ResourceID']

                if len(non_contiguous_resource_ids) > 0:
                    print '*'*80
                    print 'ERROR: Resources in your csv file are non-contiguous. Please sort your csv file by ResourceID and try import again.'
                    print '*'*80
                    sys.exit()

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

                def column_names_to_targetids(row, mapping, row_number):
                    errors = []
                    new_row = []
                    if 'ADDITIONAL' in row or 'MISSING' in row:
                        errors.append({'type': 'WARNING', 'message': 'No resource created for ResourceID {0}. Line {1} has additional or missing columns.'.format(row['ResourceID'], str(int(row_number.split('on line ')[1])))})
                        if len(errors) > 0:
                            self.errors += errors
                    for key, value in row.iteritems():
                        if value != '':
                            for row in mapping['nodes']:
                                if key.upper() == row['file_field_name'].upper():
                                    new_row.append({row['arches_nodeid']: value})
                    return new_row

                def transform_value(datatype, value, source):
                    '''
                    Transforms values from probably string/wkt representation to specified datatype in arches.
                    This code could probably move to somehwere where it can be accessed by other importers.
                    '''
                    request = ''
                    if datatype != '':
                        errors = []
                        datatype_instance = datatype_factory.get_instance(datatype)
                        try:
                            value = datatype_instance.transform_import_values(value)
                            errors = datatype_instance.validate(value, source)
                        except Exception as e:
                            errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}'.format(datatype_instance.datatype_model.classname, value, source, e)})
                            if len(errors) > 0:
                                self.errors += errors
                    else:
                        print _('No datatype detected for {0}'.format(value))

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
                resources = []

                for row_number, row in enumerate(business_data):
                    row_number = 'on line ' + unicode(row_number + 2) #to represent the row in a csv accounting for the header and 0 index
                    if row['ResourceID'] != previous_row_resourceid and previous_row_resourceid is not None:

                        save_count = save_count + 1
                        self.save_resource(populated_tiles, resourceinstanceid, legacyid, resources, target_resource_model, bulk, save_count)

                        # reset values for next resource instance
                        populated_tiles = []
                        resourceinstanceid = process_resourceid(row['ResourceID'], overwrite)
                        populated_nodegroups[resourceinstanceid] = []

                    source_data = column_names_to_targetids(row, mapping, row_number)

                    if len(source_data) > 0:
                        if source_data[0].keys():
                            try:
                                target_resource_model = all_nodes.get(nodeid=source_data[0].keys()[0]).graph_id
                            except:
                                print '*'*80
                                print 'ERROR: No resource model found. Please make sure the resource model this business data is mapped to has been imported into Arches.'
                                print '*'*80
                                sys.exit()

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
                                                    if target_tile.data[source_key] == None:
                                                        # If match populate target_tile node with transformed value.
                                                        value = transform_value(node_datatypes[source_key], source_tile[source_key], row_number)
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
                                        if str(prototype_tile.nodegroup_id) in single_cardinality_nodegroups:
                                            child_tile_cardinality = '1'
                                        else:
                                            child_tile_cardinality = 'n'

                                        def populate_child_tiles(source_data):
                                            prototype_tile_copy = cPickle.loads(cPickle.dumps(prototype_tile, -1))
                                            prototype_tile_copy.tileid = uuid.uuid4()
                                            prototype_tile_copy.parenttile = target_tile
                                            prototype_tile_copy.resourceinstance_id = resourceinstanceid
                                            if str(prototype_tile_copy.nodegroup_id) not in populated_child_nodegroups:
                                                for target_key in prototype_tile_copy.data.keys():
                                                    for source_column in source_data:
                                                        for source_key in source_column.keys():
                                                            if source_key == target_key:
                                                                if prototype_tile_copy.data[source_key] == None:
                                                                    value = transform_value(node_datatypes[source_key], source_column[source_key], row_number)
                                                                    prototype_tile_copy.data[source_key] = value['value']
                                                                    # target_tile.request = value['request']
                                                                    del source_column[source_key]
                                                                else:
                                                                    populate_child_tiles(source_data)


                                            if prototype_tile_copy.data != {}:
                                                if len([item for item in prototype_tile_copy.data.values() if item != None]) > 0:
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
                    legacyid = row['ResourceID']

                if 'legacyid' in locals():
                    self.save_resource(populated_tiles, resourceinstanceid, legacyid, resources, target_resource_model, bulk, save_count)

                if bulk:
                    Resource.bulk_save(resources=resources)
                    print _('%s total resource saved' % (save_count + 1))

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            formatted = traceback.format_exception(exc_type, exc_value, exc_traceback)
            if len(formatted):
                for message in formatted:
                    print message

        finally:
            pass
