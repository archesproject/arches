from django.conf import settings
import csv
from django.db import connection
import unicodecsv
from datetime import datetime
from django.contrib.gis.geos import fromstr
from django.contrib.gis import geos
import decimal
import sys
import os
from arches.management.commands import utils
import time

class Row(object):
    def __init__(self, *args):
        if len(args) == 0:
            self.resource_id = ''
            self.resourcetype = ''
            self.attributename = ''
            self.attributevalue = ''
            self.group_id = ''
        elif isinstance(args[0], dict):
            details = args[0]
            self.resource_id = details['RESOURCEID'].strip()
            self.resourcetype = details['RESOURCETYPE'].strip()
            self.attributename = details['ATTRIBUTENAME'].strip()
            self.attributevalue = details['ATTRIBUTEVALUE'].strip().replace('\\n', '\n')
            self.group_id = details['GROUPID'].strip()

    def __repr__(self):
        return ('"%s, %s, %s, %s"') % (self.resource_id, self. resourcetype, self. attributename, self.attributevalue)

class Group(object):
    def __init__(self, *args):
        if len(args) == 0:
            self.resource_id = ''
            self.group_id = ''
            self.rows = []
        elif isinstance(args[0], dict):
            details = args[0]
            self.resource_id = details['RESOURCEID'].strip()
            self.group_id = details['GROUPID'].strip()
            self.rows = []   

class Resource(object):
    def __init__(self, *args):

        if len(args) == 0:
            self.resource_id = ''
            self.entitytypeid = ''
            self.groups = []

        elif isinstance(args[0], dict):
            details = args[0]
            self.entitytypeid = details['RESOURCETYPE'].strip()
            self.resource_id = details['RESOURCEID'].strip()
            self.groups = []

    def appendrow(self, row, group_id=None):
        if group_id != None:
            for group in self.groups:
                if group.group_id == group_id:
                    group.rows.append(row)

    def __str__(self):
        return '{0},{1}'.format(self.resource_id, self.entitytypeid)

class Validation_Errors(object):
    def __init__(self, *args):
        self.syntax_errors = []
        self.entitytype_errors = []
        self.businesstable_error = []
        self.domain_errors = []
        self.date_errors = []
        self.geometry_errors = []
        self.filepath_errors = []
        self.number_errors = []
        self.contiguousness_errors = []
        self.relations_errors = []

