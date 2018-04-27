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

import os
import couchdb
import urllib2
import json
from urlparse import urlparse, urljoin
from arches.management.commands import utils
from arches.app.models import models
from arches.app.models.system_settings import settings
from django.core.management.base import BaseCommand, CommandError
from arches.app.utils.couch import clear_associated_surveys, clear_unassociated_surveys, create_associated_surveys


class Command(BaseCommand):
    """
    Commands for managing Arches mobile surveys

    """

    def add_arguments(self, parser):
        parser.add_argument('operation', nargs='?',
            choices=['clear_surveys', 'clear_unassociated_surveys', 'rebuild_surveys',],
            help='Operation Type; ' +
            # '\'install\'=Install\'s Elasticsearch in the provided location with the provided port' +
            # '\'setup_indexes\'=Creates the indexes in Elastic Search needed by the system' +
            '\'clear_surveys\' deletes all surveys that belong to the current arches install' +
            '\'clear_unassociated_surveys\' deletes all surveys that belong to the current arches install' +
            # '\'index_database\'=Indexes all the data (resources, concepts, and resource relations) found in the database' +
            # '\'index_concepts\'=Indxes all concepts from the database'+
            # '\'index_resources\'=Indexes all resources from the database'+
            '\'rebuild_surveys\' rebuilds all couch databases that belong to a current survey')

    def handle(self, *args, **options):
        if options['operation'] == 'clear_surveys':
            self.delete_couch_surveys()

        if options['operation'] == 'rebuild_surveys':
            self.rebuild_couch_surveys()

        if options['operation'] == 'clear_unassociated_surveys':
            self.clear_unassociated_surveys()

    def delete_couch_surveys(self):
        clear_associated_surveys()

    def clear_unassociated_surveys(self):
        clear_unassociated_surveys()

    def rebuild_couch_surveys(self):
        clear_associated_surveys()
        create_associated_surveys()
