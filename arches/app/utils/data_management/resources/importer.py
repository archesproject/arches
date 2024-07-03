import os
import sys
import csv
import json
import uuid
import importlib
import datetime
import logging
from io import StringIO
from time import time
from copy import deepcopy
from optparse import make_option
from os.path import isfile, join
from django.core import management
from multiprocessing import Pool, TimeoutError, cpu_count
import django
from django.db.models.expressions import F

# django.setup() must be called here to prepare for multiprocessing. specifically,
# it must be called before any models are imported, otherwise things will crash
# during a resource load that uses multiprocessing.
# see https://stackoverflow.com/a/49461944/3873885
django.setup()
from django.db import connection, connections
from django.contrib.gis.gdal import DataSource
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import (
    DDataType,
    Language,
    ResourceXResource,
    ResourceInstance,
)
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.i18n import capitalize_region
from arches.app.utils.zip import unzip_file
from .formats.csvfile import CsvReader
from .formats.archesfile import ArchesFileReader
import ctypes


def import_one_resource(line, prevent_indexing=False):
    """this single resource import function must be outside of the BusinessDataImporter
    class in order for it to be called with multiprocessing"""

    connections.close_all()
    reader = ArchesFileReader()
    archesresource = JSONDeserializer().deserialize(line)
    reader.import_business_data(
        {"resources": [archesresource]}, prevent_indexing=prevent_indexing
    )


