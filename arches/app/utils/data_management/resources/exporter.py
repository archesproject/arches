import zipfile
from arches.app.utils import import_class_from_string
from arches.app.models.system_settings import settings
from django.http import HttpResponse


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class ResourceExporter(object):

    def __init__(self, format=None, **kwargs):
        kwargs['format'] = format
        self.writer = import_class_from_string(settings.RESOURCE_FORMATERS[format])(**kwargs)

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
