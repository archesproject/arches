from __future__ import division
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
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import GEOSGeometry
import json
import logging
logger = logging.getLogger('excel-reader')

class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('-o', '--operation', action='store', dest='operation', default='site_dataset',type='choice', choices=['bibliography','site_dataset'],help='Operation Type; ' + '\'bibliography\'=Reads a bibliographic XLSX and converts it to arches import file' + '\'site_dataset\'=Reads a site gazetteer XLSX and converts it to arches import file'),
        make_option('-s', '--source', action='store', dest='source', default='',help='Directory containing the XLSX file you need to convert to .arches'),
        make_option('-m', '--mapping', action='store', dest='mapping_file', default='',help='Directory containing a .csv mapping file'),        
        make_option('-d', '--dest_dir', action='store', dest='dest_dir',help='Directory, comprinsing of file name, where you want to save the .arches file'),
        make_option('-r', '--res_type', action='store', dest='resource_type', default='HERITAGE_RESOURCE_GROUP.E27', help='What kind of resource the source file contains e.g. HERITAGE_RESOURCE_GROUP.E27'),
        make_option('-a', '--append', action='store_true', dest='append_data', default=False, help='This flag indicates that the XLSX file contains data to append'),
    )
    
    def handle(self, *args, **options):
    
        ## flush logger here to start fresh for each iteration
        ## (is this really working??)
        logger = logging.getLogger('excel-reader')
        logger.handlers[0].flush()

        print 'operation: '+ options['operation']
        package_name = settings.PACKAGE_NAME
        print 'package: '+ package_name
        
        if options['operation'] == 'site_dataset':
            self.SiteDataset(options['source'], options['resource_type'], options['dest_dir'],options['append_data'])
        
        ## ultimately, the result should come from the SiteDataset function
        ## below is just an example of what it could look like, and it should
        ## be dumped to a .json file and that path returned from here.
        ## returning an actual dictionary object seems to cause problems...
        result = {'success':True,'msg':[]}

        # self.stdout.write(path/to/.json)
        
        return
    
    def validatedates(self, date):
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d') #Checks for format  YYYY-MM-DD
        except ValueError:
            try:
                d =datetime.datetime.strptime(date, '%Y-%m-%d %X') #Checks for format  YYYY-MM-DD hh:mm:ss
                date = d.strftime('%Y-%m-%d')
            except ValueError:
                try:
                    d = datetime.datetime.strptime(date,'%d-%m-%Y') #Checks for format  DD-MM-YYYY
                    date = d.strftime('%Y-%m-%d')
                except ValueError:
                    try:
                        d = datetime.datetime.strptime(date,'%d/%m/%Y') #Checks for format  DD/MM/YYYY
                        date = d.strftime('%Y-%m-%d')
                    except ValueError:
                        try:
                            d = datetime.datetime.strptime(date,'%d/%m/%y') #Checks for format  DD/MM/YY
                            date = d.strftime('%Y-%m-%d')
                            
                        except ValueError:
                            try:
                                d = datetime.datetime.strptime(date,'%Y') #Checks for format  YYYY
                                isodate = d.isoformat()
                                date = isodate.strip().split("T")[0] #
                            except:
                                # raise ValueError("The value %s inserted is not a date" % date)
                                logger.error("The value %s inserted is not a date" % date)
        return date
    
    '''Validates that the number of semicolon-separated values is consistent across a worksheet and spots empty cells'''
    def validate_rows_and_values(self,workbook):
        sheet_count = len(workbook.worksheets)
        rows_count  = 0
        ret = []
        offset_max = False
        errors = {
            'different_rows': False
        }

               
                    
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
                errors[workbook.sheetnames[sheet_index]] = ','.join(str(e) for e in ret)
                # raise ValueError("Error: cells in sheet %s do not contain an equal number of semicolon separated values or are empty. Errors are at the following lines: %s" % (workbook.sheetnames[sheet_index], sorted(ret)))
