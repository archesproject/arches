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
import subprocess
import gzip
from django.core.management.base import BaseCommand
from arches.app.models.system_settings import settings


class Command(BaseCommand):
    """
    Commands for running common database commands

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "operation",
            nargs="?",
            choices=["backup", "restore"],
            help="Operation Type; "
            + "'setup_indexes'=Creates a pg.dump file of your database in a destination directory"
            + "'delete_indexes'=Restores your database from a pg.dump file in a soure directory",
        )

        parser.add_argument("-d", "--dest_dir", action="store", dest="dest_dir", default="", help="Destination directory of the backup")

        parser.add_argument("-s", "--source_dir", action="store", dest="source_dir", default="", help="Source directory of a backup")

        parser.add_argument("-n", "--name ", action="store", dest="name", default=None, help="Name of the custom index")

    def handle(self, *args, **options):
        if options["operation"] == "backup":
            self.backup(options["dest_dir"])

        if options["operation"] == "restore":
            self.restore(options["source_dir"])

    def backup(self, dest):
        if os.path.exists(dest) is False:
            dest = os.path.join(os.getcwd(), dest)
        if os.path.exists(dest):
            print("backing up to", dest)
            output = os.path.join(dest, "backup.tar")
            print(settings.APP_NAME, output)
            cmd = f"pg_dump -U postgres -W -F t arches_her".split()
            with gzip.open(output, "wb") as f:
                popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                for stdout_line in iter(popen.stdout.readline, ""):
                    f.write(stdout_line)

                popen.stdout.close()
                popen.wait()

    def start_worker(self, beat):
        if beat is True:
            cmd = f"celery -A {settings.ELASTICSEARCH_PREFIX} worker -B -l info"
        else:
            cmd = f"celery -A {settings.ELASTICSEARCH_PREFIX} worker -l info"
        cmd_process = cmd.split()
        subprocess.call(cmd_process)

    def restore(self, src):
        print("restoring from", dest)
