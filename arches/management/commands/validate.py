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

import uuid
from datetime import datetime
from enum import StrEnum, auto

from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.management import BaseCommand, CommandError, call_command
from django.db import transaction
from django.db.models import Count, Exists, Max, OuterRef, Q, Subquery

from arches import __version__
from arches.app.const import IntegrityCheck
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models


class CommandModes(StrEnum):
    FIX = auto()
    VALIDATE = auto()


class FixActions(StrEnum):
    """
    Note for implementers: the fix action should not leave side effects
    on the input queryset, as currently factored. (Instead, do things
    like delete(), or values(), or prefetch_related() that generate clones.)
    """

    BACKFILL_MISSING_WIDGETS = auto()
    DELETE_QUERYSET = auto()
    DEDUPLICATE_WIDGETS = auto()
    UPDATE_GRAPH_PUBLICATIONS = auto()


class ValidationResultList(list):
    def exists(self):
        return bool(self)


class InvalidNodeDefaultValue:
    def __init__(self, node, errors):
        self.node = node
        self.errors = errors

    def __str__(self):
        return f"{self.node} ({self.node.pk}): {self.errors}"


class Command(BaseCommand):
    """
    Validate an Arches database against a set of data integrity checks.
    Takes no action by default (other than printing a summary).

    Provide --verbosity=2 to get a richer output (list of affected rows).

    Example: python manage.py validate --fix-all
    """

    help = "Validate an Arches database against a set of data integrity checks, and opt-in to remediation."

    def add_arguments(self, parser):
        choices = [check.value for check in IntegrityCheck]

        parser.add_argument(
            "--fix-all",
            action="store_true",
            dest="fix_all",
            default=False,
            help="Apply all fix actions.",
        )
        parser.add_argument(
            "--fix",
            action="extend",
            nargs="+",
            type=int,
            default=[],
            choices=choices,
            help="List the error codes to fix, e.g. --fix 1012 1013 ...",
        )
        parser.add_argument(
            "--codes",
            action="extend",
            nargs="+",
            type=int,
            default=[],
            choices=choices,
            help="List the error codes to validate, e.g. --codes 1012 1013 ...",
        )
        parser.add_argument(
            "--limit",
            action="store",
            type=int,
            help="Maximum number of rows to print; does not affect fix actions",
        )
        parser.add_argument(
            "--export",
            action="store_true",
            dest="export",
            default=False,
            help=(
                "After fixing, export modified graphs as JSON. "
                "Only applies when used with --fix or --fix-all."
            ),
        )
        parser.add_argument(
            "--export-dir",
            default=".",
            dest="export_dir",
            metavar="DIR",
            help=(
                "Directory to export modified graphs to as JSON. "
                "Defaults to the current working directory. "
                "Only applies when used with --export and --fix or --fix-all."
            ),
        )

    def handle(self, *args, **options):
        self.options = options
        limit = self.options["limit"]
        if limit is not None and limit < 1:
            raise CommandError("Limit must be a positive integer.")
        if limit and self.options["verbosity"] < 2:
            # Limit is meaningless w/o the higher verbosity output
            self.options["verbosity"] = 2

        if self.options["fix_all"] or self.options["fix"]:
            self.mode = CommandModes.FIX
            fix_heading = "Fixed?\t"  # Lengthen to match wider "Fixable?" heading
        else:
            self.mode = CommandModes.VALIDATE
            fix_heading = "Fixable?"

        if self.options["verbosity"] > 0:
            self.stdout.write()
            self.stdout.write("Arches integrity report")
            self.stdout.write(
                f"Prepared by Arches {__version__} on {datetime.today().strftime('%c')}"
            )
            self.stdout.write()
            self.stdout.write("Run with --verbosity=2 for more details or --help")
            self.stdout.write()
            self.stdout.write(
                "\t".join(["", "Error", "Rows", fix_heading, "Description"])
            )
            self.stdout.write()

        # Add checks here in numerical order
        self.check_integrity(
            check=IntegrityCheck.NODE_HAS_ONTOLOGY_GRAPH_DOES_NOT,  # 1005
            queryset=models.Node.objects.only("ontologyclass", "graph")
            .filter(ontologyclass__isnull=False)
            .filter(graph__ontology=None),
            fix_action=None,
        )
        self.check_integrity(
            check=IntegrityCheck.NODELESS_NODE_GROUP,  # 1012
            queryset=models.NodeGroup.objects.filter(
                ~Exists(
                    models.Node.objects.filter(nodegroup_id=OuterRef("nodegroupid"))
                )
            ),
            fix_action=FixActions.DELETE_QUERYSET,
        )
        self.check_integrity(
            check=IntegrityCheck.NODEGROUP_WITHOUT_GROUPING_NODE,  # 1013
            queryset=models.NodeGroup.objects.filter(node__gt=0, grouping_node=None),
            fix_action=None,
        )
        self.check_integrity(
            check=IntegrityCheck.PUBLICATION_MISSING_FOR_LANGUAGE,  # 1014
            queryset=(
                models.GraphModel.objects.filter(
                    isresource=True,
                    publication__isnull=False,
                    source_identifier=None,
                )
                .annotate(
                    publications_in_system_languages=ArrayAgg(
                        Subquery(
                            models.PublishedGraph.objects.filter(
                                pk=OuterRef("publication__publishedgraph"),
                            )
                            .values("language")
                            .distinct()
                        ),
                        filter=Q(
                            publication__publishedgraph__language__in=[
                                lang[0] for lang in settings.LANGUAGES
                            ]
                        ),
                    )
                )
                .filter(
                    publications_in_system_languages__len__lt=len(settings.LANGUAGES)
                )
            ),
            fix_action=FixActions.UPDATE_GRAPH_PUBLICATIONS,
        )
        self.check_integrity(
            # Enforced in database as of v8, but here to help during upgrade.
            check=IntegrityCheck.TOO_MANY_WIDGETS,  # 1016
            queryset=models.Node.objects.annotate(
                source_widget_count=Count(
                    "cardxnodexwidget", filter=Q(source_identifier__isnull=True)
                ),
                draft_widget_count=Count(
                    "cardxnodexwidget", filter=Q(source_identifier__isnull=False)
                ),
            ).filter(Q(source_widget_count__gt=1) | Q(draft_widget_count__gt=1)),
            fix_action=FixActions.DEDUPLICATE_WIDGETS,
        )
        self.check_integrity(
            check=IntegrityCheck.INVALID_DEFAULT_VALUE,  # 1020
            queryset=self.get_invalid_default_values(),
            fix_action=None,
        )
        self.check_integrity(
            check=IntegrityCheck.NO_WIDGETS,  # 1017
            queryset=models.Node.objects.filter(source_identifier=None)
            .filter(
                datatype__in=models.DDataType.objects.filter(
                    defaultwidget__isnull=False
                ).values("datatype")
            )
            .annotate(widget_count=Count("cardxnodexwidget"))
            .filter(widget_count__lt=1),
            fix_action=FixActions.BACKFILL_MISSING_WIDGETS,
        )

    def get_invalid_default_values(self):
        invalid_defaults = ValidationResultList()
        datatype_factory = DataTypeFactory()
        nodes = (
            models.Node.objects.filter(config__has_key="defaultValue")
            .select_related("graph")
            .only("nodeid", "datatype", "config", "graph")
        )

        for node in nodes.iterator(chunk_size=500):
            default_value = node.config.get("defaultValue")
            datatype = datatype_factory.get_instance(node.datatype)
            errors = datatype.validate(default_value, node=node)
            if errors:
                invalid_defaults.append(InvalidNodeDefaultValue(node, errors))

        return invalid_defaults

    def _export_graphs(self, graph_slugs):
        if self.options.get("export"):
            export_dir = self.options["export_dir"]
            self.stdout.write(f"\tExporting modified graphs to {export_dir!r}:")
            call_command(
                "packages",
                operation="export_graphs",
                dest_dir=export_dir,
                graphs=",".join(
                    str(pk)
                    for slug in graph_slugs
                    for pk in models.GraphModel.objects.filter(
                        slug=slug, source_identifier=None
                    ).values_list("pk", flat=True)
                ),
                verbosity=self.options["verbosity"],
                stdout=self.stdout,
                stderr=self.stderr,
            )
        else:
            self.stdout.write(
                "\tThese graphs were modified in the database only."
                " Re-export each to persist the changes:"
            )
            for slug in sorted(graph_slugs):
                self.stdout.write(f"\t  {slug}")

    def check_integrity(self, check, queryset, fix_action):
        # 500 not set as a default earlier:
        # None distinguishes whether verbose output implied.
        limit = self.options["limit"] or 500

        if self.mode == CommandModes.VALIDATE:
            if self.options["codes"] and check.value not in self.options["codes"]:
                # User didn't request this specific check.
                return
            # Fixable?
            fix_status = (
                self.style.MIGRATE_HEADING("Yes")
                if fix_action
                else self.style.NOTICE("No")
            )
            if not queryset.exists():
                fix_status = self.style.MIGRATE_HEADING("N/A")
        else:
            if not self.options["fix_all"] and check.value not in self.options["fix"]:
                # User didn't request this specific check.
                return

            # Fixed?
            if fix_action is None:
                if self.options["fix_all"]:
                    fix_status = self.style.MIGRATE_HEADING("N/A")
                else:
                    raise CommandError(
                        f"Requested fixing unfixable - {check.value}: {check}"
                    )
            elif queryset.exists():
                fix_status = self.style.ERROR("No")  # until actually fixed below
                # Perform fix action
                if fix_action == FixActions.DELETE_QUERYSET:
                    graph_slugs = set(
                        models.GraphModel.objects.filter(
                            cardmodel__nodegroup__in=queryset,
                            source_identifier=None,
                        ).values_list("slug", flat=True)
                    )
                    with transaction.atomic():
                        queryset.delete()
                    fix_status = self.style.SUCCESS("Yes")
                    if graph_slugs:
                        self._export_graphs(graph_slugs)
                elif fix_action == FixActions.UPDATE_GRAPH_PUBLICATIONS:
                    graph_slugs = set(queryset.values_list("slug", flat=True))
                    call_command(
                        "graph",
                        "publish",
                        "--update",
                        "-g",
                        ",".join(
                            str(pk) for pk in queryset.values_list("pk", flat=True)
                        ),
                        verbosity=self.options["verbosity"],
                        stdout=self.stdout,
                        stderr=self.stderr,
                    )
                    fix_status = self.style.SUCCESS("Yes")
                    if graph_slugs:
                        self._export_graphs(graph_slugs)
                elif fix_action == FixActions.DEDUPLICATE_WIDGETS:
                    graph_slugs = set(queryset.values_list("graph__slug", flat=True))
                    problems_remain = deduplicate_widgets(
                        queryset.prefetch_related("nodegroup__cardmodel_set")
                    )
                    fix_status = (
                        self.style.MIGRATE_HEADING("Partial")
                        if problems_remain
                        else self.style.SUCCESS("Yes")
                    )
                    if graph_slugs:
                        self._export_graphs(graph_slugs)
                elif fix_action == FixActions.BACKFILL_MISSING_WIDGETS:
                    changes = backfill_missing_widgets(queryset)
                    fix_status = self.style.SUCCESS("Yes")
                    if changes and self.options["verbosity"] > 0:
                        self.stdout.write()
                        self.stdout.write("\tBackfilled CXNxW records:")
                        for slug, nodes_changed in sorted(changes.items()):
                            self.stdout.write(
                                f"\t  {slug}: {len(nodes_changed)} node(s)"
                            )
                            if self.options["verbosity"] > 1:
                                for alias, nodeid in nodes_changed:
                                    self.stdout.write(f"\t    {alias} ({nodeid})")
                        self.stdout.write()
                    if changes:
                        self._export_graphs(changes)
                else:
                    raise NotImplementedError
            else:
                # Nothing to do.
                if self.options["fix_all"]:
                    fix_status = self.style.MIGRATE_HEADING("N/A")
                else:
                    raise CommandError(f"Nothing to fix - {check.value}: {check}")

        # Print the report (after any requested fixes are made)
        if self.options["verbosity"] > 0:
            # len() works if the FixAction didn't inadvertently evaluate the qs.
            count = len(queryset)
            result = self.style.ERROR("FAIL") if count else self.style.SUCCESS("PASS")
            # Fix status takes two "columns" so add a tab
            self.stdout.write(
                "\t".join(
                    str(x)
                    for x in (result, check.value, count, fix_status + "\t", check)
                )
            )

            if self.options["verbosity"] > 1:
                self.stdout.write("\t" + "-" * 36)
                if count and check.value == IntegrityCheck.TOO_MANY_WIDGETS.value:
                    self.stdout.write(
                        "\tNode alias,nodeid,draft_or_published,graph,nodegroup,cardxnodexwidgets"
                    )
                if queryset:
                    for i, n in enumerate(queryset):
                        if i < limit:
                            if check.value == IntegrityCheck.TOO_MANY_WIDGETS.value:
                                card_set = n.cardxnodexwidget_set.all()
                                cards = " & ".join(
                                    f"{card} ({card.pk})" for card in card_set
                                )
                                self.stdout.write(f"\t{n},{n.nodegroup.pk},{cards}")
                            else:
                                self.stdout.write(f"\t{n}")
                        else:
                            self.stdout.write("\t\t(truncated...)")
                            break

            self.stdout.write()


