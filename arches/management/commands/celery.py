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

import subprocess
from arches.management.commands import utils
from arches.app.models.system_settings import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Commands for managing Arches functions

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "operation",
            nargs="?",
            help="operation 'start' starts a celery worker for your project",
        )
        parser.add_argument(
            "-b",
            "--beat",
            action="store_true",
            dest="beat",
            help="Includes the beat worker with your celery worker",
        )

    def handle(self, *args, **options):
        if options["operation"] == "start":
            self.start_worker(options["beat"])

    def start_worker(self, beat):
        if beat is True:
            cmd = f"celery -A {settings.ELASTICSEARCH_PREFIX} worker -B -l info"
        else:
            cmd = f"celery -A {settings.ELASTICSEARCH_PREFIX} worker -l info"
        cmd_process = cmd.split()
        subprocess.call(cmd_process)
