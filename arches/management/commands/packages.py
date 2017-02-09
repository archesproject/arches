'''
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

"""This module contains commands for building Arches."""

from django.core import management
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.module_loading import import_string
import os, sys, subprocess
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.setup import get_elasticsearch_download_url, download_elasticsearch, unzip_file
from arches.db.install import truncate_db
from arches.app.utils.data_management.resources.importer import ResourceLoader
import arches.app.utils.data_management.resources.remover as resource_remover
import arches.app.utils.data_management.resource_graphs.exporter as graph_exporter
import arches.app.utils.data_management.resource_graphs.importer as graph_importer
from arches.app.utils.data_management.resources.exporter import ResourceExporter
import arches.management.commands.package_utils.resource_graphs as resource_graphs
import arches.app.utils.index_database as index_database
from arches.management.commands import utils
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.mappings import prepare_term_index, delete_term_index, delete_search_index, prepare_resource_relations_index, delete_resource_relations_index
from arches.app.models import models
import csv, json
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.data_management.resources.arches_file_importer import ArchesFileImporter
from arches.app.utils.data_management.arches_file_exporter import ArchesFileExporter
from arches.app.utils.data_management.resources.csv_file_importer import CSVFileImporter
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from arches.app.utils.skos import SKOSReader
from django.db import transaction


class Command(BaseCommand):
    """
    Commands for managing the loading and running of packages in Arches

    """

    def add_arguments(self, parser):
        parser.add_argument('-o', '--operation', action='store', dest='operation', default='setup',
            choices=['setup', 'install', 'setup_db', 'setup_indexes', 'start_elasticsearch', 'setup_elasticsearch', 'build_permissions', 'livereload', 'remove_resources', 'load_concept_scheme', 'index_database','export_business_data', 'add_tilserver_layer', 'delete_tilserver_layer',
            'create_mapping_file', 'import_reference_data', 'import_graphs', 'import_business_data', 'import_mapping_file', 'add_mapbox_layer',],
            help='Operation Type; ' +
            '\'setup\'=Sets up Elasticsearch and core database schema and code' +
            '\'setup_db\'=Truncate the entire arches based db and re-installs the base schema' +
            '\'setup_indexes\'=Creates the indexes in Elastic Search needed by the system' +
            '\'install\'=Runs the setup file defined in your package root' +
            '\'start_elasticsearch\'=Runs the setup file defined in your package root' +
            '\'build_permissions\'=generates "add,update,read,delete" permissions for each entity mapping'+
            '\'livereload\'=Starts livereload for this package on port 35729')

        parser.add_argument('-s', '--source', action='store', dest='source', default='',
            help='Directory containing a .arches or .shp file containing resource records')

        parser.add_argument('-f', '--format', action='store', dest='format', default='arches',
            help='Format: shp or arches')

        parser.add_argument('-l', '--load_id', action='store', dest='load_id',
            help='Text string identifying the resources in the data load you want to delete.')

        parser.add_argument('-d', '--dest_dir', action='store', dest='dest_dir', default='',
            help='Directory where you want to save exported files.')

        parser.add_argument('-r', '--resources', action='store', dest='resources', default=False,
            help='A comma separated list of the resourceids of the resources you would like to import/export.')

        parser.add_argument('-g', '--graphs', action='store', dest='graphs', default=False,
            help='A comma separated list of the graphids of the resources you would like to import/export.')

        parser.add_argument('-c', '--config_file', action='store', dest='config_file', default=None,
            help='Usually an export mapping file.')

        parser.add_argument('-m', '--mapnik_xml_path', action='store', dest='mapnik_xml_path', default=False,
            help='A path to a mapnik xml file to generate a tileserver layer from.')

        parser.add_argument('-j', '--mapbox_json_path', action='store', dest='mapbox_json_path', default=False,
            help='A path to a mapbox json file to generate a layer from.')

        parser.add_argument('-n', '--layer_name', action='store', dest='layer_name', default=False,
            help='The name of the tileserver layer to add or delete.')

        parser.add_argument('-ow', '--overwrite', action='store', dest='overwrite', default=False,
            help='Whether to overwrite existing concepts with ones being imported or not.')

        parser.add_argument('-st', '--stage', action='store', dest='stage', default=False,
            help='Whether to stage new concepts or add them to the existing concept scheme.')

        parser.add_argument('-i', '--layer_icon', action='store', dest='layer_icon', default='fa fa-globe',
            help='An icon class to use for a tileserver layer.')

        parser.add_argument('-b', '--is_basemap', action='store_true', dest='is_basemap',
            help='Add to make the layer a basemap.')

        parser.add_argument('-bulk', '--bulk_load', action='store_true', dest='bulk_load',
            help='Bulk load values into the database.  By setting this flag the system will bypass any PreSave functions attached to the resource.')


    def handle(self, *args, **options):
        print 'operation: '+ options['operation']
        package_name = settings.PACKAGE_NAME
        print 'package: '+ package_name

        if options['operation'] == 'setup':
            self.setup(package_name)

        if options['operation'] == 'install':
            self.install(package_name)

        if options['operation'] == 'setup_db':
            self.setup_db(package_name)
            self.delete_indexes(package_name)
            self.setup_indexes(package_name)

        if options['operation'] == 'setup_indexes':
            self.setup_indexes(package_name)

        if options['operation'] == 'delete_indexes':
            self.delete_indexes(package_name)

        if options['operation'] == 'start_elasticsearch':
            self.start_elasticsearch(package_name)

        if options['operation'] == 'setup_elasticsearch':
            self.setup_elasticsearch(package_name)

        if options['operation'] == 'livereload':
            self.start_livereload()

        if options['operation'] == 'build_permissions':
            self.build_permissions()

        if options['operation'] == 'remove_resources':
            self.remove_resources(options['load_id'])

        if options['operation'] == 'load_concept_scheme':
            self.load_concept_scheme(package_name, options['source'])

        if options['operation'] == 'index_database':
            self.index_database(package_name)

        if options['operation'] == 'export_business_data':
            self.export_business_data(options['dest_dir'], options['format'], options['config_file'], options['graphs'])

        if options['operation'] == 'import_reference_data':
            self.import_reference_data(options['source'], options['overwrite'], options['stage'])

        if options['operation'] == 'import_graphs':
            self.import_graphs(options['source'])

        if options['operation'] == 'import_business_data':
            self.import_business_data(options['source'], options['config_file'], options['bulk_load'])

        if options['operation'] == 'import_mapping_file':
            self.import_mapping_file(options['source'])

        if options['operation'] == 'add_tilserver_layer':
            self.add_tilserver_layer(options['layer_name'], options['mapnik_xml_path'], options['layer_icon'], options['is_basemap'])

        if options['operation'] == 'add_mapbox_layer':
            self.add_mapbox_layer(options['layer_name'], options['mapbox_json_path'], options['layer_icon'], options['is_basemap'])

        if options['operation'] == 'delete_tilserver_layer':
            self.delete_tilserver_layer(options['layer_name'])

        if options['operation'] == 'create_mapping_file':
            self.create_mapping_file(options['dest_dir'], options['graphs'])

    def setup(self, package_name):
        """
        Installs Elasticsearch into the package directory and
        installs the database into postgres as "arches_<package_name>"

        """
        self.setup_elasticsearch(package_name, port=settings.ELASTICSEARCH_HTTP_PORT)
        self.setup_db(package_name)
        self.generate_procfile(package_name)

    def install(self, package_name):
        """
        Runs the setup.py file found in the package root

        """

        install = import_string('%s.setup.install' % package_name)
        install()

    def setup_elasticsearch(self, package_name, port=9200):
        """
        Installs Elasticsearch into the package directory and
        adds default settings for running in a test environment

        Change these settings in production

        """

        install_location = self.get_elasticsearch_install_location(package_name)
        install_root = os.path.abspath(os.path.join(install_location, '..'))
        url = get_elasticsearch_download_url(os.path.join(settings.ROOT_DIR, 'install'))
        file_name = url.split('/')[-1]

        download_elasticsearch(os.path.join(settings.ROOT_DIR, 'install'))
        unzip_file(os.path.join(settings.ROOT_DIR, 'install', file_name), install_root)

        es_config_directory = os.path.join(install_location, 'config')
        try:
            os.rename(os.path.join(es_config_directory, 'elasticsearch.yml'), os.path.join(es_config_directory, 'elasticsearch.yml.orig'))
        except: pass

        with open(os.path.join(es_config_directory, 'elasticsearch.yml'), 'w') as f:
            f.write('# ----------------- FOR TESTING ONLY -----------------')
            f.write('\n# - THESE SETTINGS SHOULD BE REVIEWED FOR PRODUCTION -')
            f.write('\nnode.max_local_storage_nodes: 1')
            f.write('\nnode.local: true')
            f.write('\nindex.number_of_shards: 1')
            f.write('\nindex.number_of_replicas: 0')
            f.write('\nhttp.port: %s' % port)
            f.write('\ndiscovery.zen.ping.multicast.enabled: false')
            f.write('\ndiscovery.zen.ping.unicast.hosts: ["localhost"]')
            f.write('\ncluster.routing.allocation.disk.threshold_enabled: false')

        # install plugin
        if sys.platform == 'win32':
            os.system("call %s install mobz/elasticsearch-head" % (os.path.join(install_location, 'bin', 'plugin.bat')))
        else:
            os.chdir(os.path.join(install_location, 'bin'))
            os.system("chmod u+x plugin")
            os.system("./plugin install mobz/elasticsearch-head")
            os.system("chmod u+x elasticsearch")

    def start_elasticsearch(self, package_name):
        """
        Starts the Elasticsearch process (blocking)
        WARNING: this will block all subsequent python calls

        """

        es_start = os.path.join(self.get_elasticsearch_install_location(package_name), 'bin')

        # use this instead to start in a non-blocking way
        if sys.platform == 'win32':
            import time
            p = subprocess.Popen(['service.bat', 'install'], cwd=es_start, shell=True)
            time.sleep(10)
            p = subprocess.Popen(['service.bat', 'start'], cwd=es_start, shell=True)
        else:
            p = subprocess.Popen(es_start + '/elasticsearch', cwd=es_start, shell=False)
        return p
        #os.system('honcho start')

    def setup_db(self, package_name):
        """
        Drops and re-installs the database found at "arches_<package_name>"
        WARNING: This will destroy data

        """

        db_settings = settings.DATABASES['default']
        truncate_path = os.path.join(settings.ROOT_DIR, 'db', 'install', 'truncate_db.sql')
        db_settings['truncate_path'] = truncate_path

        truncate_db.create_sqlfile(db_settings, truncate_path)

        os.system('psql -h %(HOST)s -p %(PORT)s -U %(USER)s -d postgres -f "%(truncate_path)s"' % db_settings)

        management.call_command('migrate')

    def setup_indexes(self, package_name):
        prepare_term_index(create=True)
        prepare_resource_relations_index(create=True)

    def drop_resources(self, packages_name):
        drop_all_resources()

    def delete_indexes(self, package_name):
        delete_term_index()
        delete_search_index()
        delete_resource_relations_index()

    def generate_procfile(self, package_name):
        """
        Generate a procfile for use with Honcho (https://honcho.readthedocs.org/en/latest/)

        """

        python_exe = os.path.abspath(sys.executable)

        contents = []
        contents.append('\nelasticsearch: %s' % os.path.join(self.get_elasticsearch_install_location(package_name), 'bin', 'elasticsearch'))
        contents.append('django: %s manage.py runserver' % (python_exe))
        contents.append('livereload: %s manage.py packages --operation livereload' % (python_exe))

        package_root = settings.PACKAGE_ROOT
        if hasattr(settings, 'SUBPACKAGE_ROOT'):
            package_root = settings.SUBPACKAGE_ROOT

        utils.write_to_file(os.path.join(package_root, '..', 'Procfile'), '\n'.join(contents))

    def get_elasticsearch_install_location(self, package_name):
        """
        Get the path to the Elasticsearch install

        """

        url = get_elasticsearch_download_url(os.path.join(settings.ROOT_DIR, 'install'))
        file_name = url.split('/')[-1]
        file_name_wo_extention = file_name[:-4]
        package_root = settings.PACKAGE_ROOT
        return os.path.join(package_root, 'elasticsearch', file_name_wo_extention)

    def build_permissions(self):
        """
        Creates permissions based on all the installed resource types

        """

        from arches.app.models import models
        from django.contrib.auth.models import Permission, ContentType

        resourcetypes = {}
        mappings = models.Mappings.objects.all()
        mapping_steps = models.MappingSteps.objects.all()
        rules = models.Rules.objects.all()
        for mapping in mappings:
            #print '%s -- %s' % (mapping.entitytypeidfrom_id, mapping.entitytypeidto_id)
            if mapping.entitytypeidfrom_id not in resourcetypes:
                resourcetypes[mapping.entitytypeidfrom_id] = set([mapping.entitytypeidfrom_id])
            for step in mapping_steps.filter(pk=mapping.pk):
                resourcetypes[mapping.entitytypeidfrom_id].add(step.ruleid.entitytyperange_id)

        for resourcetype in resourcetypes:
            for entitytype in resourcetypes[resourcetype]:
                content_type = ContentType.objects.get_or_create(app_label=resourcetype, model=entitytype)
                Permission.objects.create(codename='add_%s' % entitytype, name='%s - add' % entitytype , content_type=content_type[0])
                Permission.objects.create(codename='update_%s' % entitytype, name='%s - update' % entitytype , content_type=content_type[0])
                Permission.objects.create(codename='read_%s' % entitytype, name='%s - read' % entitytype , content_type=content_type[0])
                Permission.objects.create(codename='delete_%s' % entitytype, name='%s - delete' % entitytype , content_type=content_type[0])

    def remove_resources(self, load_id):
        """
        Runs the resource_remover command found in package_utils

        """
        # resource_remover.delete_resources(load_id)
        resource_remover.clear_resources()

    def load_concept_scheme(self, package_name, data_source=None):
        """
        Runs the setup.py file found in the package root

        """
        data_source = None if data_source == '' else data_source
        load = import_string('%s.management.commands.package_utils.authority_files.load_authority_files' % package_name)
        load(data_source)

    def index_database(self, package_name):
        """
        Runs the index_database command found in package_utils
        """
        # self.setup_indexes(package_name)
        index_database.index_db()

    def export_business_data(self, data_dest=None, file_format=None, config_file=None, graph=None):
        if file_format in ['csv', 'json']:
            resource_exporter = ResourceExporter(file_format)
            data = resource_exporter.export(data_dest=data_dest, configs=config_file, graph=graph)

            for file in data:
                with open(os.path.join(data_dest, file['name']), 'wb') as f:
                    f.write(file['outputfile'].getvalue())
        else:
            print '{0} is not a valid export file format.'.format(file_format)

    def import_reference_data(self, data_source, overwrite='ignore', stage='stage'):
        skos = SKOSReader()
        rdf = skos.read_file(data_source)
        ret = skos.save_concepts_from_skos(rdf, overwrite, stage)

    def import_business_data(self, data_source, config_file=None, bulk_load=False):
        """
        Imports business data from all formats
        """
        if data_source == '':
            print '*'*80
            print 'No data source indicated. Please rerun command with \'-s\' parameter.'
            print '*'*80

        if isinstance(data_source, basestring):
            data_source = [data_source]

        for path in data_source:
            if os.path.isfile(os.path.join(path)):
                BusinessDataImporter(path, config_file).import_business_data(bulk=bulk_load)

    def import_graphs(self, data_source=''):
        """
        Imports objects from arches.json.

        """

        if data_source == '':
            data_source = settings.RESOURCE_GRAPH_LOCATIONS

        if isinstance(data_source, basestring):
            data_source = [data_source]

        for path in data_source:
            if os.path.isfile(os.path.join(path)):
                with open(path, 'rU') as f:
                    archesfile = JSONDeserializer().deserialize(f)
                    ResourceGraphImporter(archesfile['graph'])
            else:
                file_paths = [file_path for file_path in os.listdir(path) if file_path.endswith('.json')]
                for file_path in file_paths:
                    with open(os.path.join(path, file_path), 'rU') as f:
                        archesfile = JSONDeserializer().deserialize(f)
                        ResourceGraphImporter(archesfile['graph'])

    def start_livereload(self):
        from livereload import Server
        server = Server()
        for path in settings.STATICFILES_DIRS:
            server.watch(path)
        for path in settings.TEMPLATES[0]['DIRS']:
            server.watch(path)
        server.serve(port=settings.LIVERELOAD_PORT)

    def add_tilserver_layer(self, layer_name=False, mapnik_xml_path=False, layer_icon='fa fa-globe', is_basemap=False):
        if layer_name != False and mapnik_xml_path != False:
            with transaction.atomic():
                tileserver_layer = models.TileserverLayers(name=layer_name, path=os.path.abspath(mapnik_xml_path))
                source_dict = {
                    "type": "raster",
                    "tiles": [
                        ("/tileserver/%s/{z}/{x}/{y}.png") % (layer_name)
                    ],
                    "tileSize": 256
                }
                layer_list = [{
                    "id": layer_name,
                    "type": "raster",
                    "source": layer_name,
                    "minzoom": 0,
                    "maxzoom": 22
                }]
                map_source = models.MapSources(name=layer_name, source=source_dict)
                map_layer = models.MapLayers(name=layer_name, layerdefinitions=layer_list, isoverlay=(not is_basemap), icon=layer_icon)
                map_source.save()
                map_layer.save()
                tileserver_layer.map_layer = map_layer
                tileserver_layer.map_source = map_source
                tileserver_layer.save()


    def add_mapbox_layer(self, layer_name=False, mapbox_json_path=False, layer_icon='fa fa-globe', is_basemap=False):
        if layer_name != False and mapbox_json_path != False:
            with open(mapbox_json_path) as data_file:
                data = json.load(data_file)
                with transaction.atomic():
                    for layer in data['layers']:
                        if 'source' in layer:
                            layer['source'] = layer['source'] + '-' + layer_name
                    for source_name, source_dict in data['sources'].iteritems():
                        map_source = models.MapSources.objects.get_or_create(name=source_name + '-' + layer_name, source=source_dict)
                    map_layer = models.MapLayers(name=layer_name, layerdefinitions=data['layers'], isoverlay=(not is_basemap), icon=layer_icon)
                    map_layer.save()


    def delete_tilserver_layer(self, layer_name=False):
        if layer_name != False:
            with transaction.atomic():
                tileserver_layer = models.TileserverLayers.objects.get(name=layer_name)
                tileserver_layer.map_layer.delete()
                tileserver_layer.map_source.delete()
                tileserver_layer.delete()


    def create_mapping_file(self, dest_dir=None, graphs=None):
        if graphs != False:
            graph = [x.strip(' ') for x in graphs.split(",")]

        graph_exporter.create_mapping_configuration_file(graphs, dest_dir)

    def import_mapping_file(self, source=None):
        """
        Imports export mapping files for resource models.
        """
        if source == '':
            print '*'*80
            print 'No data source indicated. Please rerun command with \'-s\' parameter.'
            print '*'*80

        if isinstance(source, basestring):
            source = [source]

        for path in source:
            if os.path.isfile(os.path.join(path)):
                with open(path, 'rU') as f:
                    mapping_file = json.load(f)
                    graph_importer.import_mapping_file(mapping_file)
