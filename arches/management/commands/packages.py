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

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.importlib import import_module
import os, sys, subprocess
from arches.setup import get_elasticsearch_download_url, download_elasticsearch, unzip_file
from arches.db.install import truncate_db, install_db
from arches.app.utils.data_management.resources.importer import ResourceLoader
import arches.app.utils.data_management.resources.remover as resource_remover
import arches.app.utils.data_management.resource_graphs.exporter as graph_exporter
from arches.app.utils.data_management.resources.exporter import ResourceExporter
import arches.app.utils.index_database as index_database
from arches.management.commands import utils
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.models import models
import csv
import arches.app.utils.backlogids as create_backlog
from arches.app.utils.FixingMethods import LegacyIdsFixer,IndexConceptFixer
from arches.app.utils.load_relations import LoadRelations,UnloadRelations

class Command(BaseCommand):
    """
    Commands for managing the loading and running of packages in Arches

    """
    
    option_list = BaseCommand.option_list + (
        make_option('-o', '--operation', action='store', dest='operation', default='setup',
            type='choice', choices=['setup', 'install', 'setup_db', 'start_elasticsearch', 'setup_elasticsearch', 'build_permissions', 'livereload', 'load_resources', 'remove_resources', 'load_concept_scheme', 'index_database','export_resource_graphs','export_resources','create_backlog', 'remove_resources_from_csv', 'legacy_fixer', 'load_relations', 'unload_relations', 'delete_indices'],
            help='Operation Type; ' +
            '\'setup\'=Sets up Elasticsearch and core database schema and code' + 
            '\'setup_db\'=Truncate the entire arches based db and re-installs the base schema' + 
            '\'install\'=Runs the setup file defined in your package root' + 
            '\'start_elasticsearch\'=Runs the setup file defined in your package root' + 
            '\'build_permissions\'=generates "add,update,read,delete" permissions for each entity mapping'+
            '\'livereload\'=Starts livereload for this package on port 35729'),
        make_option('-s', '--source', action='store', dest='source', default='',
            help='Directory containing a .arches or .shp file containing resource records'),
        make_option('-f', '--format', action='store', dest='format', default='arches',
            help='Format: shp or arches'),
        make_option('-l', '--load_id', action='store', dest='load_id',
            help='Text string identifying the resources in the data load you want to delete.'),
        make_option('-d', '--dest_dir', action='store', dest='dest_dir',
            help='Directory where you want to save exported files.'),
        make_option('-a', '--append', action='store_true', dest='appending',
            help='Select this option to append data at the end of a resource'),
    )

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

        if options['operation'] == 'start_elasticsearch':
            self.start_elasticsearch(package_name)

        if options['operation'] == 'setup_elasticsearch':
            self.setup_elasticsearch(package_name)

        if options['operation'] == 'livereload':
            self.start_livereload()

        if options['operation'] == 'build_permissions':
            self.build_permissions()

        if options['operation'] == 'load_resources':
            self.load_resources(package_name, options['source'], options['appending'])
            
        if options['operation'] == 'remove_resources':     
            self.remove_resources(options['load_id'])
        
        if options['operation'] == 'remove_resources_from_csv':     
            self.remove_resources_from_csv(options['source'])

        if options['operation'] == 'load_concept_scheme':
            self.load_concept_scheme(package_name, options['source'])

        if options['operation'] == 'index_database':
            self.index_database(package_name)

        if options['operation'] == 'export_resource_graphs':
            self.export_resource_graphs(package_name, options['dest_dir'])

        if options['operation'] == 'export_resources':
            self.export_resources(package_name, options['dest_dir'])
        
        if options['operation'] == 'create_backlog':
            self.create_backlog()
        if options['operation'] == 'legacy_fixer':
            self.legacy_fixer(options['source'])
        if options['operation'] == 'load_relations':
            self.load_relations(options['source'])
        if options['operation'] == 'unload_relations':
            self.unload_relations(options['source'])
        if options['operation'] == 'delete_indices':
            self.delete_indices(options['source'])
            
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

        module = import_module('%s.setup' % package_name)
        install = getattr(module, 'install')
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

        try:
            unzip_file(os.path.join(settings.ROOT_DIR, 'install', file_name), install_root)
        except:
            download_elasticsearch(os.path.join(settings.ROOT_DIR, 'install'))

        es_config_directory = os.path.join(install_location, 'config')
        try:
            os.rename(os.path.join(es_config_directory, 'elasticsearch.yml'), os.path.join(es_config_directory, 'elasticsearch.yml.orig'))
        except: pass

        with open(os.path.join(es_config_directory, 'elasticsearch.yml'), 'w') as f:
            f.write('# ----------------- FOR TESTING ONLY -----------------')
            f.write('\n# - THESE SETTINGS SHOULD BE REVIEWED FOR PRODUCTION -')
            f.write('\nnode.max_local_storage_nodes: 1')
            f.write('\nindex.number_of_shards: 1')
            f.write('\nindex.number_of_replicas: 0')
            f.write('\nhttp.port: %s' % port)
            f.write('\ndiscovery.zen.ping.multicast.enabled: false')
            f.write('\ndiscovery.zen.ping.unicast.hosts: ["localhost"]')
            f.write('\ncluster.routing.allocation.disk.threshold_enabled: false')

        # install plugin
        if sys.platform == 'win32':
            os.system("call %s --install mobz/elasticsearch-head" % (os.path.join(install_location, 'bin', 'plugin.bat')))
        else:
            os.chdir(os.path.join(install_location, 'bin'))
            os.system("chmod u+x plugin")
            os.system("./plugin -install mobz/elasticsearch-head")
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
        install_path = os.path.join(settings.ROOT_DIR, 'db', 'install', 'install_db.sql')  
        db_settings['truncate_path'] = truncate_path
        db_settings['install_path'] = install_path   
        
        truncate_db.create_sqlfile(db_settings, truncate_path)
        install_db.create_sqlfile(db_settings, install_path)
        
        os.system('psql -h %(HOST)s -p %(PORT)s -U %(USER)s -d postgres -f "%(truncate_path)s"' % db_settings)
        os.system('psql -h %(HOST)s -p %(PORT)s -U %(USER)s -d %(NAME)s -f "%(install_path)s"' % db_settings)

        self.create_groups()
        self.create_users()

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

    def create_groups(self):
        """
        Creates read and edit groups.
        """

        from django.contrib.auth.models import User, Group

        edit_group = Group.objects.create(name='edit')
        read_group = Group.objects.create(name='read')

    def create_users(self):
        """
        Creates anonymous user and adds anonymous and admin user to appropriate groups.
        """

        from django.contrib.auth.models import User, Group

        anonymous_user = User.objects.create_user('anonymous', '', '')
        read_group = Group.objects.get(name='read')
        anonymous_user.groups.add(read_group)

        edit_group = Group.objects.get(name='edit')
        admin_user = User.objects.get(username='admin')
        admin_user.groups.add(edit_group)
        admin_user.groups.add(read_group)

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
                content_type = ContentType.objects.get_or_create(name='Arches', app_label=resourcetype, model=entitytype)
                Permission.objects.create(codename='add_%s' % entitytype, name='%s - add' % entitytype , content_type=content_type[0])
                Permission.objects.create(codename='update_%s' % entitytype, name='%s - update' % entitytype , content_type=content_type[0])
                Permission.objects.create(codename='read_%s' % entitytype, name='%s - read' % entitytype , content_type=content_type[0])
                Permission.objects.create(codename='delete_%s' % entitytype, name='%s - delete' % entitytype , content_type=content_type[0])

    def load_resources(self, package_name, data_source=None, appending = False):
        """
        Runs the setup.py file found in the package root

        """
        data_source = None if data_source == '' else data_source
        module = import_module('%s.setup' % package_name)
        load = getattr(module, 'load_resources')
        ResourceLoader().load(data_source, appending) 

    def remove_resources(self, load_id = None):
        """
        Runs the resource_remover command found in package_utils

        """
        if load_id == None:
            resource_remover.truncate_resources()
        else: 
            resource_remover.delete_resources(load_id)
          
    def remove_resources_from_csv(self, data_source):
      
        resource_remover.delete_resources_from_csv(data_source)

    def load_concept_scheme(self, package_name, data_source=None):
        """
        Runs the setup.py file found in the package root

        """
        data_source = None if data_source == '' else data_source
        module = import_module('%s.setup' % package_name)
        load = getattr(module, 'load_authority_files')
        load(data_source) 

    def index_database(self, package_name):
        """
        Runs the index_database command found in package_utils
        """
        # self.setup_indexes(package_name)
        index_database.index_db()

    def export_resource_graphs(self, package_name, data_dest=None):
        """
        Exports resource graphs to csv files
        """
        graph_exporter.export(data_dest)

    def export_resources(self, package_name, data_dest=None):
        """
        Exports resources to archesjson
        """
        resource_exporter = ResourceExporter('json')
        resource_exporter.export(search_results=False, dest_dir=data_dest)
        related_resources = [{'RESOURCEID_FROM':rr.entityid1, 'RESOURCEID_TO':rr.entityid2,'RELATION_TYPE':rr.relationshiptype,'START_DATE':rr.datestarted,'END_DATE':rr.dateended,'NOTES':rr.notes} for rr in models.RelatedResource.objects.all()] 
        relations_file = os.path.splitext(data_dest)[0] + '.relations'
        with open(relations_file, 'w') as f:
            csvwriter = csv.DictWriter(f, delimiter='|', fieldnames=['RESOURCEID_FROM','RESOURCEID_TO','START_DATE','END_DATE','RELATION_TYPE','NOTES'])
            csvwriter.writeheader()
            for csv_record in related_resources:
                csvwriter.writerow({k: str(v).encode('utf8') for k, v in csv_record.items()})
                
    def legacy_fixer(self, source):
        LegacyIdsFixer(source)

    def load_relations(self, source):
        LoadRelations(source)
        
    def unload_relations(self, source):
        UnloadRelations(source)
        
    def delete_indices(self, source):
        IndexConceptFixer(source)
        
    def start_livereload(self):
        from livereload import Server
        server = Server()
        for path in settings.STATICFILES_DIRS:
            server.watch(path)
        for path in settings.TEMPLATE_DIRS:
            server.watch(path)
        server.serve(port=settings.LIVERELOAD_PORT)

    def create_backlog(self):
        print "Function called"
        create_backlog.createBacklogIds()