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

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from arches.app.models import models
import arches.app.utils.permission_backend as permission_backend


class Command(BaseCommand):
    """
    Command for granting or revoking object permissions
    Example: python manage.py permissions --permission view --action grant --group 'Resource Reviewer' --type etlmodule

    """

    def add_arguments(self, parser):
        parser.add_argument("operation", nargs="?")

        parser.add_argument(
            "-p",
            "--permission",
            action="store",
            dest="permission",
            choices=["view", "add", "change", "delete"],
            help="Permission to be added",
        )

        parser.add_argument(
            "-a",
            "--action",
            action="store",
            dest="action",
            choices=["grant", "revoke"],
            help="Indicate if you want to grant a permission or revoke it",
        )

        parser.add_argument(
            "-g",
            "--group",
            action="store",
            dest="group",
            help="Indicate to which group permissions will be applied",
        )

        parser.add_argument(
            "-t",
            "--type",
            action="store",
            dest="type",
            choices=["plugin", "etlmodule"],
            help="Type of object to which permissions will be applied",
        )

    def handle(self, *args, **options):

        self.edit_permissions(
            permission=options["permission"],
            action=options["action"],
            group=options["group"],
            type=options["type"],
        )

    def edit_permissions(self, permission, action, group, type):
        if type == "plugin":
            objects = models.Plugin.objects.all()
        elif type == "etlmodule":
            objects = models.ETLModule.objects.all()

        if action == "grant":
            permission_action = getattr(permission_backend, "assign_perm")
        elif action == "revoke":
            permission_action = getattr(permission_backend, "remove_perm")

        try:
            permission_group = Group.objects.get(name=group)
        except Group.DoesNotExist:
            self.stderr.write(f"{group} group does not exist")

        permission_type = f"{permission}_{type}"

        for object in objects:
            permission_action(permission_type, permission_group, object)
