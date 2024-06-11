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

"""This module contains commands for building Arches."""

import os
import sys

from arches.management.commands import utils
from arches.app.models import models
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Commands for managing datatypes

    """

    def add_arguments(self, parser):
        parser.add_argument("operation", nargs="?")

        parser.add_argument(
            "-s",
            "--source",
            action="store",
            dest="dt_source",
            default="",
            help="Datatype file to be loaded",
        )

        parser.add_argument(
            "-d",
            "--datatype",
            action="store",
            dest="datatype",
            default="",
            help="The name of the datatype to unregister",
        )

    def handle(self, *args, **options):
        if options["operation"] == "register":
            self.register(source=options["dt_source"])

        if options["operation"] == "update":
            self.update(source=options["dt_source"])

        if options["operation"] == "unregister":
            self.unregister(datatype=options["datatype"])

        if options["operation"] == "list":
            self.list()

    def register(self, source):
        """
        Inserts a datatype into the arches db

        """
        utils.load_source("dt_source", source)
        details = sys.modules["dt_source"].details
        self.validate_details(details)

        dt = models.DDataType(
            datatype=details["datatype"],
            iconclass=details["iconclass"],
            modulename=os.path.basename(source),
            classname=details["classname"],
            defaultwidget=details["defaultwidget"],
            defaultconfig=details["defaultconfig"],
            configcomponent=details["configcomponent"],
            configname=details["configname"],
            isgeometric=details["isgeometric"],
            issearchable=details["issearchable"],
        )

        if len(models.DDataType.objects.filter(datatype=dt.datatype)) == 0:
            dt.save()
        else:
            print("{0} already exists".format(dt.datatype))

    def validate_details(self, details):
        try:
            details["issearchable"]
        except KeyError:
            details["issearchable"] = False

    def unregister(self, datatype):
        """
        Removes a datatype from the system

        """
        try:
            dt = models.DDataType.objects.filter(datatype=datatype)
            print(dt)
            dt[0].delete()
        except Exception as e:
            print(e)

    def update(self, source):
        """
        Updates an existing datatype in the arches db

        """
        utils.load_source("dt_source", source)
        details = sys.modules["dt_source"].details
        self.validate_details(details)

        instance = models.DDataType.objects.get(datatype=details["datatype"])
        instance.iconclass = details["iconclass"]
        instance.modulename = os.path.basename(source)
        instance.classname = details["classname"]
        instance.defaultwidget = details["defaultwidget"]
        instance.defaultconfig = details["defaultconfig"]
        instance.configcomponent = details["configcomponent"]
        instance.configname = details["configname"]
        instance.isgeometric = details["isgeometric"]
        instance.issearchable = details["issearchable"]

        instance.save()

    def list(self):
        """
        Lists registered functions

        """
        try:
            dt = models.DDataType.objects.all()
            for datatype in dt:
                print(datatype.datatype)
        except Exception as e:
            print(e)
