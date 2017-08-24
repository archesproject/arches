import os
import csv
import zipfile
import datetime
import json
import glob
import uuid
from django.db.models import Q
from formats.csvfile import CsvWriter
from formats.rdffile import RdfWriter
from formats.archesjson import JsonWriter #Writes full resource instances rather than search results
from django.http import HttpResponse
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class ResourceExporter(object):

    def __init__(self, file_format, **kwargs):
        self.filetypes = {'csv': CsvWriter, 'json': JsonWriter, 'rdf': RdfWriter}
        self.format = file_format
        self.writer = self.filetypes[file_format](**kwargs)

    def export(self, graph_id=None, resourceinstanceids=None):
        resources = self.writer.write_resources(graph_id=graph_id, resourceinstanceids=resourceinstanceids)
        return resources

    def zip_response(self, files_for_export, zip_file_name=None, file_type=None):
        '''
        Given a list of export file names, zips up all the files with those names and returns and http response.
        '''
        buffer = StringIO()

        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip:
            for f in files_for_export:
                f['outputfile'].seek(0)
                zip.writestr(f['name'], f['outputfile'].read())

        zip.close()
        buffer.flush()
        zip_stream = buffer.getvalue()
        buffer.close()

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename=' + zip_file_name
        response['Content-length'] = str(len(zip_stream))
        response['Content-Type'] = 'application/zip'
        response.write(zip_stream)
        return response
