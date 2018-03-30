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


class Command(BaseCommand):
    """
    Commands for managing Arches mobile surveys

    """

    def add_arguments(self, parser):
        parser.add_argument('operation', nargs='?',
        help='operation \'clearcouch\' deletes all couch databases that do not belong to the current project')

    def handle(self, *args, **options):
        if options['operation'] == 'clearcouch':
            self.clear_couch()

    def clear_couch(self):
        surveys = [str(msm['id']) for msm in models.MobileSurveyModel.objects.values("id")]
        uri=urlparse(settings.COUCHDB_URL)
        couchserver = couchdb.Server(settings.COUCHDB_URL)
        couchdbs = [dbname for dbname in couchserver]
        for db in couchdbs:
            survey_id = db[-36:]
            print db
            if survey_id not in surveys:
                print 'deleting', db
                del couchserver[db]
            else:
                print 'keeping', db
