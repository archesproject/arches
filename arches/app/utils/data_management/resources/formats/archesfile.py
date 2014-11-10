from django.conf import settings
import csv

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
            self.nongroups = []

        elif isinstance(args[0], dict):
            details = args[0]
            self.entitytypeid = details['RESOURCETYPE'].strip()
            self.resource_id = details['RESOURCEID'].strip()
            self.nongroups = []  
            self.groups = []


    def appendrow(self, row, group_id=None):
        if group_id != None:
            for group in self.groups:
                if group.group_id == group_id:
                    group.rows.append(row)
        else:
           self.nongroups.append(row)

    def __str__(self):
        return '{0},{1}'.format(self.resource_id, self.entitytypeid)


class ArchesReader():

    def load_file(self, arches_file):
        '''Reads an arches data file and creates resource graphs'''
        resource_list = []
        resource_id = ''
        group_id = ''

        resource_info = csv.DictReader(open(arches_file, 'r'), delimiter='|')

        for row in resource_info:
            
            group_val = row['GROUPID'].strip()
            resource_type_val = row['RESOURCETYPE'].strip()
            resource_id_val = row['RESOURCEID'].strip()

            if (settings.LIMIT_ENTITY_TYPES_TO_LOAD == None or resource_type_val in settings.LIMIT_ENTITY_TYPES_TO_LOAD):
                if resource_id_val != resource_id:
                    resource = Resource(row)
                    resource_list.append(resource)
                    resource_id = resource_id_val
                
                if group_val != '-1' and group_val != group_id:  #create a new group of resouces
                    resource.groups.append(Group(row))
                    group_id = group_val

                if group_val == group_id:
                    resource.appendrow(Row(row), group_id=group_id)

                if group_val == '-1':
                    resource.appendrow(Row(row))

        return resource_list