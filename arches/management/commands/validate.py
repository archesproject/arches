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

from datetime import datetime

from arches import __version__
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
            self.stdout.write()
            self.stdout.write("Arches integrity report")
            self.stdout.write(f"Prepared by Arches {__version__} on {datetime.today()}")
            self.stdout.write()
            self.stdout.write("\t".join(["", "Error", "Rows", "Description"]))
            self.stdout.write()
        
        # add checks here in numerical order
        self.check_integrity(
            errno=IntegrityCheck.NODE_HAS_ONTOLOGY_GRAPH_DOES_NOT.value,  # 1005
            name="Nodes with ontologies found in graphs without ontologies",
            queryset=models.Node.objects.only("ontologyclass", "graph").filter(
                ontologyclass__isnull=False).filter(graph__ontology=None),
            fix_action=None,
        )
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
        result = self.style.ERROR("FAIL") if count else self.style.SUCCESS("PASS")

        if self.options["verbosity"] > 0:
            self.stdout.write("\t".join([result, str(errno), str(count), name]))
            if self.options["verbosity"] > 1:
                self.stdout.write("\t" + "-" * 36)
                if queryset:
                    for i, n in enumerate(queryset):
                        if i < self.options["limit"]:
                            self.stdout.write(f"\t{n.pk}")
                        else:
                            self.stdout.write("\t\t(truncated...)")
                            break

        if not count:
            return

        if self.options["fix_all"] or errno in self.options["fix"]:
            if fix_action:
                self.stdout.write("\tFixing ...")
            if fix_action == DELETE_QUERYSET:
                with transaction.atomic():
                    queryset.delete()
                self.stdout.write(f"\tDELETED.")
