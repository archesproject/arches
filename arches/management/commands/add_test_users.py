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
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from guardian.shortcuts import assign_perm
from arches.app.models import models

class Command(BaseCommand):
    """
    Commands for adding arches test users

    """

    def add_arguments(self, parser):
        parser.add_argument("operation", nargs="?")

    def handle(self, *args, **options):
        self.add_users()

    def add_users(self):
        profiles = (
            {"name": "tester1", "email": "tester1@test.com", "password": "Test12345!", "groups": ["Graph Editor", "Resource Editor"]},
            {"name": "tester2", "email": "tester2@test.com", "password": "Test12345!", "groups": ["Graph Editor", "Resource Editor"]},
            {"name": "tester3", "email": "tester3@test.com", "password": "Test12345!", "groups": ["Graph Editor", "Resource Editor"]},
            {
                "name": "dev",
                "email": "dev@test.com",
                "password": "dev",
                "groups": [
                    "Graph Editor",
                    "Resource Editor",
                    "Resource Reviewer",
                    "Application Administrator",
                    "Crowdsource Editor",
                    "Guest",
                    "RDM Administrator",
                    "Resource Reviewer",
                    "System Administrator",
                    "Developer",
                ],
            },
        )

        dev_perm_codenames = ["add_cardmodel",
                "change_cardmodel",
                "delete_cardmodel",
                "view_cardmodel",
                "add_cardcomponent",
                "change_cardcomponent",
                "delete_cardcomponent",
                "view_cardcomponent",
                "add_cardxnodexwidget",
                "change_cardxnodexwidget",
                "delete_cardxnodexwidget",
                "view_cardxnodexwidget",
                "add_concept",
                "change_concept",
                "delete_concept",
                "view_concept",
                "add_ddatatype",
                "change_ddatatype",
                "delete_ddatatype",
                "view_ddatatype",
                "add_function",
                "change_function",
                "delete_function",
                "view_function",
                "add_functionxgraph",
                "change_functionxgraph",
                "delete_functionxgraph",
                "view_functionxgraph",
                "add_reporttemplate",
                "change_reporttemplate",
                "delete_reporttemplate",
                "view_reporttemplate",
                "no_access_to_resourceinstance",
                "add_searchcomponent",
                "change_searchcomponent",
                "delete_searchcomponent",
                "view_searchcomponent",
                "add_widget",
                "change_widget",
                "delete_widget",
                "view_widget",
                "add_plugin",
                "change_plugin",
                "delete_plugin",
                "view_plugin",
                "add_iiifmanifest",
                "change_iiifmanifest",
                "delete_iiifmanifest",
                "view_iiifmanifest",
                "add_vwannotation",
                "change_vwannotation",
                "delete_vwannotation",
                "view_vwannotation",
                "add_etlmodule",
                "change_etlmodule",
                "delete_etlmodule",
                "view_etlmodule",
                "add_spatialview",
                "change_spatialview",
                "delete_spatialview",
                "view_spatialview",
                "add_card",
                "change_card",
                "delete_card",
                "view_card",
                "view_resourceinstance",
                "change_resourceinstance",
                "delete_resourceinstance",
                "add_resourceinstance",
                "add_permission",
                "change_permission",
                "delete_permission",
                "view_permission",
                "add_group",
                "change_group",
                "delete_group",
                "view_group",
                "add_user",
                "change_user",
                "delete_user",
                "view_user",
                "add_groupobjectpermission",
                "change_groupobjectpermission",
                "delete_groupobjectpermission",
                "view_groupobjectpermission",
                "add_userobjectpermission",
                "change_userobjectpermission",
                "delete_userobjectpermission",
                "view_userobjectpermission",
                "add_archestemplate",
                "change_archestemplate",
                "delete_archestemplate",
                "view_archestemplate",
            ]       

        try:
            dev_group = Group.objects.create(name='Developer')
            dev_perms = Permission.objects.filter(codename__in=dev_perm_codenames).values("id")
            perm_ids = [int(perm['id']) for perm in dev_perms]
            for permission in perm_ids:
                dev_group.permissions.add(permission)
        except Exception as e:
            print(e)
        
        for profile in profiles:
            try:
                user = User.objects.create_user(username=profile["name"], email=profile["email"], password=profile["password"])
                if user.username == "dev":
                    user.is_staff = True
                    user.first_name = "Dev"
                    user.last_name = "User"
                    plugins = models.Plugin.objects.all()
                    for plugin in plugins:
                        assign_perm("change_plugin", user, plugin)
                        assign_perm("add_plugin", user, plugin)
                        assign_perm("delete_plugin", user, plugin)
                        assign_perm("view_plugin", user, plugin)
                user.save()
                print(f"Added test user: {user.username}, password: {profile['password']}")

                for group_name in profile["groups"]:
                    group = Group.objects.get(name=group_name)
                    group.user_set.add(user)

            except Exception as e:
                print(e)
