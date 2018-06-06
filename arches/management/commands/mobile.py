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
import urllib2
import json
from urlparse import urlparse, urljoin
from arches.management.commands import utils
from arches.app.models.mobile_survey import MobileSurvey
from arches.app.models.system_settings import settings
from django.core.management.base import BaseCommand, CommandError
from arches.app.utils.couch import Couch


class Command(BaseCommand):
    """
    Commands for managing Arches mobile surveys

    """

    def add_arguments(self, parser):
        parser.add_argument('operation', nargs='?',
            choices=['delete_surveys', 'delete_unassociated_surveys', 'rebuild_surveys',],
            help='Operation Type; ' +
            '\'delete_surveys\' deletes all surveys that belong to the current arches install' +
            '\'delete_unassociated_surveys\' deletes all surveys that do not belong to the current arches install' +
            '\'rebuild_surveys\' rebuilds all surveys that belong to the current arches install')

    def handle(self, *args, **options):
        if options['operation'] == 'delete_surveys':
            self.delete_associated_surveys()

        if options['operation'] == 'rebuild_surveys':
            self.rebuild_couch_surveys()

        if options['operation'] == 'delete_unassociated_surveys':
            self.delete_unassociated_surveys()

    def delete_associated_surveys(self):
        couch = Couch()
        surveys = [str(msm['id']) for msm in MobileSurvey.objects.values("id")]
        for survey in surveys:
            couch.delete_db('project_' + str(survey))

    def delete_unassociated_surveys(self):
        couch = Couch()
        surveys = [str(msm['id']) for msm in MobileSurvey.objects.values("id")]
        couchdbs = [dbname for dbname in couch.couch]
        for db in couchdbs:
            survey_id = db[-36:]
            if survey_id not in surveys:
                if 'project' in db:
                    couch.delete_db('project_' + str(survey_id))

    def create_associated_surveys(self):
        for mobile_survey in MobileSurvey.objects.all():
            print "Writing", mobile_survey, "to CouchDB"
            mobile_survey.save()

    def rebuild_couch_surveys(self):
        self.delete_associated_surveys()
        self.create_associated_surveys()
