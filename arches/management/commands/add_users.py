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

import argparse
import csv
import traceback
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.utils.crypto import get_random_string
from arches.app.utils.permission_backend import assign_perm
from arches.app.models import models


class Command(BaseCommand):
    """
    Commands for adding arches test users

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--operation",
            action="store",
            dest="operation",
            choices=[
                "test_users",
                "csv_users",
            ],
            default="test_users",
            help="Operation Type; "
            + "'test_users'=Creates test users"
            + "'csv_users'=Loads users from CSV file",
        )

        parser.add_argument(
            "-s",
            "--source",
            action="store",
            dest="csv_file",
            help="CSV file to be loaded",
        )

        parser.add_argument(
            "-c",
            "--count",
            action="store",
            dest="user_count",
            default=3,
            type=int,
            help="The number of test users to add.  Not used for csv loading",
        )

        parser.add_argument(
            "-p",
            "--power-user",
            action=argparse.BooleanOptionalAction,
            help="Whether or not to create a power user",
        )

    def handle(self, *args, **options):
        if options.get("operation") == "test_users":
            number_of_existing_users = User.objects.filter(
                username__startswith="tester"
            ).count()
            user_count = options.get("user_count")
            if number_of_existing_users > 0:
                print(
                    "{number_of_existing_users} test users already exist.  Do you wish to add {user_count} new test users to Arches? (y or n):".format(
                        number_of_existing_users=number_of_existing_users,
                        user_count=user_count,
                    )
                )
                confirm_new_test_users = input()

                if confirm_new_test_users.lower() == "y":
                    self.add_test_users(options)
            else:
                self.add_test_users(options)

        elif options.get("operation") == "csv_users":
            self.load_users_from_csv(options)

    def add_test_users(self, options):
        user_count = options.get("user_count")
        profiles = []
        number_of_existing_users = User.objects.filter(
            username__startswith="tester"
        ).count()
        for current in range(1, user_count + 1):
            suffix = current + number_of_existing_users
            profiles.append(
                {
                    "name": f"tester{suffix}",
                    "email": f"tester{suffix}@test.com",
                    "password": "Test12345!",
                    "groups": ["Graph Editor", "Resource Editor"],
                }
            )

        if options.get("power_user"):
            profiles = list(
                profiles
                + [
                    {
                        "name": "dev",
                        "email": "dev@test.com",
                        "password": "dev",
                        "groups": [
                            "Graph Editor",
                            "Resource Editor",
                            "Resource Exporter",
                            "Resource Reviewer",
                            "Application Administrator",
                            "Crowdsource Editor",
                            "Guest",
                            "RDM Administrator",
                            "Resource Reviewer",
                            "System Administrator",
                            "Developer",
                        ],
                    }
                ]
            )

            try:
                dev_group = Group.objects.create(name="Developer")
                dev_perms = Permission.objects.all().values("id")
                perm_ids = [int(perm["id"]) for perm in dev_perms]
                for permission in perm_ids:
                    dev_group.permissions.add(permission)
            except:
                self.stderr.write(traceback.format_exc())

        plugins = models.Plugin.objects.all()
        etl_modules = models.ETLModule.objects.all()
        groups_dict = Group.objects.in_bulk(field_name="name")
        for profile in profiles:
            try:
                user = User.objects.create_user(
                    username=profile["name"],
                    email=profile["email"],
                    password=profile["password"],
                )
                if user.username == "dev":
                    user.is_staff = True
                    user.first_name = "Dev"
                    user.last_name = "User"
                    for plugin in plugins:
                        assign_perm("change_plugin", user, plugin)
                        assign_perm("add_plugin", user, plugin)
                        assign_perm("delete_plugin", user, plugin)
                        assign_perm("view_plugin", user, plugin)
                    for etl_module in etl_modules:
                        assign_perm("view_etlmodule", user, etl_module)
                user.save()
                self.stdout.write(
                    f"Added test user: {user.username}, password: {profile['password']}"
                )

                for group_name in profile["groups"]:
                    group = groups_dict[group_name]
                    group.user_set.add(user)

            except:
                self.stderr.write(traceback.format_exc())

    def load_users_from_csv(self, options):
        csv_file = options.get("csv_file")
        if not csv_file:
            self.stdout.write("No CSV file provided.")
            return
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        try:
            with open(csv_file, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    user = User.objects.create_user(
                        username=row.get("username")
                        or row.get("user", None)
                        or row.get("email"),
                        email=row.get("email"),
                        password=row.get("password", get_random_string(50, chars)),
                    )
                    for group_name in row.get("groups", "").split(";"):
                        group = Group.objects.filter(name=group_name).first()
                        if group:
                            group.user_set.add(user)
                    user.save()
        except Exception as e:
            self.stderr.write(traceback.format_exc())
