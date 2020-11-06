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

import requests
import textwrap
import argparse
import glob
import os
from django.core.management.base import BaseCommand
from arches.app.models.system_settings import settings


class ArchesHelpTextFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        ret = []
        for line in text.splitlines():
            ret = ret + [line if index == 0 else f"     {line}" for index, line in enumerate(textwrap.wrap(line.strip(), width))]
        return ret


class Command(BaseCommand):
    """
    Commands for running common elasticsearch commands

    """

    def __init__(self, *args, **kwargs):
        self.baseurl = f"{settings.KIBANA_URL}{settings.KIBANA_CONFIG_BASEPATH}"
        self.headers = {"kbn-xsrf": "true"}
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.formatter_class = ArchesHelpTextFormatter
        parser.add_argument(
            "operation",
            nargs="?",
            choices=["add_space", "delete_space", "load"],
            help="Operation Type;\n"
            + BaseCommand().style.SUCCESS("add_space")
            + " = Creates an Arches managed space in Kibana if no name is provided otherwise creates the space with the passed in name\n"
            + BaseCommand().style.SUCCESS("delete_space")
            + " = Deletes an Arches managed space in Kibana if no name is provided otherwise deletes the space with the passed in name\n"
            + BaseCommand().style.SUCCESS("load")
            + " = Loads Kibana objects/dashboards provided by .ndjson files into an existing or new space\n",
        )

        parser.add_argument("-n", "--name", action="store", dest="name", default="", help="Name of Kibana space.")

        parser.add_argument(
            "-s", "--source_dir", action="store", dest="source_dir", default="", help="Directory where Kibana .ndjson files are stored."
        )

        parser.add_argument("-ow", "--overwrite", action="store_true", dest="overwrite", help="Overwirte existing objects.")

        parser.add_argument(
            "-y", "--yes", action="store_true", dest="yes", help='Used to force a yes answer to any user input "continue? y/n" prompt'
        )

    def handle(self, *args, **options):
        if options["operation"] == "add_space":
            self.setup_kibana_space(space_name=options["name"])

        if options["operation"] == "delete_space":
            self.delete_kibana_space(space_name=options["name"], force=options["yes"])

        if options["operation"] == "load":
            self.upload_kibana_objects(
                space_name=options["name"], source=options["source_dir"], overwrite=options["overwrite"], force=options["yes"]
            )

    def setup_kibana_space(self, space_name=""):
        try:
            name = settings.ELASTICSEARCH_PREFIX if space_name == "" else space_name
            url = f"{self.baseurl}/api/spaces/space"
            values = {
                "id": f"{name}",
                "name": f"{name}",
            }
            req = requests.post(url, data=values, headers=self.headers)
            if req.status_code == 200:
                self.stdout.write(self.style.SUCCESS(f"Space '{name}' successfully created"))
            else:
                self.stdout.write(self.style.ERROR(f"ERROR - {req.json()['message']}"))
        except requests.exceptions.ConnectionError:
            self.stdout.write(self.style.WARNING(f"Kibana is not running, the Kibana space wasn't created."))

    def delete_kibana_space(self, space_name="", force=False):
        try:
            name = settings.ELASTICSEARCH_PREFIX if space_name == "" else space_name
            url = f"{self.baseurl}/api/spaces/space/{name}"
            if force is False:
                yes_no = input(
                    f'Deleting the space "{name}" will permanently removes the space and all of its contents. You can\'t undo this action. Do you want to delete it? Y/N:  '
                )
            if force is True or yes_no.upper() == "Y":
                req = requests.delete(url=url, headers=self.headers)
                if req.status_code == 204:
                    self.stdout.write(self.style.SUCCESS(f"Space '{name}' successfully deleted"))
                elif req.status_code == 404:
                    self.stdout.write(self.style.ERROR(f"ERROR - space '{name}' not found"))
                else:
                    self.stdout.write(self.style.ERROR(f"ERROR - {req.json()['message']}"))
        except requests.exceptions.ConnectionError:
            self.stdout.write(self.style.WARNING(f"Kibana is not running, the Kibana space wasn't deleted."))

    def upload_kibana_objects(self, space_name="", source="", overwrite=False, force=False):
        try:
            name = settings.ELASTICSEARCH_PREFIX if space_name == "" else space_name

            # first check to see if the kibana space exists
            req = requests.get(url=f"{self.baseurl}/api/spaces/space/{name}")
            if req.status_code != 200:
                if force is True:
                    self.setup_kibana_space(space_name=name)
                else:
                    yes_no = input(f'The Kibana space name specified "{name}" doesn\'t exist. Do you want to create it? Y/N:  ')
                    if yes_no.upper() == "Y":
                        self.setup_kibana_space(space_name=name)

            # now try to figure out if we can find the appropriate .ndjson files to load
            if source == "":
                in_project = os.path.isfile(os.path.join(os.getcwd(), "manage.py"))
                if not in_project:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Please run this command from the directory where manage.py resides or supply a source file/directory"
                        )
                    )
                    return
                else:
                    index_files = glob.glob(os.path.join("**", "pkg", "kibana_objects", "*.ndjson"))
            else:
                if source.endswith(".ndjson"):
                    if os.path.isfile(source):
                        index_files = [source]
                    else:
                        self.stdout.write(self.style.ERROR(f"Source file not found at: {source}"))
                else:
                    index_files = glob.glob(os.path.join(source, "*.ndjson"))

            # load the .ndjson files if any
            url = f"{self.baseurl}/s/{name}/api/saved_objects/_import"
            if len(index_files) > 0:
                for index_file in index_files:
                    files = {"file": open(index_file, "rb")}
                    req = requests.post(url, files=files, headers=self.headers, params={"overwrite": str(overwrite).lower()})
                    if req.status_code == 200:
                        if req.json()["success"]:
                            self.stdout.write(self.style.SUCCESS(f"Loaded: {index_file}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"Errors when loading: {index_file}"))
                            self.stdout.write(self.style.SUCCESS(f"{req.json()['successCount']} items loaded successfully"))
                            for error in req.json()["errors"]:
                                name = error["title"] if "title" in error else error["id"]
                                self.stdout.write(self.style.ERROR(f"{error['error']['type']} - type: {error['type']} - name/id: {name}"))
                    elif req.status_code == 404:
                        self.stdout.write(self.style.ERROR(f"ERROR - space '{name}' not found"))
                    else:
                        self.stdout.write(self.style.ERROR(f"ERROR - {req.json()['message']}"))
            else:
                self.stdout.write(self.style.ERROR(f"No '.ndjson' files found!"))
        except requests.exceptions.ConnectionError:
            self.stdout.write(self.style.WARNING(f"Kibana is not running, no objects were loaded."))
            if force is False:
                yes_no = input(f"Would you like to start Kibana and try again? Y/N:  ")
                if yes_no.upper() == "Y":
                    self.upload_kibana_objects(space_name=space_name, source=source, overwrite=overwrite, force=force)
