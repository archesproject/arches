"""
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
"""

import os
import logging
import urllib.request, urllib.error, urllib.parse
import json
from urllib.parse import urlparse, urljoin
from arches.management.commands import utils
from arches.app.models.mobile_survey import MobileSurvey
from arches.app.models.models import MobileSyncLog
from arches.app.models.system_settings import settings
from django.core.management.base import BaseCommand, CommandError
from arches.app.utils.couch import Couch

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Commands for managing Arches collector projects

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "operation",
            nargs="?",
            choices=["list_surveys", "delete_surveys", "delete_unassociated_surveys", "sync_survey", "rebuild_surveys"],
            help="Operation Type; "
            + "'delete_surveys' deletes all surveys that belong to the current arches install"
            + "'delete_unassociated_surveys' deletes all surveys that do not belong to the current arches install"
            + "'sync_survey' sync all survey databases (couch) with arches"
            + "'rebuild_surveys' rebuilds all surveys that belong to the current arches install",
        )
        parser.add_argument("-id", "--id", dest="id", default=None, help="UUID of Survey")
        parser.add_argument("-u", "--user", dest="user", default=None, help="UUID of Survey")

    def handle(self, *args, **options):
        if options["operation"] == "list_surveys":
            for mobile_survey in MobileSurvey.objects.all():
                logger.info("{0}: {1} ({2})".format(mobile_survey.name, mobile_survey.id, "Active" if mobile_survey.active else "Inactive"))

        if options["operation"] == "delete_surveys":
            self.delete_associated_surveys()

        if options["operation"] == "rebuild_surveys":
            self.rebuild_couch_surveys()

        if options["operation"] == "delete_unassociated_surveys":
            self.delete_unassociated_surveys()

        if options["operation"] == "sync_survey":
            if options["id"] is not None:
                self.sync_survey(options["id"], options["user"])
            else:
                for mobile_survey in MobileSurvey.objects.all():
                    self.sync_survey(mobile_survey.id)

    def sync_survey(self, uuid, userid=None):
        mobile_survey = MobileSurvey.objects.get(id=uuid)
        synclog = MobileSyncLog(userid=userid, survey=mobile_survey)
        synclog.save()
        logger.info("Syncing {0} from CouchDB to PostgreSQL".format(mobile_survey.name))
        mobile_survey.push_edits_to_db(synclog, user)
        synclog.save()

    def delete_associated_surveys(self):
        couch = Couch()
        surveys = [str(msm["id"]) for msm in MobileSurvey.objects.values("id")]
        for survey in surveys:
            couch.delete_db("project_" + str(survey))

    def delete_unassociated_surveys(self):
        couch = Couch()
        surveys = [str(msm["id"]) for msm in MobileSurvey.objects.values("id")]
        couchdbs = [dbname for dbname in couch.couch]
        for db in couchdbs:
            survey_id = db[-36:]
            if survey_id not in surveys:
                if "project" in db:
                    couch.delete_db("project_" + str(survey_id))

    def create_associated_surveys(self):
        for mobile_survey in MobileSurvey.objects.all():
            logger.info("Writing {0} to CouchDB".format(mobile_survey.name))
            mobile_survey.save()

    def rebuild_couch_surveys(self):
        self.delete_associated_surveys()
        self.create_associated_surveys()
