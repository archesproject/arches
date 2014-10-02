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

class Command(BaseCommand):
    """
    Commands for managing the loading and running of packages in Arches

    """
    
    option_list = BaseCommand.option_list + (
        make_option('-o', '--operation', action='store', dest='operation', default='setup',
            type='choice', choices=['setup', 'install', 'start_elasticsearch', 'build_permissions'],
            help='Operation Type; ' +
            '\'setup\'=Sets up Elasticsearch and core database schema and code' + 
            '\'install\'=Runs the setup file defined in your package root' + 
            '\'start_elasticsearch\'=Runs the setup file defined in your package root' + 
            '\'build_permissions\'=generates "add,update,read,delete" permissions for each entity mapping'),
    )

    def handle(self, *args, **options):
        print 'operation: '+ options['operation']
        package_name = settings.PACKAGE_NAME
        print 'package: '+ package_name
        
        if options['operation'] == 'setup':
            self.setup(package_name)

        if options['operation'] == 'install':
            self.install(package_name)

        if options['operation'] == 'start_elasticsearch':
            self.start_elasticsearch(package_name)

        if options['operation'] == 'build_permissions':
            self.build_permissions()
                
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
        url = get_elasticsearch_download_url()
        file_name = url.split('/')[-1]

        try:
            unzip_file(os.path.join(settings.ROOT_DIR, 'install', file_name), install_root)
        except:
            download_elasticsearch()

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
            p = subprocess.Popen('elasticsearch.bat', cwd=es_start, shell=True)  
        else:
            p = subprocess.Popen(es_start + '/elasticsearch', cwd=es_start, shell=False)  

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

    def generate_procfile(self, package_name):
        """
        Generate a procfile for use with Honcho (https://honcho.readthedocs.org/en/latest/)

        """

        python_exe = os.path.abspath(sys.executable)

        with open(os.path.join(settings.PACKAGE_ROOT, '..', 'Procfile'), 'w') as f:
            f.write('elasticsearch: %s' % os.path.join(self.get_elasticsearch_install_location(package_name), 'bin', 'elasticsearch'))
            f.write('\ndjango: %s manage.py runserver' % (python_exe))

    def get_elasticsearch_install_location(self, package_name):
        """
        Get the path to the Elasticsearch install

        """

        url = get_elasticsearch_download_url()
        file_name = url.split('/')[-1]
        file_name_wo_extention = file_name[:-4]
        return os.path.join(settings.PACKAGE_ROOT, 'elasticsearch', file_name_wo_extention)

    def build_permissions(self):
        """
        Creates permissions based on all the installed resource types

        """

        from arches.app.models import models
        from django.contrib.auth.models import Permission, ContentType

        mappings = models.Mappings.objects.all()
        for mapping in mappings:
            content_type = ContentType.objects.get_or_create(name='Arches', app_label=mapping.entitytypeidfrom, model=mapping.entitytypeidto)
            Permission.objects.create(codename='add_%s' % mapping.entitytypeidto, name='%s - add' % mapping.entitytypeidto , content_type=content_type[0])
            Permission.objects.create(codename='update_%s' % mapping.entitytypeidto, name='%s - update' % mapping.entitytypeidto , content_type=content_type[0])
            Permission.objects.create(codename='read_%s' % mapping.entitytypeidto, name='%s - read' % mapping.entitytypeidto , content_type=content_type[0])
            Permission.objects.create(codename='delete_%s' % mapping.entitytypeidto, name='%s - delete' % mapping.entitytypeidto , content_type=content_type[0])
