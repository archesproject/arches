import os
import sys
import csv
import json
import uuid
import importlib
import datetime
import unicodecsv
from time import time
from os.path import isfile, join
from django.conf import settings
from django.db import connection, transaction
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.core.management.base import BaseCommand, CommandError
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.entity import Entity
from arches.app.models.resource import Resource
from arches.app.models.models import Concept
from arches.app.models.models import Value
from arches.app.models.models import ResourceXResource
from arches.app.models.concept import Concept
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.management.commands import utils
from optparse import make_option
from formats.archesjson import JsonReader
from formats.shpfile import ShapeReader
from formats.csvfile import CsvReader
from formats.archesfile import ArchesFileReader
from arches.app.models.tile import Tile
from arches.app.models.models import DDataType
from arches.app.models.models import ResourceInstance
from arches.app.models.models import FunctionXGraph
from arches.app.models.models import ResourceXResource
from arches.app.models.models import NodeGroup
from arches.app.models.models import ResourceXResource
from django.core.exceptions import ValidationError
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from copy import deepcopy


class BusinessDataImporter(object):

    def __init__(self, file=None, mapping_file=None, relations_file=None):
        self.business_data = ''
        self.mapping = None
        self.graphs = ''
        self.reference_data = ''
        self.business_data = ''
        self.file_format = ''
        self.relations = ''

        if not file:
            file = settings.BUSINESS_DATA_FILES
        else:
            file = [file]

        if mapping_file == None:
            try:
                mapping_file = [file[0].split('.')[0] + '.mapping']
            except:
                print '*'*80
                print "ERROR: Mapping file is missing or improperly named. Make sure you have mapping file with the same basename as your business data file and the extension .mapping"
                print '*'*80
                sys.exit()
        else:
            try:
                mapping_file = [mapping_file]
            except:
                print '*'*80
                print "ERROR: Mapping file is missing or improperly named. Make sure you have mapping file with the same basename as your business data file and the extension .mapping"
                print '*'*80
                sys.exit()

        if relations_file == None:
            try:
                relations_file = [file[0].split('.')[0] + '.relations']
            except:
                pass

        for path in relations_file:
            if os.path.exists(path):
                if isfile(join(path)):
                    self.relations = csv.DictReader(open(relations_file[0], 'r'))

        for path in mapping_file:
            if os.path.exists(path):
                if isfile(join(path)):
                    self.mapping = json.load(open(path, 'r'))
                else:
                    self.mapping = None

        for path in file:
            if os.path.exists(path):
                if isfile(join(path)):
                    self.file_format = file[0].split('.')[1]
                    if self.file_format == 'json':
                        with open(file[0], 'rU') as f:
                            archesfile = JSONDeserializer().deserialize(f)
                            if 'graph' in archesfile.keys():
                                self.graphs = archesfile['graph']
                            if 'reference_data' in archesfile.keys():
                                self.reference_data = archesfile['reference_data']
                            if 'business_data' in archesfile.keys():
                                self.business_data = archesfile['business_data']
                    elif self.file_format == 'csv':
                        data = unicodecsv.DictReader(open(file[0], 'r'), encoding='utf-8-sig', restkey='ADDITIONAL', restval='MISSING')
                        self.business_data = list(data)
                else:
                    print str(file) + ' is not a valid file'
            else:
                print path + ' is not a valid path'

    def import_business_data(self, file_format=None, business_data=None, mapping=None, overwrite='append', bulk=False):
        reader = None
        start = time()
        cursor = connection.cursor()

        try:
            if file_format == None:
                file_format = self.file_format
            if business_data == None:
                business_data = self.business_data
            if mapping == None:
                mapping = self.mapping
            if file_format == 'json':
                reader = ArchesFileReader()
                reader.import_business_data(business_data, mapping)
            elif file_format == 'csv':
                if mapping != None:
                    reader = CsvReader()
                    reader.import_business_data(business_data=business_data, mapping=mapping, overwrite=overwrite, bulk=bulk)
                else:
                    print '*'*80
                    print 'ERROR: No mapping file detected. Please indicate one with the \'-c\' paramater or place one in the same directory as your business data.'
                    print '*'*80
                    sys.exit()

            elapsed = (time() - start)
            print 'Time to import_business_data = {0}'.format(datetime.timedelta(seconds=elapsed))

            reader.report_errors()

        finally:
            datatype_factory = DataTypeFactory()
            datatypes = DDataType.objects.all()
            for datatype in datatypes:
                datatype_instance = datatype_factory.get_instance(datatype.datatype)
                datatype_instance.after_update_all()


class ResourceLoader(object):

    def __init__(self):
        self.user = User()
        self.user.first_name = settings.ETL_USERNAME
        self.resources = []
        self.se = SearchEngineFactory().create()

    option_list = BaseCommand.option_list + (
        make_option('--source',
            action='store',
            dest='source',
            default='',
            help='.arches file containing resource records'),
         make_option('--format',
            action='store_true',
            default='arches',
            help='format extension that you would like to load: arches or shp'),
        )

    def load(self, source):
        file_name, file_format = os.path.splitext(source)
        archesjson = False
        if file_format == '.shp':
            reader = ShapeReader()
        elif file_format == '.arches':
            reader = ArchesReader()
            print '\nVALIDATING ARCHES FILE ({0})'.format(source)
            reader.validate_file(source)
        elif file_format == '.json':
            archesjson = True
            reader = JsonReader()

        start = time()
        resources = reader.load_file(source)

        print '\nLOADING RESOURCES ({0})'.format(source)
        relationships = None
        related_resource_records = []
        relationships_file = file_name + '.relations'
        elapsed = (time() - start)
        print 'time to parse {0} resources = {1}'.format(file_name, elapsed)
        results = self.resource_list_to_entities(resources, archesjson)
        if os.path.exists(relationships_file):
            relationships = csv.DictReader(open(relationships_file, 'r'), delimiter='|')
            for relationship in relationships:
                related_resource_records.append(self.relate_resources(relationship, results['legacyid_to_entityid'], archesjson))
        else:
            print 'No relationship file'


    # def relate_resources(self, relationship, legacyid_to_entityid, archesjson):
    #     start_date = None if relationship['START_DATE'] in ('', 'None') else relationship['START_DATE']
    #     end_date = None if relationship['END_DATE'] in ('', 'None') else relationship['END_DATE']
    #
    #     if archesjson == False:
    #         relationshiptype_concept = Concept.objects.get(legacyoid = relationship['RELATION_TYPE'])
    #         concept_value = Value.objects.filter(concept = relationshiptype_concept.conceptid).filter(valuetype = 'prefLabel')
    #         entityid1 = legacyid_to_entityid[relationship['RESOURCEID_FROM']]
    #         entityid2 = legacyid_to_entityid[relationship['RESOURCEID_TO']]
    #
    #     else:
    #         concept_value = Value.objects.filter(valueid = relationship['RELATION_TYPE'])
    #         entityid1 = relationship['RESOURCEID_FROM']
    #         entityid2 = relationship['RESOURCEID_TO']
    #
    #     related_resource_record = ResourceXResource(
    #         entityid1 = entityid1,
    #         entityid2 = entityid2,
    #         notes = relationship['NOTES'],
    #         relationshiptype = concept_value[0].valueid,
    #         datestarted = start_date,
    #         dateended = end_date,
    #         )
    #
    #     related_resource_record.save()
    #     self.se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(related_resource_record), idfield='resourcexid')