class BusinessDataImporter(object):
    def __init__(self, file=None, mapping_file=None, relations_file=None):
        self.business_data = ""
        self.mapping = None
        self.graphs = ""
        self.reference_data = ""
        self.business_data = ""
        self.file_format = ""
        self.relations = ""
        try:
            csv.field_size_limit(sys.maxsize)
        except:
            csv.field_size_limit(int(ctypes.c_ulong(-1).value // 2))

        if not file:
            file = settings.BUSINESS_DATA_FILES
        else:
            file = [file]
        self.file = file
        if mapping_file is None:
            try:
                mapping_file_base = os.path.splitext(file[0])[0]
                mapping_file = [f"{mapping_file_base}.mapping"]
            except:
                print("*" * 80)
                print(
                    "ERROR: Mapping file is missing or improperly named. Make sure you have \
                    mapping file with the same basename as your business data file and the extension .mapping"
                )
                print("*" * 80)
                sys.exit()
        else:
            try:
                mapping_file = [mapping_file]
            except:
                print("*" * 80)
                print(
                    "ERROR: Mapping file is missing or improperly named. Make sure you have \
                    mapping file with the same basename as your business data file and the extension .mapping"
                )
                print("*" * 80)
                sys.exit()

        if relations_file is None:
            try:
                relations_file_base = os.path.splitext(file[0])[0]
                relations_file = [f"{relations_file_base}.relations"]
            except:
                pass

        for path in relations_file:
            if os.path.exists(path):
                if isfile(join(path)):
                    with open(relations_file[0], "r") as f:
                        self.relations = csv.DictReader(f)

        for path in mapping_file:
            if os.path.exists(path):
                if isfile(join(path)):
                    with open(path, "r") as f:
                        self.mapping = json.load(f)
                else:
                    self.mapping = None

        for path in file:
            if os.path.exists(path):
                if isfile(join(path)):
                    self.file_format = os.path.splitext(file[0])[1].strip(".")
                    if self.file_format == "json":
                        with open(file[0], "r") as f:
                            archesfile = JSONDeserializer().deserialize(f)
                            if "graph" in list(archesfile.keys()):
                                self.graphs = archesfile["graph"]
                            if "reference_data" in list(archesfile.keys()):
                                self.reference_data = archesfile["reference_data"]
                            if "business_data" in list(archesfile.keys()):
                                self.business_data = archesfile["business_data"]
                    elif self.file_format == "csv":
                        with open(file[0], encoding="utf-8") as f:
                            data = csv.DictReader(f)
                            self.business_data = list(data)
                    elif self.file_format == "zip":
                        shp_zipfile = os.path.basename(path)
                        shp_zipfile_name = os.path.splitext(shp_zipfile)[0]
                        unzip_dir = os.path.join(
                            os.path.dirname(path), shp_zipfile_name
                        )
                        unzip_file(path, unzip_dir)
                        shp = [i for i in os.listdir(unzip_dir) if i.endswith(".shp")]
                        if len(shp) == 0:
                            print("*" * 80)
                            print("ERROR: There is no shapefile in this zipfile.")
                            print("*" * 80)
                            exit()
                        elif len(shp) > 1:
                            print("*" * 80)
                            print(
                                "ERROR: There are multiple shapefiles in this zipfile. Please load each individually:"
                            )
                            for s in shp:
                                print(
                                    "\npython manage.py packages -o import_business_data -s {0} -c {1} -ow [append or overwrite]".format(
                                        os.path.join(unzip_dir, s), mapping_file[0]
                                    )
                                )
                            print("*" * 80)
                            exit()
                        shp_path = os.path.join(unzip_dir, shp[0])
                        self.business_data = self.shape_to_csv(shp_path)
                    elif self.file_format == "shp":
                        self.business_data = self.shape_to_csv(path)
                else:
                    print(str(file) + " is not a valid file")
            else:
                print(path + " is not a valid path")

    def scan_for_new_languages(self, business_data=None, reader=None):
        file_reader = reader
        data = business_data
        if file_reader is None:
            file_reader = self.get_reader()
        if data is None:
            data = self.business_data
        if file_reader is not None and data is not None:
            language_list = file_reader.scan_for_new_languages(business_data=data)
            if language_list is not None:
                return list(set(capitalize_region(code) for code in language_list))

        return []

    def get_reader(self, file_format=None):
        if file_format is None:
            file_format = self.file_format
        if file_format == "json" or file_format == "jsonl":
            return ArchesFileReader()
        elif file_format == "csv" or file_format == "shp" or file_format == "zip":
            return CsvReader()

    def import_business_data(
        self,
        file_format=None,
        business_data=None,
        mapping=None,
        overwrite="append",
        bulk=False,
        create_concepts=False,
        create_collections=False,
        use_multiprocessing=False,
        prevent_indexing=False,
        transaction_id=None,
    ):
        start = time()
        cursor = connection.cursor()
        try:
            if file_format is None:
                file_format = self.file_format
            if business_data is None:
                business_data = self.business_data
            if mapping is None:
                mapping = self.mapping

            reader = self.get_reader(file_format)

            if file_format == "json":
                reader.import_business_data(
                    business_data,
                    mapping=mapping,
                    overwrite=overwrite,
                    prevent_indexing=prevent_indexing,
                    transaction_id=transaction_id,
                )
            elif file_format == "jsonl":
                with open(self.file[0], "r") as openf:
                    lines = openf.readlines()
                    if use_multiprocessing is True:
                        pool = Pool(cpu_count())
                        pool.map(import_one_resource, lines)
                        connections.close_all()
                    else:
                        for line in lines:
                            archesresource = JSONDeserializer().deserialize(line)
                            reader.import_business_data(
                                {"resources": [archesresource]},
                                overwrite=overwrite,
                                prevent_indexing=prevent_indexing,
                                transaction_id=transaction_id,
                            )
            elif file_format == "csv" or file_format == "shp" or file_format == "zip":
                if mapping is not None:
                    reader.import_business_data(
                        business_data=business_data,
                        mapping=mapping,
                        overwrite=overwrite,
                        bulk=bulk,
                        create_concepts=create_concepts,
                        create_collections=create_collections,
                        prevent_indexing=prevent_indexing,
                        transaction_id=transaction_id,
                    )
                else:
                    print("*" * 80)
                    print(
                        f"ERROR: No mapping file detected for {self.file[0]}. Please indicate one \
                        with the '-c' parameter or place one in the same directory as your business data."
                    )
                    print("*" * 80)

            elapsed = time() - start
            print(
                "Time to import_business_data = {0}".format(
                    datetime.timedelta(seconds=elapsed)
                )
            )

            if reader is not None:
                reader.report_errors()

        finally:
            # cleans up the ResourceXResource table, adding any graph_id values that were unavailable during package/csv load
            for res_x_res in ResourceXResource.objects.filter(
                resourceinstanceto_graphid__isnull=True
            ):
                # wrapping in a try allows for graceful handling of corrupted data
                try:
                    res_x_res.resourceinstanceto_graphid = (
                        res_x_res.resourceinstanceidto.graph
                    )
                except:
                    pass

                res_x_res.save()

            datatype_factory = DataTypeFactory()
            datatypes = DDataType.objects.all()
            for datatype in datatypes:
                try:
                    datatype_instance = datatype_factory.get_instance(datatype.datatype)
                    datatype_instance.after_update_all()
                except BrokenPipeError as e:
                    logger = logging.getLogger(__name__)
                    logger.info("Celery not working: tasks unavailable during import.")

    def shape_to_csv(self, shp_path):
        csv_records = []
        ds = DataSource(shp_path)
        layer = ds[0]
        field_names = layer.fields
        for feat in layer:
            csv_record = dict((f, feat.get(f)) for f in field_names)
            csv_record["geom"] = feat.geom.wkt
            csv_records.append(csv_record)
        return csv_records
