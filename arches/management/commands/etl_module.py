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

import uuid
from django.core.management.base import BaseCommand
from arches.app.models.models import ETLModule
from arches.app.utils import module_importer


class Command(BaseCommand):
    """
    Commands for managing Arches etl modules

    """

    def add_arguments(self, parser):
        parser.add_argument("operation", nargs="?")

        parser.add_argument(
            "-s",
            "--source",
            action="store",
            dest="source",
            default="",
            help="Extension file to be loaded",
        )

        parser.add_argument(
            "-n",
            "--name",
            action="store",
            dest="name",
            default="",
            help="The name of the extension to unregister",
        )

    def handle(self, *args, **options):
        if options["operation"] == "register":
            self.register(source=options["source"])

        if options["operation"] == "unregister":
            self.unregister(name=options["name"])

        if options["operation"] == "list":
            self.list()

    def start(self, dest_dir):
        """
        Creates a template etlmodule

        """

    def register(self, source):
        """
        Inserts a etlmodule into the arches db

        """

        module = module_importer.get_module(source)
        details = module.details

        try:
            uuid.UUID(details["etlmoduleid"])
        except:
            details["etlmoduleid"] = str(uuid.uuid4())

        etl_module = ETLModule(**details)
        etl_module.save()

    def unregister(self, name):
        """
        Removes an etl module from the system

        """
        try:
            etl_module = ETLModule.objects.filter(name=name)
            etl_module[0].delete()
        except Exception as e:
            print(e)

    def list(self):
        """
        Lists registered modules

        """
        try:
            etl_modules = ETLModule.objects.all()
            for etl_module in etl_modules:
                print(etl_module.name)
        except Exception as e:
            print(e)
