import importlib
import uuid
from django.conf import settings
from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from django.contrib.gis.geos import GEOSGeometry
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from shapely.geometry import asShape

def get_datatype_instance(datatype):
    d_datatype = models.DDataType.objects.get(datatype=datatype)
    mod_path = d_datatype.modulename.replace('.py', '')
    module = importlib.import_module('arches.app.datatypes.%s' % mod_path)
    datatype_instance = getattr(module, d_datatype.classname)(d_datatype)
    return datatype_instance

class StringDataType(BaseDataType):
    def append_to_document(self, document, nodevalue):
        document['strings'].append(nodevalue)

    def transform_export_values(self, value):
        return value.encode('utf8')

    def get_search_term(self, nodevalue):
        term = None
        if nodevalue is not None:
            if settings.WORDS_PER_SEARCH_TERM == None or (len(nodevalue.split(' ')) < settings.WORDS_PER_SEARCH_TERM):
                term = nodevalue
        return term

class NumberDataType(BaseDataType):
    def transform_import_values(self, value):
        return float(value)

    def append_to_document(self, document, nodevalue):
        document['numbers'].append(nodevalue)

class BooleanDataType(BaseDataType):
    def transform_import_values(self, value):
        return bool(distutils.util.strtobool(value))

class DateDataType(BaseDataType):
    def append_to_document(self, document, nodevalue):
        document['dates'].append(nodevalue)

class GeojsonFeatureCollectionDataType(BaseDataType):
    def transform_import_values(self, value):
        arches_geojson = {}
        arches_geojson['type'] = "FeatureCollection"
        arches_geojson['features'] = []
        geometry = GEOSGeometry(value, srid=4326)
        if geometry.num_geom > 1:
            for geom in geometry:
                arches_json_geometry = {}
                arches_json_geometry['geometry'] = JSONDeserializer().deserialize(GEOSGeometry(geom, srid=4326).json)
                arches_json_geometry['type'] = "Feature"
                arches_json_geometry['id'] = str(uuid.uuid4())
                arches_json_geometry['properties'] = {}
                arches_geojson['features'].append(arches_json_geometry)
        else:
            arches_json_geometry = {}
            arches_json_geometry['geometry'] = JSONDeserializer().deserialize(geometry.json)
            arches_json_geometry['type'] = "Feature"
            arches_json_geometry['id'] = str(uuid.uuid4())
            arches_json_geometry['properties'] = {}
            arches_geojson['features'].append(arches_json_geometry)

        return arches_geojson

    def transform_export_values(self, value):
        wkt_geoms = []
        for feature in value['features']:
            wkt_geoms.append(GEOSGeometry(json.dumps(feature['geometry'])))
        return GeometryCollection(wkt_geoms)

    def append_to_document(self, document, nodevalue):
        document['geometries'].append(nodevalue)

    def get_bounds(self, tile, node):
        bounds = None
        node_data = tile.data[str(node.pk)]
        for feature in node_data['features']:
            shape = asShape(feature['geometry'])
            bounds = shape.bounds
        return bounds

class FileListDataType(BaseDataType):
    def manage_files(self, previously_saved_tile, current_tile, request, node):
        if previously_saved_tile.count() == 1:
            for previously_saved_file in previously_saved_tile[0].data[str(node.pk)]:
                previously_saved_file_has_been_removed = True
                for incoming_file in current_tile.data[str(node.pk)]:
                    if previously_saved_file['file_id'] == incoming_file['file_id']:
                        previously_saved_file_has_been_removed = False
                if previously_saved_file_has_been_removed:
                    deleted_file = models.File.objects.get(pk=previously_saved_file["file_id"])
                    deleted_file.delete()

        files = request.FILES.getlist('file-list_' + str(node.pk), [])
        for file_data in files:
            file_model = models.File()
            file_model.path = file_data
            file_model.save()
            for file_json in current_tile.data[str(node.pk)]:
                if file_json["name"] == file_data.name and file_json["url"] is None:
                    file_json["file_id"] = str(file_model.pk)
                    file_json["url"] = str(file_model.path.url)
                    file_json["status"] = 'uploaded'

    def transform_import_values(self, value):
        '''
        # TODO: Following commented code can be used if user does not already have file in final location using django ORM:

        request = HttpRequest()
        # request.FILES['file-list_' + str(nodeid)] = None
        files = []
        # request_list = []

        for val in value.split(','):
            val_dict = {}
            val_dict['content'] = val
            val_dict['name'] = val.split('/')[-1].split('.')[0]
            val_dict['url'] = None
            # val_dict['size'] = None
            # val_dict['width'] = None
            # val_dict['height'] = None
            files.append(val_dict)
            f = open(val, 'rb')
            django_file = InMemoryUploadedFile(f,'file',val.split('/')[-1].split('.')[0],None,None,None)
            request.FILES.appendlist('file-list_' + str(nodeid), django_file)
        print request.FILES
        value = files
        '''

        mime = MimeTypes()
        tile_data = []
        for file_path in value.split(','):
            try:
                file_stats = os.stat(file_path)
                tile_file['lastModified'] = file_stats.st_mtime
                tile_file['size'] =  file_stats.st_size
            except:
                pass
            tile_file = {}
            tile_file['file_id'] =  str(uuid.uuid4())
            tile_file['status'] = ""
            tile_file['name'] =  file_path.split('/')[-1]
            tile_file['url'] =  settings.MEDIA_URL + 'uploadedfiles/' + str(tile_file['name'])
            # tile_file['index'] =  0
            # tile_file['height'] =  960
            # tile_file['content'] =  None
            # tile_file['width'] =  1280
            # tile_file['accepted'] =  True
            tile_file['type'] =  mime.guess_type(file_path)[0]
            tile_file['type'] = '' if tile_file['type'] == None else file_tile['type']
            tile_data.append(tile_file)
            file_path = 'uploadedfiles/' + str(tile_file['name'])
            fileid = tile_file['file_id']
            File.objects.get_or_create(fileid=fileid, path=file_path)

        result = json.loads(json.dumps(tile_data))
        return result
