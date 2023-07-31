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

from arches.app.models import models
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Exists, OuterRef


class Command(BaseCommand):
    """
    Rectifies issue described at:
    https://github.com/archesproject/arches/issues/9847
    """
    help = "Identify and remove nodeless node groups/cards that were created in Arches 7.3."

    def add_arguments(self, parser):
        parser.add_argument("-d", "--dry", action="store_true", dest="dry_run", default=False,
                            help="Identify and print nodeless node groups; does not delete them.")

    def handle(self, *args, **options):
        nodeless = models.NodeGroup.objects.filter(
            ~Exists(models.Node.objects.filter(nodegroup_id=OuterRef("nodegroupid")))
        )

        num = len(nodeless)
        print(num, "nodeless nodegroups.")

        if options["dry_run"]:
            print("No action taken.")
            return

        print("Deleting ...")

        with transaction.atomic():
            nodeless.delete()

        print(num, "nodeless nodegroups deleted (with any associated cards).")
