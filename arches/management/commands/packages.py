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
from arches.setup import get_elasticsearch_download_url, download_elasticsearch, unzip_file
from arches.db.install import truncate_db
from arches.app.utils.data_management.resources.importer import ResourceLoader
import arches.app.utils.data_management.resources.remover as resource_remover
import arches.app.utils.data_management.resource_graphs.exporter as graph_exporter
from arches.app.utils.data_management.resources.exporter import ResourceExporter
import arches.management.commands.package_utils.resource_graphs as resource_graphs
import arches.app.utils.index_database as index_database
from arches.management.commands import utils
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.mappings import prepare_term_index
from arches.app.models import models
import csv
from arches.app.utils.data_management.arches_file_importer import ArchesFileImporter
from arches.app.utils.data_management.arches_file_exporter import ArchesFileExporter


class Command(BaseCommand):
    """
    Commands for managing the loading and running of packages in Arches

    """

    def add_arguments(self, parser):
        parser.add_argument('-o', '--operation', action='store', dest='operation', default='setup',
            choices=['setup', 'install', 'setup_db', 'setup_indexes', 'start_elasticsearch', 'setup_elasticsearch', 'build_permissions', 'livereload', 'load_resources', 'remove_resources', 'load_concept_scheme', 'index_database','export_resources', 'import_json', 'export_json'],
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

        parser.add_argument('-c', '--concepts', action='store', dest='concepts', default=False,
            help='A comma separated list of the conceptids of the concepts you would like to import/export.')




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
            self.setup_indexes(package_name)

        if options['operation'] == 'setup_indexes':
            self.setup_indexes(package_name)

        if options['operation'] == 'start_elasticsearch':
            self.start_elasticsearch(package_name)

        if options['operation'] == 'setup_elasticsearch':
            self.setup_elasticsearch(package_name)

        if options['operation'] == 'livereload':
            self.start_livereload()

        if options['operation'] == 'build_permissions':
            self.build_permissions()

        if options['operation'] == 'load_resources':
            self.load_resources(package_name, options['source'])

        if options['operation'] == 'remove_resources':
            self.remove_resources(options['load_id'])

        if options['operation'] == 'load_concept_scheme':
            self.load_concept_scheme(package_name, options['source'])

        if options['operation'] == 'index_database':
            self.index_database(package_name)

        if options['operation'] == 'export_resources':
            self.export_resources(package_name, options['dest_dir'], options['resources'])

        if options['operation'] == 'import_json':
            self.import_json(options['source'], options['graphs'], options['resources'], options['concepts'])

        if options['operation'] == 'export_json':
            self.export(options['dest_dir'], options['graphs'], options['resources'], options['concepts'])

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

    def load_resources(self, package_name, data_source=None):
        """
        Runs the setup.py file found in the package root

        """
        # data_source = None if data_source == '' else data_source
        # load = import_string('%s.setup.load_resources' % package_name)
        # load(data_source)
        ArchesFileImporter(data_source).import_business_data()


    def remove_resources(self, load_id):
        """
        Runs the resource_remover command found in package_utils

        """
        resource_remover.delete_resources(load_id)

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


    def export_resources(self, package_name, data_dest=None, resources=''):
        """
        Exports resources to archesjson
        """
    #     resource_exporter = ResourceExporter('json')
    #     resource_exporter.export(search_results=False, dest_dir=data_dest)
    #     related_resources = [{'RESOURCEID_FROM':rr.entityid1, 'RESOURCEID_TO':rr.entityid2,'RELATION_TYPE':rr.relationshiptype,'START_DATE':rr.datestarted,'END_DATE':rr.dateended,'NOTES':rr.notes} for rr in models.RelatedResource.objects.all()]
    #     relations_file = os.path.splitext(data_dest)[0] + '.relations'
    #     with open(relations_file, 'w') as f:
    #         csvwriter = csv.DictWriter(f, delimiter='|', fieldnames=['RESOURCEID_FROM','RESOURCEID_TO','START_DATE','END_DATE','RELATION_TYPE','NOTES'])
    #         csvwriter.writeheader()
    #         for csv_record in related_resources:
    #             csvwriter.writerow({k: str(v).encode('utf8') for k, v in csv_record.items()})

        resource_exporter = ResourceExporter('json')
        resource_exporter.export(resources=resources, dest_dir=data_dest)


    def import_json(self, data_source='', graphs=None, resources=None, concepts=None):
        """
        Imports objects from arches.json.

        """

        if data_source == '':
            for path in settings.RESOURCE_GRAPH_LOCATIONS:
                if os.path.isfile(os.path.join(path)):
                    ArchesFileImporter(path).import_all()
                else:
                    file_paths = [file_path for file_path in os.listdir(path) if file_path.endswith('.json')]
                    for file_path in file_paths:
                        ArchesFileImporter(os.path.join(path, file_path)).import_all()
        else:
            if os.path.isfile(os.path.join(data_source)):
                ArchesFileImporter(data_source).import_all()
            else:
                file_paths = [filename for filename in os.listdir(data_source) if filename.endswith('.json')]
                for file_path in file_paths:
                    ArchesFileImporter(os.path.join(data_source, file_path)).import_all()


    def start_livereload(self):
        from livereload import Server
        server = Server()
        for path in settings.STATICFILES_DIRS:
            server.watch(path)
        for path in settings.TEMPLATES[0]['DIRS']:
            server.watch(path)
        server.serve(port=settings.LIVERELOAD_PORT)

    def export(self, data_dest=None, graphs=None, resources=None, concepts=None):
        """
        Export objects to arches.json.
        """

        if graphs != False:
            graphs = [x.strip(' ') for x in graphs.split(",")]
        if concepts != False:
            concepts = [x.strip(' ') for x in concepts.split(",")]
        if resources != False:
            resources = [x.strip(' ') for x in resources.split(",")]

        ArchesFileExporter().export_all(data_dest, graphs, resources, concepts)
