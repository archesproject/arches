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
from arches.app.utils import transaction


class Command(BaseCommand):
    """
    Commands for managing Arches functions

    """

    def add_arguments(self, parser):
        parser.add_argument("operation", nargs="?")
        parser.add_argument("transaction_id", nargs="?")

    def handle(self, *args, **options):
        if options["operation"] == "reverse":
            self.reverse(options["transaction_id"])

    def reverse(self, transaction_id):
        print(transaction.reverse_edit_log_entries(transaction_id))
