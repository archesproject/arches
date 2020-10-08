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
from django.contrib.auth.models import User
from django.contrib.auth.models import Group


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
        )

        for profile in profiles:
            try:
                user = User.objects.create_user(username=profile["name"], email=profile["email"], password=profile["password"])
                user.save()
                print(f"Added test user: {user.username}, password: {profile['password']}")

                for group_name in profile["groups"]:
                    group = Group.objects.get(name=group_name)
                    group.user_set.add(user)

            except Exception as e:
                print(e)
