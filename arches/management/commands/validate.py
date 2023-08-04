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

from arches.app.const import IntegrityCheck
from arches.app.models import models
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Exists, OuterRef

DELETE_QUERYSET = "delete queryset"


class Command(BaseCommand):
    """
    Validate an Arches database against a set of data integrity checks.
    Takes no action by default (other than printing a summary).

    Provide --verbosity=2 to get a richer output (list of affected nodes).
    """
    help = "Validate an Arches database against a set of data integrity checks."

    def add_arguments(self, parser):
        parser.add_argument("--fix-all", action="store_true", dest="fix_all", default=False,
                            help="Apply all fix actions.")
        parser.add_argument("--fix", action="extend", nargs="+", type=int, default=[])
        parser.add_argument("--limit", action="store", type=int, default=500)

    def handle(self, *args, **options):
        self.options = options
        if self.options["verbosity"] > 0:
            print("Error\tDescription")
            print()
        
        # add checks here in numerical order
        self.check_integrity(
            errno=IntegrityCheck.NODELESS_NODE_GROUP.value,  # 1012
            name="Nodeless node groups",
            queryset=models.NodeGroup.objects.filter(
                ~Exists(models.Node.objects.filter(nodegroup_id=OuterRef("nodegroupid")))
            ),
            fix_action=DELETE_QUERYSET,
        )

    def check_integrity(self, *, errno, name, queryset, fix_action):
        count = len(queryset)

        if self.options["verbosity"] > 0:
            print(f"{errno}\t{name}:\t{count}")
            if self.options["verbosity"] > 1:
                print("\t" + "-" * 36)
                if queryset:
                    for i, n in enumerate(queryset):
                        if i < self.options["limit"]:
                            print(f"\t{n.pk}")
                        else:
                            print("\t\t(truncated...)")
                            break
                else:
                    print("\tPASS")

        if self.options["fix_all"] or errno in self.options["fix"]:
            print("\tFixing ...")
            if fix_action == DELETE_QUERYSET:
                with transaction.atomic():
                    queryset.delete()
                print(f"\tDELETED.")
        elif self.options["verbosity"] > 0:
            print()  # trailing empty line
