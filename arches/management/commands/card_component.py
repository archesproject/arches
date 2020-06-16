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

        parser.add_argument("-n", "--name", action="store", dest="name", default="", help="The name of the widget to unregister")

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
        Inserts a card component into the arches db

        """
        import json

        details = {}

        with open(source) as f:
            details = json.load(f)

        try:
            uuid.UUID(details["componentid"])
        except:
            details["componentid"] = str(uuid.uuid4())
            print("Registering card component with componentid: {}".format(details["componentid"]))

        instance = models.CardComponent(
            componentid=details["componentid"],
            name=details["name"],
            description=details["description"],
            component=details["component"],
            componentname=details["componentname"],
            defaultconfig=details["defaultconfig"],
        )

        instance.save()

    def update(self, source):
        """
        Updates an existing card component in the arches db

        """
        import json

        details = {}

        with open(source) as f:
            details = json.load(f)

        instance = models.CardComponent.objects.get(name=details["name"])
        instance.description = details["description"]
        instance.component = details["component"]
        instance.componentname = details["componentname"]
        instance.defaultconfig = details["defaultconfig"]
        instance.save()

    def unregister(self, name):
        """
        Removes a function from the system

        """
        try:
            instances = models.CardComponent.objects.filter(name=name)
            if str(instances[0].componentid) != "f05e4d3a-53c1-11e8-b0ea-784f435179ea":
                instances[0].delete()
            else:
                print("You cannot unregister the default card component.")
        except Exception as e:
            print(e)

    def list(self):
        """
        Lists registered card components

        """
        try:
            instances = models.CardComponent.objects.all()
            for instance in instances:
                print(instance.name)
        except Exception as e:
            print(e)
