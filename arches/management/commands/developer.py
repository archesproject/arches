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
from arches.management.commands import utils
from arches.app.models import models
from arches.app.models.system_settings import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Commands for managing Arches functions

    """

    def add_arguments(self, parser):
        parser.add_argument("operation", nargs="?", help="operation 'livereload' starts livereload for this project on port 35729")

    def handle(self, *args, **options):
        if options["operation"] == "livereload":
            self.start_livereload()

    def start_livereload(self):
        from livereload import Server

        server = Server()
        for path in settings.STATICFILES_DIRS:
            server.watch(path)
        for path in settings.TEMPLATES[0]["DIRS"]:
            server.watch(path)
        server.serve(port=settings.LIVERELOAD_PORT)
