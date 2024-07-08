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
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Commands for managing the loading and running of packages in Arches

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--source",
            action="store",
            dest="source",
            default="",
            help="A self executing python file.",
        )

    def handle(self, *args, **options):
        self.run_patch_file(options["source"])

    def run_patch_file(self, data_source=None):
        """
        Runs the setup.py file found in the package root

        """
        data_source = None if data_source == "" else data_source
        if data_source:
            module_name = os.path.basename(data_source).split(".")[0]
            apps.import_string("arches.management.patches.%s" % module_name)
        else:
            print("You need to specify a file with the -s option")
