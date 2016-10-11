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

from arches.app.models import models
from optparse import make_option
from formats.archesfile import ArchesReaderNew
from formats.archesjson import JsonReader
from formats.shpfile import ShapeReader


class ResourceLoader(object):

    def __init__(self):
        self.user = User()
        self.user.first_name = settings.ETL_USERNAME
        self.resources = []
        self.se = SearchEngineFactory().create()

    option_list = BaseCommand.option_list + (
        make_option('--source',
            action='store',
            dest='source',
            default='',
            help='.arches file containing resource records'),
         make_option('--format',
            action='store_true',
            default='arches',
            help='format extension that you would like to load: arches or shp'),
        )

    def load(self, source):
        file_name, file_format = os.path.splitext(source)
        archesjson = False
        if file_format == '.shp':
            # reader = ShapeReader()
            pass
        elif file_format == '.arches':
            reader = ArchesReader()
            print '\nVALIDATING ARCHES FILE ({0})'.format(source)
            # reader.validate_file(source)
            pass
        elif file_format == '.json':
            archesjson = True
            reader = JsonReaderNew()

        start = time()
        resources = reader.load_file(source)

        print '\nLOADING RESOURCES ({0})'.format(source)
        relationships = None
        related_resource_records = []
        relationships_file = file_name + '.relations'
        elapsed = (time() - start)
        print 'time to parse {0} resources = {1}'.format(file_name, elapsed)
        # results = self.resource_list_to_entities(resources, archesjson)
        pass
