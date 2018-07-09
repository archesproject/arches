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
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import GEOSGeometry
import json

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
        
        print 'operation: '+ options['operation']
        package_name = settings.PACKAGE_NAME
        print 'package: '+ package_name

        if options['operation'] == 'site_dataset':
            result, filelist = self.SiteDataset(options['source'], options['resource_type'], options['dest_dir'],options['append_data'])
        error_path = os.path.join(settings.BULK_UPLOAD_DIR,"_validation_errors.json")
        with open(error_path,'w') as out:
            json.dump(result,out)
        self.stdout.write(error_path)

        if filelist:
            self.stdout.write("Has attachments")

        return
    
    def validatedates(self, date, header = None, row_no = None):
        try:
            d = datetime.datetime.strptime(date, '%Y-%m-%d') #Checks for format  YYYY-MM-DD
        except ValueError:
            try:
                d =datetime.datetime.strptime(date, '%Y-%m-%d %X') #Checks for format  YYYY-MM-DD hh:mm:ss (locale)
            except ValueError:
                try:
                    d = datetime.datetime.strptime(date,'%d-%m-%Y') #Checks for format  DD-MM-YYYY
                except ValueError:
                    try:
                        d = datetime.datetime.strptime(date,'%d/%m/%Y') #Checks for format  DD/MM/YYYY
                    except ValueError:
                        try:
                            d = datetime.datetime.strptime(date,'%d/%m/%y') #Checks for format  DD/MM/YY
                        except ValueError:
                            try:
                                d = datetime.datetime.strptime(date,'%Y') #Checks for format  YYYY
                                isodate = d.isoformat()
                                d = isodate.strip().split("T")[0]
                            except:
                                return "The value %s inserted under header %s at line %s is not a date" % (date, header, row_no)
        date = d.date()
        return date
    
    '''Validates that the number of semicolon-separated values is consistent across a worksheet and spots empty cells'''
    def validate_rows_and_values(self,workbook):
        sheet_count = len(workbook.worksheets)
        rows_count  = 0
        ret = []
        offset_max = False
#         errors_dict = {
#             'different_rows': False,
#             'errors': []
#         }
        errors = []
               
            
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
                # errors[workbook.sheetnames[sheet_index]] = ','.join(str(e) for e in ret)
                # raise ValueError("Error: cells in sheet %s do not contain an equal number of semicolon separated values or are empty. Errors are at the following lines: %s" % (workbook.sheetnames[sheet_index], sorted(ret)))
                errors.append("Error: cells in sheet %s do not contain an equal number of semicolon separated values or are empty. Errors are at the following lines: %s" % (workbook.sheetnames[sheet_index], sorted(ret)))
        if (rows_count/sheet_count).is_integer() is not True:
#             errors_dict['different_rows'] = True
            errors.append("Error: some sheets in your XLSX file have a different number of rows")
            return errors
            # raise ValueError("Error: some sheets in your XLSX file have a different number of rows")
            
        if errors:
            return errors
        else:
            return None
            
    def validate_value_number(self, sheet, sheet_name):
        FaultyRows=[]
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
    
    def validate_geometries(self, geometry,header,row):
        try:
            GEOSGeometry(geometry)
            return
        except:
            # raise ValueError("The geometry at line %s is not an acceptable GEOSGeometry" % row+2)
            return "The geometry at header %s, line %s is not an acceptable GEOSGeometry" % (header, row+2)

    def validate_files(self, filename, header, row):
        """
        Going to validate files here. check they don't contain directory info and are an accepted file format.
        """
        name, ext = os.path.splitext(os.path.basename(filename))
        accepted_extensions = ['.pdf', '.jpg', '.png', '.doc', '.docx', '.txt']
        if filename != name + ext:
            return "The file at header %s, line %s looks like it contains a folder name." % (header, row+2)
        if ext in accepted_extensions:
            return
        else:
            return "Cannot recognise file extension at header %s, line %s. Currently only accept %s" % (header, row+2, accepted_extensions)
    
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
        if headers_errors or rows_values_errors:
            return Log
    
        filelist = []

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
                                            Log['validate_concepts']['errors'].append("{0} in {1}, at row no. {2}".format(concept,header[0].value,(row_index+2)))
                                            Log['validate_concepts']['passed'] = False
                                            # logger.info("{0} in {1}, at row no. {2}".format(concept,header[0].value,(row_index+2)))
                                    if modelinstance.businesstablename == 'strings':
                                            concept_list = [str(resourceid),resourcetype,modelinstance.entitytypeid,concept, GroupName]
                                            ResourceList.append(concept_list)
        #                                     print "ResourceId %s, AttributeName %s, AttributeValue %s, GroupId %s" %(row_index,modelinstance.entitytypeid,concept, GroupName)
                                    if modelinstance.businesstablename == 'dates':
                                            if isinstance(self.validatedates(concept), basestring):
                                                Log['validate_dates']['errors'].append(self.validatedates(concept,header =header[0].value, row_no = row_index+2))
                                                Log['validate_dates']['passed'] = False                                       
                                            else:
                                                concept_list = [str(resourceid),resourcetype,modelinstance.entitytypeid,self.validatedates(concept), GroupName]
                                                ResourceList.append(concept_list)                                                         
                                    if modelinstance.businesstablename == 'geometries':
                                            if self.validate_geometries(concept,header[0].value,row_index):
                                                Log['validate_geometries']['errors'].append(self.validate_geometries(concept,header[0].value,row_index))
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
                                                                        