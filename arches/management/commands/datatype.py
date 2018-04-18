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
from arches.management.commands import utils
from arches.app.models import models
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Commands for managing datatypes

    """

    def add_arguments(self, parser):
        parser.add_argument('operation', nargs='?')

        parser.add_argument('-s', '--source', action='store', dest='dt_source', default='',
            help='Datatype file to be loaded')

        parser.add_argument('-d', '--datatype', action='store', dest='datatype', default='',
            help='The name of the datatype to unregister')

    def handle(self, *args, **options):
        if options['operation'] == 'register':
            self.register(source=options['dt_source'])

        if options['operation'] == 'unregister':
            self.unregister(datatype=options['datatype'])

        if options['operation'] == 'list':
            self.list()

    def register(self, source):
        """
        Inserts a datatype into the arches db

        """

        import imp
        fn_config = imp.load_source('', source)
        details = fn_config.details

        dt = models.DDataType(
            datatype = details['datatype'],
            iconclass = details['iconclass'],
            modulename = os.path.basename(source),
            classname = details['classname'],
            defaultwidget = details['defaultwidget'],
            defaultconfig = details['defaultconfig'],
            configcomponent = details['configcomponent'],
            configname = details['configname'],
            isgeometric = details['isgeometric']
            )


        if len(models.DDataType.objects.filter(datatype=dt.datatype)) == 0:
            dt.save()
        else:
            print "{0} already exists".format(dt.datatype)

    def unregister(self, datatype):
        """
        Removes a datatype from the system

        """
        try:
            fn = models.DDataType.objects.filter(datatype=datatype)
            fn[0].delete()
        except Exception as e:
            print e

    def list(self):
        """
        Lists registered functions

        """
        try:
            dt = models.DDataType.objects.all()
            for datatype in dt:
                print datatype.datatype
        except Exception as e:
            print e
