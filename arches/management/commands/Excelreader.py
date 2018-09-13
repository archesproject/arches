from __future__ import division
import os
import re
import csv
import datetime
from django.conf import settings
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError 
from openpyxl import load_workbook
from openpyxl import Workbook
import arches.app.models.models as archesmodels
from arches.management.commands import utils
from django.contrib.gis.geos import GEOSGeometry
import json

class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('-o', '--operation', action='store', dest='operation', default='site_dataset',type='choice', choices=['bibliography','site_dataset','validate','write_arches_files'],help='Operation Type; ' + '\'bibliography\'=Reads a bibliographic XLSX and converts it to arches import file' + '\'site_dataset\'=Reads a site gazetteer XLSX and converts it to arches import file'),
        make_option('-s', '--source', action='store', dest='source', default='',help='Directory containing the XLSX file you need to convert to .arches'),
        make_option('-m', '--mapping', action='store', dest='mapping_file', default='',help='Directory containing a .csv mapping file'),        
        make_option('-d', '--dest_dir', action='store', dest='dest_dir',help='Directory, comprinsing of file name, where you want to save the .arches file'),
        make_option('-r', '--res_type', action='store', dest='resource_type', default='HERITAGE_RESOURCE_GROUP.E27', help='What kind of resource the source file contains e.g. HERITAGE_RESOURCE_GROUP.E27'),
        make_option('-a', '--append', action='store_true', dest='append_data', default=False, help='This flag indicates that the XLSX file contains data to append'),
        make_option('--validation_type',help='choose which type of validation to run')
    )
    
    def handle(self, *args, **options):
        
        print 'operation: '+ options['operation']
        if options['operation'] == 'validate':
            print '  suboperation: '+options['validation_type']
        package_name = settings.PACKAGE_NAME
        print 'package: '+ package_name
        start = datetime.datetime.now()

        workbook = load_workbook(options['source'], data_only=True)

        filelist = []
        if options['operation'] == 'validate':
            try:
                vtype = options['validation_type']
                fname = os.path.splitext(os.path.basename(options['dest_dir']))[0]
                error_path = os.path.join(settings.BULK_UPLOAD_DIR,
                    "{}_validation_errors-{}.json".format(fname,vtype)
                )

                if vtype == 'headers':
                    result = self.validate_headers(workbook, skip_resourceid_col=options['append_data'])
                    
                elif vtype == 'rows_and_values':
                    result = self.validate_rows_and_values(workbook)
                    
                elif vtype == 'dates':
                    data = self.get_values(workbook,datatype="dates")
                    values = self.flatten_values(data)
                    result = self.validatedates(values)

                elif vtype == 'geometries':
                    data = self.get_values(workbook,datatype="geomtries")
                    values = self.flatten_values(data)
                    result = self.validate_geometries(values)
                    
                elif vtype == 'concepts':
                    data = self.get_values(workbook,datatype="domains")
                    result = self.validate_concepts(data)
                    
                elif vtype == 'files':
                    data = self.get_values(workbook,datatype="files")
                    values = self.flatten_values(data)
                    result, filelist = self.validate_files(values)
                    
                elif vtype == 'write_arches_file':
                    result = {'success':True,'errors':[]}
                    try:
                        self.write_arches_file(workbook,options['resource_type'], options['dest_dir'],options['append_data'])
                    except Exception as e:
                        result['success'] = False
                        result['errors'].append('error writing .arches file: '+repr(e))
            except Exception as e:
                print repr(e)
            with open(error_path,'w') as out:
                json.dump(result,out)

        ## DEPRECATED sept 13 2018
        if options['operation'] == 'site_dataset':
            result, filelist = self.SiteDataset(options['source'], options['resource_type'], options['dest_dir'],options['append_data'])

        if filelist:
            self.stdout.write("Has attachments")
        
        print "elapsed time:",datetime.datetime.now()-start
        return
        
    def validatedates(self,date_tuples):
        '''wraps the existing date validation, only returns validation errors,
        no transformed date objects'''
        
        result = {'success':True,'errors':[]}
        for dt in date_tuples:
            validated = self.validatedate(dt[0])
            if not self.validatedate(dt[0]):
                msg = "{}: {} ({} > row {}, col {})".format(
                    dt[2],dt[0],dt[1],dt[3],dt[4]
                )
                result['errors'].append(msg)
        if result['errors']:
            result['success'] = False
        return result

    def validatedate(self, date, header = None, row_no = None):
        
        valid_formats = [
            '%Y-%m-%d', #Checks for format  YYYY-MM-DD
            '%Y-%m-%d %X', #Checks for format  YYYY-MM-DD hh:mm:ss (locale)
            '%d-%m-%Y', #Checks for format  DD-MM-YYYY
            '%d/%m/%Y', #Checks for format  DD/MM/YYYY
            '%d/%m/%y', #Checks for format  DD/MM/YY
        ]
        
        ## check all valid full date formats
        for d_format in valid_formats:
            try:
                d = datetime.datetime.strptime(date, d_format)
                result = d.date()
                break
            except ValueError:
                result = None

        ## final attempt for just year format
        if not result:
            try:
                d = datetime.datetime.strptime(date,'%Y') #Checks for format  YYYY
                isodate = d.isoformat()
                d = isodate.strip().split("T")[0]
                result = d.date()
            except:
                result = None

        return result

    def validate_rows_and_values(self,workbook):
        '''Validates that the number of semicolon-separated values is consistent
        across a worksheet and spots empty cells'''
        result = {'success':True,'errors':[]}
        sheet_count = len(workbook.worksheets)
        rows_count  = 0
        ret = []
        offset_max = False

        for sheet_index,sheet in enumerate(workbook.worksheets):
            last_row = list(sheet.rows)[sheet.max_row-1]
            if last_row[0].value is None: #this if cluase is to exclude rows with None values from the row count across worksheets
                max_row = sheet.max_row - 1
            else:
                max_row = sheet.max_row
            rows_count = rows_count + max_row

            ret = self.validate_value_number(sheet, workbook.sheetnames[sheet_index])
            if ret:
                ret = sorted(ret)
                result['errors'].append("Error: cells in sheet %s do not contain an equal number of \"|\" separated values or are empty. Errors are at the following lines: %s" % (workbook.sheetnames[sheet_index], sorted(ret)))
        if (rows_count/sheet_count).is_integer() is not True:
            result['errors'].append("Error: some sheets in your XLSX file have a different number of rows")

        if result['errors']:
            result['success'] = False
        return result
            
    def validate_value_number(self, sheet, sheet_name):
        FaultyRows=[]
        for row_index, row in enumerate(sheet.iter_rows(row_offset = 1)):
            values_no = []
            if any(cell.value for cell in row):
                for cell in row:
                    if cell.value is not None:
                        if sheet_name !='NOT': #In the NOT tab, cells in a row are not part of the same merge group, so the number of semicolon separated values need not be equal
                            value_encoded = (unicode(cell.value)).encode('utf-8')
                            cell_no = len(value_encoded.split("|"))
                            values_no.append(cell_no)
                    else:
                        values_no.append(0)
            try: 
                if values_no.count(values_no[0]) != len(values_no) or 0 in values_no:
                    FaultyRows.append(row_index+2) 
            except:
                pass
                        
        return list(set(FaultyRows))       

    def validate_headers(self, workbook, skip_resourceid_col = False):
        result = {'success':True,'errors':[]}
        for sheet in workbook.worksheets:
            for header in sheet.iter_cols(max_row = 1):
                if header[0].value is not None:
                    if skip_resourceid_col == True and header[0].value =='RESOURCEID':
                        pass
                    else:
                        try:
                            modelinstance = archesmodels.EntityTypes.objects.get(pk = header[0].value)
                            # print modelinstance
                        except archesmodels.EntityTypes.DoesNotExist:
                            print "exception!"
                            result['errors'].append("The header %s is not a valid EAMENA node name" % header[0].value)