class Validator(object):
    def __init__(self, *args):
        self.resource_attributes = self.get_resource_attributes() # {resource1:{entitype:businesstable, entitytype:businesstable}, resource2:{entitype:businesstable, entitytype:businesstable}...}
        self.domain_values = self.get_domain_values()
        self.complete_resources = {}
        self.previous_resourceid = ''
        self.contiguous_errors = []
        self.current_group = {}
        self.group_errors = []
        self.unique_resourceids = set()
        self.errors = []

        self.validation_errors = Validation_Errors()

    def get_resource_attributes(self):
        cursor = connection.cursor()
        sql = """
            SELECT m.entitytypeidfrom, m.entitytypeidto, et.businesstablename FROM ontology.mappings m
            JOIN data.entity_types et ON et.entitytypeid = m.entitytypeidto
        """
        cursor.execute(sql)
        resource_types = []
        resource_dict = {}
        for val in cursor.fetchall():
            if val[0] in resource_dict:
                resource_dict[val[0]][val[1]] = val[2]
            else:
                resource_dict[val[0]] = {val[1] : val[2]}

        return resource_dict

    def get_domain_values(self):
        cursor = connection.cursor()
        sql = """
            SELECT DISTINCT(legacyoid) FROM concepts.concepts
        """
        cursor.execute(sql)
        domain_vals = []
        for val in cursor.fetchall():
            domain_vals.append(val[0])

        return domain_vals

    def validate_contiguousness(self, row, rownum):
        if row['RESOURCEID'] not in self.complete_resources:
            self.complete_resources[row['RESOURCEID']] = False
        else:
            if self.complete_resources[row['RESOURCEID']] != False and row['RESOURCEID'] not in self.contiguous_errors:
                self.append_error('ERROR ROW: {0} - {1} has noncontiguous attributes.'.format(rownum, row['RESOURCEID']), 'contiguousness_errors')
                self.contiguous_errors.append(row['RESOURCEID'])

        if self.previous_resourceid != row['RESOURCEID']:
            self.complete_resources[self.previous_resourceid] = True

        self.previous_resourceid = row['RESOURCEID']

    def validate_row_syntax(self, row, rownum):
        # property for row num, also value for missing property row['MISSING'] same for additional
        if 'MISSING' in row.values():
            self.append_error('row missing value', 'syntax_errors')

        if 'ADDITIONAL' in row.values():
            self.append_error('additional values present in row', 'syntax_errors')

    def validate_entitytype(self, row, rownum):
        if row['RESOURCETYPE'] in self.resource_attributes:
            if row['ATTRIBUTENAME'] in self.resource_attributes[row['RESOURCETYPE']]:
                pass
            else:
                self.append_error('{0} not a valid entity type for {1} resource.'.format(row['ATTRIBUTENAME'], row['RESOURCETYPE']), 'entitytype_errors')
        else:
            self.append_error('{0} is not a valid resource type.'.format(row['RESOURCETYPE']), 'entitytype_errors')


    def valdiate_attribute_value(self, row, rownum):
        entity_type = row['ATTRIBUTENAME']
        resource_type = row['RESOURCETYPE']
        business_table = self.get_businesstable(resource_type, entity_type)

        if business_table not in ['strings', 'dates', 'domains', 'files', 'geometries', 'numbers']:
            self.append_error('{0} is not a valid business table name.'.format(business_table), 'businesstable_error')
        else:
            if business_table == 'domains':
                self.validate_domains(row, rownum)

            elif business_table == 'dates':
                self.validate_dates(row, rownum)

            elif business_table == 'geometries':
                self.validate_geometries(row, rownum)

            # DO NOT DELETE: Uncomment this when we have acual file paths to test against.
            # elif business_table == 'files':
            #     self.validate_files(row, rownum)

            elif business_table == 'numbers':
                self.validate_numbers(row, rownum)


    def validate_domains(self, row, rownum):
        if row['ATTRIBUTEVALUE'] not in self.domain_values:
            self.append_error('ERROR ROW:{0} - {1} is not a valid domain value. Check authority document related to {2}'.format(rownum, row['ATTRIBUTEVALUE'], row['ATTRIBUTENAME']), 'domain_errors')

    def validate_dates(self, row, rownum):
        date_formats = settings.DATE_PARSING_FORMAT
        valid = False
        for format in date_formats:
            if valid == False: 
                try:
                    if datetime.strptime(row['ATTRIBUTEVALUE'], format):
                        valid = True
                except:
                    valid = False
        if valid == False:
            self.append_error('ERROR ROW: {0} - {1} is not a properly formatted date. Dates must be in {2}, or {3} format.'.format(rownum, row['ATTRIBUTEVALUE'], (',').join(date_formats[:-1]), date_formats[-1]), 'date_errors')

    def validate_geometries(self, row, rownum):
        try:
            geom = fromstr(row['ATTRIBUTEVALUE'])
            coord_limit = 1500
            bbox = geos.Polygon(settings.DATA_VALIDATION_BBOX)

            if geom.num_coords > coord_limit:
                self.append_error('ERROR ROW: {0} - {1} has too many coordinates ({2}), Please limit to less then {3} coordinates of 5 digits of precision or less.'.format(rownum, row['ATTRIBUTEVALUE'][:75] + '......', geom.num_coords, coord_limit), 'geometry_errors')

            # if fromstr(row['ATTRIBUTEVALUE']).valid == False:
            #     self.append_error('ERROR ROW: {0} - {1} is an invalid geometry.'.format(rownum, row['ATTRIBUTEVALUE']), 'geometry_errors')

            if bbox.contains(geom) == False:
                self.append_error('ERROR ROW: {0} - {1} does not fall within the bounding box of the selected coordinate system. Adjust your coordinates or your settings.DATA_EXTENT_VALIDATION property.'.format(rownum, row['ATTRIBUTEVALUE']), 'geometry_errors')
            
        except:
            self.append_error('ERROR ROW: {0} - {1} is not a properly formatted geometry.'.format(rownum, row['ATTRIBUTEVALUE']), 'geometry_errors')

    def validate_numbers(self, row, rownum):
        try:
            decimal.Decimal(row['ATTRIBUTEVALUE'])
        except:
            self.append_error('ERROR ROW: {0} - {1} is not a properly formatted number.'.format(rownum, row['ATTRIBUTEVALUE']), 'number_errors')

    def validate_files(self, row, rownum):
        """
        This method will have to be changed to include prefix for file directory.
        """
        if os.path.isfile(row['ATTRIBUTEVALUE']):
                pass
        else:
            self.append_error('ERROR ROW: {0} - {1} file either does not exist at location or is not readable.'.format(rownum, row['ATTRIBUTEVALUE']), 'filepath_errors')

    def validate_relations_file(self, arches_file):
        unique_relationids = set()
        relations_file = arches_file.replace('.arches', '.relations')
        with open(relations_file, 'rU') as f:
            fieldnames = ['RESOURCEID_FROM','RESOURCEID_TO','START_DATE','END_DATE','RELATION_TYPE','NOTES']
            rows = unicodecsv.DictReader(f, fieldnames=fieldnames, 
                encoding='utf-8-sig', delimiter='|', restkey='ADDITIONAL', restval='MISSING')
            rows.next()
            rownum = 2
            for row in rows:
                self.validate_row_syntax(row, rownum)
                unique_relationids.add(row['RESOURCEID_FROM'])
                unique_relationids.add(row['RESOURCEID_TO'])
                rownum += 1

        for resourceid in unique_relationids - self.unique_resourceids:
            self.append_error('"{0}" is present in {1} but not {2}. Both resourceids must be present in {3} in order to create a valid relation.'.format(resourceid, relations_file.split('/')[-1], arches_file.split('/')[-1], arches_file.split('/')[-1]), 'relations_errors')

    def get_businesstable(self, resource, attributename):
        try:
            return self.resource_attributes[resource][attributename]
        except:
            self.append_error('No business table for {0} in {1}. Check if attributename is valid and that business table name is populated for {2} in {3}.'.format(attributename, resource, attributename, resource), 'businesstable_error')

    def append_error(self, text, error_type):
        error_type_list = getattr(self.validation_errors, error_type)
        error_type_list.append(text)