def backfill_missing_widgets(nodes):
    widget_by_datatype = {
        dt.datatype: dt.defaultwidget
        for dt in models.DDataType.objects.filter(
            defaultwidget__isnull=False
        ).select_related("defaultwidget")
    }
    graph_ids_to_republish: set[uuid.UUID] = set()
    # graph_id → [(alias, nodeid)] for every record created
    changes: dict[uuid.UUID, list[tuple[str, uuid.UUID]]] = {}
    with transaction.atomic():
        card_by_nodegroup = {
            card.nodegroup_id: card
            for card in models.CardModel.objects.filter(
                nodegroup_id__in=nodes.values("nodegroup_id"),
                source_identifier=None,
            )
        }
        next_sortorder_by_card = {
            card_id: (0 if max_so is None else max_so + 1)
            for card_id, max_so in models.CardXNodeXWidget.objects.filter(
                card__in=card_by_nodegroup.values()
            )
            .values("card_id")
            .annotate(max_so=Max("sortorder"))
            .values_list("card_id", "max_so")
        }
        for node in nodes:
            card = card_by_nodegroup.get(node.nodegroup_id)
            if not card:
                continue
            defaultwidget = widget_by_datatype.get(node.datatype)
            if not defaultwidget:
                continue
            next_sortorder = next_sortorder_by_card.get(card.pk, 0)
            next_sortorder_by_card[card.pk] = next_sortorder + 1
            _, created = models.CardXNodeXWidget.objects.update_or_create(
                node=node,
                card=card,
                defaults={
                    "widget_id": defaultwidget.pk,
                    "config": defaultwidget.defaultconfig or {},
                    "label": node.name,
                    "sortorder": next_sortorder,
                },
            )
            if created:
                graph_ids_to_republish.add(node.graph_id)
                changes.setdefault(node.graph_id, []).append((node.alias, node.pk))

        for graph in models.Graph.objects.filter(
            pk__in=graph_ids_to_republish,
            source_identifier=None,
        ):
            graph.publish(notes="Backfilled missing card_x_node_x_widgets")

    slug_map = dict(
        models.GraphModel.objects.filter(pk__in=changes).values_list("pk", "slug")
    )
    return {
        slug_map.get(graph_id, str(graph_id)): nodes_changed
        for graph_id, nodes_changed in changes.items()
    }


