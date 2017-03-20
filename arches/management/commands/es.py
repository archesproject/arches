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

import os
from arches.setup import get_elasticsearch_download_url, download_elasticsearch, unzip_file
from arches.management.commands import utils
from arches.app.search.mappings import prepare_term_index, delete_term_index, delete_search_index, prepare_resource_relations_index, delete_resource_relations_index
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Commands for running common elasticsearch commands

    """

    def add_arguments(self, parser):
        parser.add_argument('operation', nargs='?')

        parser.add_argument('-d', '--dest_dir', action='store', dest='dest_dir', default='',
            help='Directory from where you want to run elasticsearch.')

        parser.add_argument('-p', '--port', action='store', dest='port', default=settings.ELASTICSEARCH_HTTP_PORT,
            help='Port to use for elasticsearch.')


    def handle(self, *args, **options):
        if options['operation'] == 'install':
            self.install(install_location=options['dest_dir'], port=options['port'])

        # if options['operation'] == 'start':
        #     self.start(install_location=options['dest_dir'])

        if options['operation'] == 'setup_indexes':
            self.setup_indexes()

        if options['operation'] == 'delete_indexes':
            self.delete_indexes()

    def install(self, install_location=None, port=None):
        """
        Installs Elasticsearch into the package directory and
        adds default settings for running in a test environment

        Change these settings in production

        """

        install_location = os.path.abspath(install_location)
        utils.ensure_dir(install_location)

        url = get_elasticsearch_download_url(os.path.join(settings.ROOT_DIR, 'install'))
        file_name = url.split('/')[-1]
        file_name_wo_extention, extention = os.path.splitext(file_name)

        download_elasticsearch(os.path.join(settings.ROOT_DIR, 'install'))
        unzip_file(os.path.join(settings.ROOT_DIR, 'install', file_name), install_location)

        es_config_directory = os.path.join(install_location, file_name_wo_extention, 'config')
        try:
            os.rename(os.path.join(es_config_directory, 'elasticsearch.yml'), os.path.join(es_config_directory, 'elasticsearch.yml.orig'))
        except: pass

        os.chmod(os.path.join(install_location, file_name_wo_extention, 'bin', 'elasticsearch'), 0755)

        with open(os.path.join(es_config_directory, 'elasticsearch.yml'), 'w') as f:
            f.write('# ----------------- FOR TESTING ONLY -----------------')
            f.write('\n# - THESE SETTINGS SHOULD BE REVIEWED FOR PRODUCTION -')
            f.write('\n# -https://www.elastic.co/guide/en/elasticsearch/reference/5.0/system-config.html - ')
            f.write('\nhttp.port: %s' % port)
            f.write('\nscript.inline: true')
            f.write('\n\n# for the elasticsearch-head plugin')
            f.write('\nhttp.cors.enabled: true')
            f.write('\nhttp.cors.allow-origin: "*"')
            f.write('\n')

        print 'Elasticsearch installed at %s' % os.path.join(install_location, file_name_wo_extention)

    # def start(self, install_location=None):
    #     """
    #     Starts the Elasticsearch process (blocking)
    #     WARNING: this will block all subsequent python calls

    #     """

    #     es_start = os.path.join(install_location, 'bin')
    #     print es_start

    #     # use this instead to start in a non-blocking way
    #     if sys.platform == 'win32':
    #         import time
    #         p = subprocess.Popen(['service.bat', 'install'], cwd=es_start, shell=True)
    #         time.sleep(10)
    #         p = subprocess.Popen(['service.bat', 'start'], cwd=es_start, shell=True)
    #     else:
    #         p = subprocess.Popen(es_start + '/elasticsearch', cwd=es_start, shell=False)
    #     return p

    def setup_indexes(self):
        prepare_term_index(create=True)
        prepare_resource_relations_index(create=True)

    def delete_indexes(self):
        delete_term_index()
        delete_search_index()
        delete_resource_relations_index()