#                             logger.error("The header %s is not a valid EAMENA node name" % header[0].value)
                            # raise ObjectDoesNotExist("The header %s is not a valid EAMENA node name" % header[0].value)
        if result['errors']:
            result['success'] = False
        return result
        
    
    def validate_concepts(self,concept_data):
    
        result = {'success':True,'errors':[]}
        for sheet_name,contents in concept_data.iteritems():

            for node_name, concept_tuples in contents.iteritems():
                node_obj = archesmodels.EntityTypes.objects.get(pk=node_name)
                all_concepts = self.collect_concepts(node_obj.conceptid_id,full_concept_list=[])
                all_labels = []
                for c in all_concepts:
                    labels = archesmodels.Values.objects.filter(conceptid_id=c)
                    for label in labels:
                        ## label.lower() allows for case-agnostic matching
                        all_labels.append(label.value.lower())

                for ct in concept_tuples:
                    if ct[0] == "x":
                        continue
                    #Values could be in Arabic or contain unicode chars, so it is essential to encode them properly.
                    value_encoded = (unicode(ct[0])).encode('utf-8')
                    for concept in value_encoded.split('|'):
                        concept = concept.rstrip().lstrip()
                        ## concept.lower() allows for case-agnostic matching
                        if not concept.lower() in all_labels:
                            msg = "{}: {} ({} > row {}, col {})".format(
                                node_name,concept,sheet_name,ct[1],ct[2]
                            )
                            result['errors'].append(msg)

        if result['errors']:
            result['success'] = False
        return result

    def collect_concepts(self, node_conceptid, full_concept_list = []):
        ''' Collects a full list of child concepts given the conceptid of the node. Returns a list of a set of concepts, i.e. expounding the duplicates'''
        concepts_in_node = archesmodels.ConceptRelations.objects.filter(conceptidfrom = node_conceptid)
        # print len(concepts_in_node)
        if concepts_in_node.count() > 0:
            full_concept_list.append(node_conceptid) 
            for concept_in_node in concepts_in_node:
                
                self.collect_concepts(concept_in_node.conceptidto_id, full_concept_list)
        else:
            full_concept_list.append(node_conceptid)
        return list(set(full_concept_list)) 

    def validate_geometries(self,geom_tuples):
        '''wraps the existing geom validation, returns errors'''
        
        result = {'success':True,'errors':[]}
        for gt in geom_tuples:
            validated = self.validate_geometry(gt[0])
            if not validated:
                msg = "{}: {} ({} > row {}, col {})".format(
                    gt[2],gt[0],gt[1],gt[3],gt[4]
                )
                result['errors'].append(msg)

        if result['errors']:
            result['success'] = False
        return result
        
    def validate_geometry(self, geometry,header,row):
        try:
            GEOSGeometry(geometry)
            return True
        except:
            return False

    def validate_files(self, file_tuples):
        """
        Going to validate files here. check they don't contain directory info and are an accepted file format.
        """
        result = {'success':True,'errors':[]}
        filelist = []
        for ft in file_tuples:
            filelist.append(ft[0])
            name, ext = os.path.splitext(os.path.basename(ft[0]))
            accepted_extensions = ['.pdf', '.jpg', '.png', '.doc', '.docx', '.txt']
            if ft[0] != name + ext:
                result['errors'].append("The file at header {}, line {} looks like it contains a folder name.".format(ft[2],ft[3]))
            if not ext in accepted_extensions:
                result['errors'].append("Cannot recognise file extension at header {}, line {}. Currently only accept {}".format(ft[2],ft[3], accepted_extensions))
        
        if result['errors']:
            result['success'] = False
        return result, filelist

    def create_resourceid_list(self, workbook):
        ''''Looks for RESOURCEID column and creates a list of resourceids and returns '''
        resourceids_list = []
        for sheet_index,sheet in enumerate(workbook.worksheets):
            if workbook.sheetnames[sheet_index] == 'NOT':
                for col_index,header in enumerate(sheet.iter_cols(max_row = 1)):
                    if header[0].value =='RESOURCEID':
                        for row_index, row in enumerate(sheet.iter_rows(row_offset = 1)):
                            if row[col_index].value is not None:
                                resourceids_list.append(row[col_index].value)

        return resourceids_list
        
    def get_node_x_business_table_dict(self,wb):
        '''returns a dictionary that can be used to get the businesstablename
        of a node'''
        
        node_names = []
        for sheet in wb.worksheets:
            for header in sheet.iter_cols(max_row = 1):
                node_name = header[0].value
                if not node_name or node_name == 'RESOURCEID':
                    continue
                node_names.append(node_name)
        lookup = {}
        for name in node_names:
            obj = archesmodels.EntityTypes.objects.get(pk=name)
            lookup[name] = obj.businesstablename
        return lookup
        
    def flatten_values(self,data):
        '''flattens the dictionary output of get_values() into a list of tuples
        in the following format:
        
        (value,sheet_name,node_name,row_number,col_number)
        
        meant for easy iteration when the validation operation need not be grouped
        by node.
        '''
        
        output = []
        for sheet_name,contents in data.iteritems():
            for node_name,values in contents.iteritems():
                for val in values:
                    line = (val[0],sheet_name,node_name,val[1],val[2])
                    output.append(line)
        return output

    def get_values(self,wb,datatype=''):
        '''collects all data values from the workbook, only of certain type
        if specified.
        '''

        result = {}
        businesstable = self.get_node_x_business_table_dict(wb)

        for sheet_index,sheet in enumerate(wb.worksheets):
            sheet_name = wb.sheetnames[sheet_index]
            result[sheet_name] = {}
            for col_index,header in enumerate(sheet.iter_cols(max_row = 1)):
                node_name = header[0].value

                if not node_name or node_name == 'RESOURCEID':
                    continue

                if datatype and businesstable[node_name] != datatype:
                    continue

                result[sheet_name][node_name] = []
                for row_index, row in enumerate(sheet.iter_rows(row_offset = 1)):
                    value = row[col_index].value
                    if not value:
                        continue
                    result[sheet_name][node_name].append((value,row_index,col_index))

        return result
        
    def write_arches_file(self,workbook,resourcetype,destination,append=False):
        '''trimmed down version of SiteDataset, removing all validation operations.
        only produces a .arches file now.'''

        ResourceList = []

        if append:
            resourceids_list = self.create_resourceid_list(workbook)

        for sheet_index,sheet in enumerate(workbook.worksheets):
            sheet_name = workbook.sheetnames[sheet_index]
            for col_index,header in enumerate(sheet.iter_cols(max_row = 1)):
                GroupNo = 0
                node_name = header[0].value
                if not node_name or node_name == 'RESOURCEID':
                    continue

                node_obj = archesmodels.EntityTypes.objects.get(pk=node_name)
                entitytype = node_obj.entitytypeid
                datatype = node_obj.businesstablename

                start = datetime.datetime.now()
                all_concepts = self.collect_concepts(node_obj.conceptid_id,full_concept_list=[])

                ## dictionary will hold {label:concept.legacyoid}
                label_lookup = {}
                for c in all_concepts:
                    cobj = archesmodels.Concepts.objects.get(pk=c)
                    labels = archesmodels.Values.objects.filter(conceptid_id=c)
                    for label in labels:
                            label_lookup[label.value.lower()] = cobj.legacyoid

                for row_index, row in enumerate(sheet.iter_rows(row_offset = 1)):
                    
                    value = row[col_index].value
                    if not value:
                        continue

                    resourceid = row_index if append == False else resourceids_list[row_index]
                    value_encoded = (unicode(value)).encode('utf-8')

                    for concept in value_encoded.split('|'):
                        concept = concept.rstrip().lstrip() #removes potential trailing spaces, r and l
                        GroupNo = GroupNo + 1 if sheet_name is not 'NOT' else ''
                        GroupName = " ".join((sheet_name, str(GroupNo))) if sheet_name != 'NOT' else sheet_name

                        ## data transformations must happen with domains and dates
                        if datatype == 'domains':
                            if concept == "x":
                                continue
                            outval = label_lookup[concept.lower()]

                        elif datatype == 'dates':
                            outval = self.validatedate(concept)

                        else:
                            outval = concept

                        row = [str(resourceid),resourcetype,entitytype,outval, GroupName]
                        ResourceList.append(row)

        with open(destination, 'wb') as archesfile:
            writer = csv.writer(archesfile, delimiter ="|")
            writer.writerow(['RESOURCEID', 'RESOURCETYPE', 'ATTRIBUTENAME', 'ATTRIBUTEVALUE', 'GROUPID'])
            ResourceList = sorted(ResourceList, key = lambda row:(row[0],row[4],row[2]), reverse = False)
            for row in ResourceList:
                writer.writerow(row)

        ## make blank relations file
        relationsfile = destination.replace(".arches",".relations")
        with open(relationsfile, 'wb') as rel:
            writer = csv.writer(rel, delimiter ="|")
            writer.writerow(['RESOURCEID_FROM','RESOURCEID_TO','START_DATE','END_DATE','RELATION_TYPE','NOTES'])

        return

    ## DEPRECATED sept 13 2018
    def SiteDataset(self, source, resourcetype, destination, append = False):
        wb2 = load_workbook(source)