def deduplicate_widgets(nodes):
    class BreakNestedLoops(Exception):
        pass

    problems_remain = False
    graph_ids_to_republish: set[uuid.UUID] = set()
    with transaction.atomic():
        for node in nodes:
            try:
                card = node.nodegroup.cardmodel_set.first()
                good_cross = node.cardxnodexwidget_set.filter(card=card).first()
                if not good_cross:
                    node.cardxnodexwidget_set.all().delete()
                    continue
                for test_cross in node.cardxnodexwidget_set.all():
                    if test_cross.pk == good_cross.pk:
                        continue

                    if test_cross.card.pk != good_cross.card.pk:
                        graph_ids_to_republish.add(test_cross.node.graph_id)
                        test_cross.delete()
                        continue

                    for field, value in vars(test_cross).items():
                        if field in ("_state", "id", "card_id", "sortorder"):
                            continue
                        # If the values differ, we can't deduplicate.
                        # Use str() because I18n_JSON doesn't implement __eq__().
                        if str(getattr(test_cross, field)) != str(value):
                            problems_remain = True
                            raise BreakNestedLoops
                    # If we get here, the only difference is sortorder.
                    graph_ids_to_republish.add(test_cross.node.graph_id)
                    test_cross.delete()
            except BreakNestedLoops:
                continue

        for graph in models.Graph.objects.filter(
            pk__in=graph_ids_to_republish,
            source_identifier=None,
        ):
            graph.publish(notes="Deduplicated card_x_node_x_widgets")

    return problems_remain