#                 logger.error("cells in sheet %s do not contain an equal number of semicolon separated values or are empty. Errors are at the following lines:" % (workbook.sheetnames[sheet_index]))
#                 for row in sorted(ret):
#                     logger.error(row)
        if (rows_count/sheet_count).is_integer() is not True:
            errors['different_rows'] = True
            return errors
            # raise ValueError("Error: some sheets in your XLSX file have a different number of rows")
#             logger.error("some sheets in your XLSX file have a different number of rows")
            
        if errors:
            return errors
        else:
            return None
            
    def validate_value_number(self, sheet, sheet_name):
        FaultyRows=[]
        print sheet_name
        for row_index, row in enumerate(sheet.iter_rows(row_offset = 1)):
            values_no = []
            if any(cell.value for cell in row):
                for cell in row:
                    if cell.value is not None:
                        if sheet_name !='NOT': #In the NOT tab, cells in a row are not part of the same merge group, so the number of semicolon separated values need not be equal
                            cell_no = 0
                            value_encoded = (unicode(cell.value)).encode('utf-8') #Values could be in Arabic or containing unicode chars, so it is essential to encode them properly.
                            cell_no = len(re.sub(ur';\s+', ';', value_encoded).split(';'))
                            values_no.append(cell_no)
                    else:
                        print row_index
                        values_no.append(0)
            try: 
                if values_no.count(values_no[0]) != len(values_no) or 0 in values_no:
                    FaultyRows.append(row_index+2) 
            except:
                pass
                        
        return list(set(FaultyRows))       
    #def validate_resourcetype(self, resourcetype):

    def validate_headers(self, workbook, skip_resourceid_col = False):
        errors = []
        for sheet in workbook.worksheets:
            for header in sheet.iter_cols(max_row = 1):
                if header[0].value is not None:
                    if skip_resourceid_col == True and header[0].value =='RESOURCEID':
                        pass
                    else:
                        try:
                            modelinstance = archesmodels.EntityTypes.objects.get(pk = header[0].value)
                        except ObjectDoesNotExist:
                            errors.append("The header %s is not a valid EAMENA node name" % header[0].value)
#                             logger.error("The header %s is not a valid EAMENA node name" % header[0].value)
                            # raise ObjectDoesNotExist("The header %s is not a valid EAMENA node name" % header[0].value)
        if errors:
            return errors
        else:
            return None
        
    def validate_concept(self, concept, concepts_in_node):
        valuelist = [archesmodels.Values.objects.filter(value__iexact = concept, conceptid= concept_in_node) for concept_in_node in concepts_in_node]
        valuelist = filter(None, valuelist)
        if valuelist:
            valueinstance = [x for x in valuelist if x]
            return valueinstance
        else:
            return None
            
    def collect_concepts(self, node_conceptid, full_concept_list = []):
        ''' Collects a full list of child concepts given the conceptid of the node. Returns a list of a set of concepts, i.e. expounding the duplicates'''
        concepts_in_node = archesmodels.ConceptRelations.objects.filter(conceptidfrom = node_conceptid)
        if concepts_in_node.count() > 0:
            full_concept_list.append(node_conceptid) 
            for concept_in_node in concepts_in_node:
                
                self.collect_concepts(concept_in_node.conceptidto_id, full_concept_list)
        else:
            full_concept_list.append(node_conceptid)
        return list(set(full_concept_list)) 
    
    def validate_geometries(self, geometry,row):
        try:
            GEOSGeometry(geometry)
            return
        except:
            logger.error("The geometry at line %s is not an acceptable GEOSGeometry" % row+2)
            # raise ValueError("The geometry at line %s is not an acceptable GEOSGeometry" % row+2)
            return "The geometry at line %s is not an acceptable GEOSGeometry" % row+2
    
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
                        
    def SiteDataset(self, source, resourcetype, destination, append = False):
        wb2 = load_workbook(source)
