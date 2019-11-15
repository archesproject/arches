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
import uuid
from arches.management.commands import utils
from arches.app.models import models
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError


class Command(BaseCommand):
    """
    Commands for managing Arches functions

    """

    def add_arguments(self, parser):
        parser.add_argument("operation", nargs="?")

        parser.add_argument("-s", "--source", action="store", dest="source", default="", help="Widget json file to be loaded")

        parser.add_argument("-n", "--name", action="store", dest="name", default="", help="The name of the report template to unregister")

    def handle(self, *args, **options):
        if options["operation"] == "register":
            self.register(source=options["source"])

        if options["operation"] == "unregister":
            self.unregister(name=options["name"])

        if options["operation"] == "list":
            self.list()

        if options["operation"] == "update":
            self.update(source=options["source"])

    def register(self, source):
        """
        Inserts a report template into the arches db

        """
        import json

        details = {}

        with open(source) as f:
            details = json.load(f)

        try:
            uuid.UUID(details["templateid"])
        except:
            details["templateid"] = str(uuid.uuid4())
            print("Registering report template with templateid: {}".format(details["templateid"]))

        instance = models.ReportTemplate(
            templateid=details["templateid"],
            name=details["name"],
            description=details["description"],
            component=details["component"],
            componentname=details["componentname"],
            defaultconfig=details["defaultconfig"],
        )

        instance.save()
