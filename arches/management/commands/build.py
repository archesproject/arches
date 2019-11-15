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

from django.core.management.base import BaseCommand, CommandError
from django.core import management
from arches.app.models.system_settings import settings


class Command(BaseCommand):
    """A general command used in compiling all the required static data files and js file in Arches."""

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--operation",
            action="store",
            dest="operation",
            default="collectstatic",
            choices=["collectstatic"],
            help="Operation Type; collectstatic=Alias for the collectstatic command provided by django",
        )

    def handle(self, *args, **options):
        print("operation: " + options["operation"])
        if options["operation"] == "collectstatic":
            if settings.STATIC_ROOT != "":
                management.call_command("collectstatic", interactive=False)