#             self.validaterows(wb2)
        
        ResourceList = []
        FaultyConceptsList = []
        Error_Log = {
            'validate_headers' : {'errors': [], 'passed': True},
            'validate_rows_and_values' : {'errors': [], 'passed': True},
            'validate_geometries' :  {'errors': [], 'passed': True},
            'validate_dates' : {'errors': [], 'passed': True},
            'validate_concepts' :  {'errors': [], 'passed': True},
        }
        if append:
            resourceids_list = self.create_resourceid_list(wb2)
        
        headers_errors = self.validate_headers(wb2,skip_resourceid_col = append)
        rows_values_errors =  self.validate_rows_and_values(wb2)
        if headers_errors:
            Error_Log['validate_headers']['errors'].append(headers_errors)
            Error_Log['validate_headers']['passed'] = False
            return Error_Log
        if rows_values_errors:
            if rows_values_errors['different_rows'] == True:
                Error_Log['validate_rows_and_values']['passed'] = False
            else:       
                Error_Log['validate_rows_and_values']['errors'].append(self.validate_rows_and_values(wb2))
                Error_Log['validate_rows_and_values']['passed'] = False
            return Error_Log
        
        for sheet_index,sheet in enumerate(wb2.worksheets):
            sheet_name = wb2.sheetnames[sheet_index]
            for col_index,header in enumerate(sheet.iter_cols(max_row = 1)):
                GroupNo = 0
                if header[0].value is not None and header[0].value != 'RESOURCEID':
                    print "Now analysing values for %s" % header[0].value
                    logger.info("Now analysing values for %s" % header[0].value)
                    modelinstance = archesmodels.EntityTypes.objects.get(pk = header[0].value)
                    for row_index, row in enumerate(sheet.iter_rows(row_offset = 1)):
    #                     print "Row %s column %s with value %s" %(row_index, col_index, row[col_index].value)
                        if row[col_index].value is not None:
                            resourceid = row_index if append == False else resourceids_list[row_index]
                            value_encoded = (unicode(row[col_index].value)).encode('utf-8') #Values could be in Arabic or containing unicode chars, so it is essential to encode them properly.
                            for concept_index,concept in enumerate(re.sub(ur';\s+', ';', value_encoded).split(';')): #replacing a semicolon (u003b) and space (u0020) with a semicolon in case that that space in front of the semicolon exists
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
                                            Error_Log['validate_concepts']['errors'].append("{0} in {1}, at row no. {2}".format(concept,header[0].value,(row_index+2)))
                                            Error_Log['validate_concepts']['passed'] = False
                                            # logger.info("{0} in {1}, at row no. {2}".format(concept,header[0].value,(row_index+2)))
                                    if modelinstance.businesstablename == 'strings':
                                            concept_list = [str(resourceid),resourcetype,modelinstance.entitytypeid,concept, GroupName]
                                            ResourceList.append(concept_list)
        #                                     print "ResourceId %s, AttributeName %s, AttributeValue %s, GroupId %s" %(row_index,modelinstance.entitytypeid,concept, GroupName)
                                    if modelinstance.businesstablename == 'dates':
                                            date = self.validatedates(concept)
                                            concept_list = [str(resourceid),resourcetype,modelinstance.entitytypeid,date, GroupName]
                                            ResourceList.append(concept_list)
                                    if modelinstance.businesstablename == 'geometries':
                                            if self.validate_geometries(concept,row_index):
                                                Error_Log['validate_geometries']['errors'].append(self.validate_geometries(concept,row_index))
                                                Error_Log['validate_geometries']['passed'] = False
                                            else:
                                                concept_list = [str(resourceid),resourcetype,modelinstance.entitytypeid,concept, GroupName]
                                                ResourceList.append(concept_list)
                                    
#         if FaultyConceptsList:
        if Error_Log['validate_geometries']['errors'] or Error_Log['validate_concepts']['errors']:
            return Error_Log
        else:
            with open(destination, 'wb') as csvfile:
                writer = csv.writer(csvfile, delimiter ="|")
                writer.writerow(['RESOURCEID', 'RESOURCETYPE', 'ATTRIBUTENAME', 'ATTRIBUTEVALUE', 'GROUPID'])
                for row in ResourceList:
                    writer.writerow(row)      
            # raise ValueError("The following concepts had issues %s" % FaultyConceptsList)
                                                                        
                            