#             self.validaterows(wb2)
                
        ResourceList = []
        FaultyConceptsList = []
        Log = {
            'validate_headers' : {'errors': [], 'passed': True},
            'validate_rows_and_values' : {'errors': [], 'passed': True},
            'validate_geometries' :  {'errors': [], 'passed': True},
            'validate_dates' : {'errors': [], 'passed': True},
            'validate_concepts' :  {'errors': [], 'passed': True},
            'validate_files' : {'errors': [], 'passed': True},
        }
        if append:
            resourceids_list = self.create_resourceid_list(wb2)
        
        headers_errors = self.validate_headers(wb2,skip_resourceid_col = append)
        rows_values_errors =  self.validate_rows_and_values(wb2)
        if headers_errors:
            Log['validate_headers']['errors'].extend(headers_errors)
            Log['validate_headers']['passed'] = False
        if rows_values_errors:
            Log['validate_rows_and_values']['errors'].extend(rows_values_errors)
            Log['validate_rows_and_values']['passed'] = False            
#             if rows_values_errors['different_rows'] == True:
#                 Log['validate_rows_and_values']['passed'] = False
#             else:
#                 rows_values_errors.pop('different_rows', None)
#                 Log['validate_rows_and_values']['errors'].append(rows_values_errors['errors'])
#                 Log['validate_rows_and_values']['passed'] = False

        filelist = []
        
        if headers_errors or rows_values_errors:
            return Log, filelist

        for sheet_index,sheet in enumerate(wb2.worksheets):
            sheet_name = wb2.sheetnames[sheet_index]
            for col_index,header in enumerate(sheet.iter_cols(max_row = 1)):
                GroupNo = 0
                if header[0].value is not None and header[0].value != 'RESOURCEID':
                    print "Now analysing values for %s" % header[0].value
                    modelinstance = archesmodels.EntityTypes.objects.get(pk = header[0].value)
                    for row_index, row in enumerate(sheet.iter_rows(row_offset = 1)):
    #                     print "Row %s column %s with value %s" %(row_index, col_index, row[col_index].value)
                        if row[col_index].value is not None:
                            resourceid = row_index if append == False else resourceids_list[row_index]
                            value_encoded = (unicode(row[col_index].value)).encode('utf-8') #Values could be in Arabic or containing unicode chars, so it is essential to encode them properly.
                            for concept_index,concept in enumerate(re.sub(ur'|\s+', '|', value_encoded).split('|')): #replacing a semicolon (u003b) and space (u0020) with a semicolon in case that that space in front of the semicolon exists
                                concept = concept.rstrip() #removes potential trailing spaces
                                GroupNo = GroupNo +1 if sheet_name is not 'NOT' else ''
                                GroupName = " ".join((sheet_name, str(GroupNo))) if sheet_name != 'NOT' else sheet_name
                                if concept != 'x':
                                    if modelinstance.businesstablename == 'domains':                                
                                        concepts_in_node = self.collect_concepts(modelinstance.conceptid_id, full_concept_list =[])
                                        valueinstance =  self.validate_concept(concept, concepts_in_node)
                                        if valueinstance is not None:
                                            conceptinstance = archesmodels.Concepts.objects.get(pk=valueinstance[0][0].conceptid)
                                            concept_list = [str(resourceid),resourcetype,modelinstance.entitytypeid,conceptinstance.legacyoid,GroupName]
                                            ResourceList.append(concept_list)
