import os
import sys
import csv
import json
import uuid
import importlib
import datetime
import unicodecsv
from time import time
from copy import deepcopy
from optparse import make_option
from os.path import isfile, join
from django.db import connection, transaction
from django.contrib.auth.models import User
from django.contrib.gis.gdal import DataSource
from django.forms.models import model_to_dict
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.models.models import DDataType
from arches.app.models.models import ResourceInstance
from arches.app.models.models import FunctionXGraph
from arches.app.models.models import ResourceXResource
from arches.app.models.models import NodeGroup
from arches.app.models.models import ResourceXResource
from arches.app.models.models import Concept
from arches.app.models.models import Value
from arches.app.models.models import ResourceXResource
from arches.app.models.concept import Concept
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.management.commands import utils
from arches.setup import unzip_file
from formats.csvfile import CsvReader
from formats.archesfile import ArchesFileReader

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class BusinessDataImporter(object):

    def __init__(self, file=None, mapping_file=None, relations_file=None):
        self.business_data = ''
        self.mapping = None
        self.graphs = ''
        self.reference_data = ''
        self.business_data = ''
        self.file_format = ''
        self.relations = ''
        csv.field_size_limit(sys.maxint)

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
                    self.file_format = file[0].split('.')[-1]
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
                        data = unicodecsv.DictReader(open(file[0], 'rU'), encoding='utf-8-sig', restkey='ADDITIONAL', restval='MISSING')
                        self.business_data = list(data)
                    elif self.file_format == 'zip':
                        shp_zipfile = os.path.basename(path)
                        shp_zipfile_name = os.path.splitext(shp_zipfile)[0]
                        unzip_dir = os.path.join(os.path.dirname(path),shp_zipfile_name)
                        unzip_file(path,unzip_dir)
                        shp = [i for i in os.listdir(unzip_dir) if i.endswith(".shp")]
                        if len(shp) == 0:
                            print '*'*80
                            print "ERROR: There is no shapefile in this zipfile."
                            print '*'*80
                            exit()
                        elif len(shp) > 1:
                            print '*'*80
                            print "ERROR: There are multiple shapefiles in this zipfile. Please load each individually:"
                            for s in shp:
                                print "\npython manage.py packages -o import_business_data -s {0} -c {1} -ow [append or overwrite]".format(
                                    os.path.join(unzip_dir,s),mapping_file[0])
                            print '*'*80
                            exit()
                        shp_path = os.path.join(unzip_dir,shp[0])
                        self.business_data = self.shape_to_csv(shp_path)
                    elif self.file_format == 'shp':
                        self.business_data = self.shape_to_csv(path)
                else:
                    print str(file) + ' is not a valid file'
            else:
                print path + ' is not a valid path'

    def import_business_data(self, file_format=None, business_data=None, mapping=None, overwrite='append', bulk=False, create_concepts=False, create_collections=False):
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
            elif file_format == 'csv' or file_format == 'shp' or file_format == 'zip':
                if mapping != None:
                    reader = CsvReader()
                    reader.import_business_data(business_data=business_data, mapping=mapping, overwrite=overwrite, bulk=bulk, create_concepts=create_concepts, create_collections=create_collections)
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

    def shape_to_csv(self, shp_path):
        csv_records = []
        ds = DataSource(shp_path)
        layer = ds[0]
        field_names = layer.fields
        for feat in layer:
            csv_record = dict((f, feat.get(f)) for f in field_names)
            csv_record['geom'] = feat.geom.wkt
            csv_records.append(csv_record)
        return csv_records
