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
from glob import glob
from pprint import pprint as pp
from arches.management.commands import utils
from arches.app.models import models
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
            help="operation 'list' lists orphaned files, \
                            'remove' deletes orphaned files",
        )
        parser.add_argument("accept_defaults", nargs="?", default="n", help="'y' accepts all defaults")

    def handle(self, *args, **options):
        accept_defaults = False
        if options["accept_defaults"].lower() in ("y", "t"):
            accept_defaults = True
        if options["operation"] == "list":
            self.print_orphans()
        if options["operation"] == "remove":
            self.remove_files(accept_defaults)

    def list_orphans(self):
        saved_files = models.File.objects.all()
        saved_file_names = {os.path.basename(f.path.path) for f in saved_files}
        uploaded_paths = glob(os.path.join(settings.MEDIA_ROOT, "uploadedfiles", "*"))
        uploaded_names = {os.path.basename(path) for path in uploaded_paths}
        orphans = list(uploaded_names.difference(saved_file_names))
        return orphans, uploaded_paths

    def print_orphans(self):
        orphans, uploaded_paths = self.list_orphans()
        res = "orphans: {} uploaded: {}".format(len(orphans), len(uploaded_paths))
        pp(orphans)
        pp(res)

    def delete(self, orphans, uploaded_paths):
        for path in uploaded_paths:
            if os.path.basename(path) in orphans:
                os.remove(path)

    def remove_files(self, accept_defaults):
        orphans, uploaded_paths = self.list_orphans()
        if accept_defaults is False:
            pp(orphans)
            message = "Do you want to delete the above files?"
            if utils.get_yn_input(message) is True:
                print("deleting files")
                self.delete(orphans, uploaded_paths)
            else:
                print("not deleting")
        else:
            print("deleting files")
            self.delete(orphans, uploaded_paths)