#                                             print "ConceptId %s, ResourceId %s, AttributeName %s, AttributeValue %s, GroupId %s" %(valueinstance[0][0].conceptid, row_index,modelinstance.entitytypeid,conceptinstance.legacyoid,GroupName)
                                        else:
                                            Log['validate_concepts']['errors'].append("{0} in {1}, at row no. {2}".format(concept,header[0].value,(row_index+2)))
                                            Log['validate_concepts']['passed'] = False
                                            # logger.info("{0} in {1}, at row no. {2}".format(concept,header[0].value,(row_index+2)))
                                    if modelinstance.businesstablename == 'strings':
                                            concept_list = [str(resourceid),resourcetype,modelinstance.entitytypeid,concept, GroupName]
                                            ResourceList.append(concept_list)
        #                                     print "ResourceId %s, AttributeName %s, AttributeValue %s, GroupId %s" %(row_index,modelinstance.entitytypeid,concept, GroupName)
                                    if modelinstance.businesstablename == 'dates':
                                            if isinstance(self.validatedate(concept), basestring):
                                                Log['validate_dates']['errors'].append(self.validatedate(concept,header =header[0].value, row_no = row_index+2))
                                                Log['validate_dates']['passed'] = False                                       
                                            else:
                                                concept_list = [str(resourceid),resourcetype,modelinstance.entitytypeid,self.validatedate(concept), GroupName]
                                                ResourceList.append(concept_list)                                                         
                                    if modelinstance.businesstablename == 'geometries':
                                            if self.validate_geometry(concept,header[0].value,row_index):
                                                Log['validate_geometries']['errors'].append(self.validate_geometry(concept,header[0].value,row_index))
                                                Log['validate_geometries']['passed'] = False
                                            else:
                                                concept_list = [str(resourceid),resourcetype,modelinstance.entitytypeid,concept, GroupName]
                                                ResourceList.append(concept_list)
                                    if modelinstance.businesstablename == 'files':
                                            if self.validate_files(concept, header[0].value, row_index):
                                                Log['validate_files']['errors'].append(self.validate_files(concept, header[0].value, row_index))
                                                Log['validate_files']['passed'] = False
                                            else:
                                                concept_list = [str(resourceid), resourcetype, modelinstance.entitytypeid, concept, GroupName]
                                                ResourceList.append(concept_list)
                                                filelist.append(concept)

        else:
            Log['success'] = True
            with open(destination, 'wb') as archesfile:
                writer = csv.writer(archesfile, delimiter ="|")
                writer.writerow(['RESOURCEID', 'RESOURCETYPE', 'ATTRIBUTENAME', 'ATTRIBUTEVALUE', 'GROUPID'])
                ResourceList = sorted(ResourceList, key = lambda row:(row[0],row[4],row[2]), reverse = False)
                for row in ResourceList:
                    writer.writerow(row)

            ## make blank relations file
            relationsfile = destination.replace(".arches",".relations")
            with open(relationsfile, 'wb') as rel:
                writer = csv.writer(rel, delimiter ="|")
                writer.writerow(['RESOURCEID_FROM','RESOURCEID_TO','START_DATE','END_DATE','RELATION_TYPE','NOTES'])

            return Log, filelist
                                                                        