class ArchesReader():

    def validate_file(self, arches_file, break_on_error=True):
        """
        Creates row dictionaries from a csv file

        """
        validator = Validator()
        with open(arches_file, 'rU') as f:
            fieldnames = ['RESOURCEID','RESOURCETYPE','ATTRIBUTENAME','ATTRIBUTEVALUE','GROUPID']
            rows = unicodecsv.DictReader(f, fieldnames=fieldnames, 
                encoding='utf-8-sig', delimiter='|', restkey='ADDITIONAL', restval='MISSING')
            rows.next() # skip header row
            rownum = 2
            start_time = time.time()
            for row in rows:
                validator.validate_row_syntax(row, rownum)
                validator.validate_entitytype(row, rownum)
                validator.valdiate_attribute_value(row, rownum)
                validator.validate_contiguousness(row, rownum)

                validator.unique_resourceids.add(row['RESOURCEID'])
                rownum += 1
        validator.validate_relations_file(arches_file)
        duration = time.time() - start_time

        sorted_errors = []
        attr_length = len(validator.validation_errors.__dict__)
        for attr, value in validator.validation_errors.__dict__.iteritems():
            if value != []:
                sorted_errors.extend(value)
                sorted_errors.append('\n\n\n\n')
        if len(sorted_errors) > 1:
            del sorted_errors[-1]

        print 'Validation of your Arches file took: {0} seconds.'.format(str(duration))
        if len(sorted_errors) > 0:
            utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'validation_errors.txt'), '\n'.join(sorted_errors))
            print "\n\nERROR: There were errors detected in your arches file."
            print "Please review the errors at %s, \ncorrect the errors and then rerun this script." % (os.path.join(settings.PACKAGE_ROOT, 'logs', 'validation_errors.txt'))
            if break_on_error:
                sys.exit(101)

    def load_file(self, arches_file):
        '''Reads an arches data file and creates resource graphs'''
        resource_list = []
        resource_id = ''
        group_id = ''
        resource = ''

        resource_info = csv.DictReader(open(arches_file, 'r'), delimiter='|')

        # Import package specific validation module.
        fully_qualified_modulename = settings.PACKAGE_VALIDATOR
        components = fully_qualified_modulename.split('.')
        classname = components[len(components)-1]
        modulename = ('.').join(components[0:len(components)])
        validation_module = __import__(modulename, globals(), locals(), [classname], -1)
        start_time = time.time()

        for row in resource_info:
            # print row
            
            group_val = row['GROUPID'].strip()
            resource_type_val = row['RESOURCETYPE'].strip()
            resource_id_val = row['RESOURCEID'].strip()

            if (settings.LIMIT_ENTITY_TYPES_TO_LOAD == None or resource_type_val in settings.LIMIT_ENTITY_TYPES_TO_LOAD):
                if resource_id_val != resource_id:
                    if resource != '':
                        validation_module.validate_resource(resource)
                    resource = Resource(row)
                    resource_list.append(resource)
                    resource_id = resource_id_val
                    group_id = ''
                
                if group_val != group_id:  #create a new group of resouces
                    resource.groups.append(Group(row))
                    group_id = group_val

                if group_val == group_id:
                    resource.appendrow(Row(row), group_id=group_id)

        validation_module.validate_resource(resource)

        sorted_errors = []
        attr_length = len(validation_module.validation_errors.__dict__)
        for attr, value in validation_module.validation_errors.__dict__.iteritems():
            if value != []:
                sorted_errors.extend(value)
                sorted_errors.append('\n\n\n\n')
        if len(sorted_errors) > 1:
            del sorted_errors[-1]
        duration = time.time() - start_time
        print 'Validation of your business data took: {0} seconds.'.format(str(duration))
        if len(sorted_errors) > 0:
            utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'validation_errors.txt'), '\n'.join(sorted_errors))
            print "\n\nERROR: There were errors detected in your business data."
            print "Please review the errors at %s, \ncorrect the errors and then rerun this script." % (os.path.join(settings.PACKAGE_ROOT, 'logs', 'validation_errors.txt'))
            break_on_error = True
            if break_on_error:
                sys.exit(101)

        return resource_list