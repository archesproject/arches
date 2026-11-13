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
    FIX_CARD_SORTORDERS = auto()
    FIX_NODE_SORTORDERS = auto()
    FIX_WIDGET_SORTORDERS = auto()
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
        # Cards with NULL sortorder, or a duplicate sortorder among their siblings
        # (siblings share the same parentnodegroup within the same graph).
        # The null-parent and non-null-parent cases are handled with separate
        # subqueries because SQL cannot equate NULL = NULL.
        _dup_card_nonnull = models.CardModel.objects.filter(
            source_identifier=None,
            sortorder=OuterRef("sortorder"),
            sortorder__isnull=False,
            nodegroup__parentnodegroup_id=OuterRef("nodegroup__parentnodegroup_id"),
            graph_id=OuterRef("graph_id"),
        ).exclude(cardid=OuterRef("cardid"))
        _dup_card_null = models.CardModel.objects.filter(
            source_identifier=None,
            sortorder=OuterRef("sortorder"),
            sortorder__isnull=False,
            nodegroup__parentnodegroup_id__isnull=True,
            graph_id=OuterRef("graph_id"),
        ).exclude(cardid=OuterRef("cardid"))
        self.check_integrity(
            check=IntegrityCheck.NULL_OR_DUPLICATE_CARD_SORTORDER,  # 1018
            queryset=models.CardModel.objects.filter(source_identifier=None).filter(
                Q(sortorder=None)
                | (
                    Q(nodegroup__parentnodegroup_id__isnull=False)
                    & Exists(_dup_card_nonnull)
                )
                | (
                    Q(nodegroup__parentnodegroup_id__isnull=True)
                    & Exists(_dup_card_null)
                )
            ),
            fix_action=FixActions.FIX_CARD_SORTORDERS,
        )
        # Nodes with NULL sortorder (excluding root nodes which have no parent
        # edge), or a duplicate sortorder among their Edge-table siblings.
        self.check_integrity(
            check=IntegrityCheck.NULL_OR_DUPLICATE_NODE_SORTORDER,  # 1019
            queryset=models.Node.objects.filter(source_identifier=None).filter(
                (
                    Q(sortorder=None)
                    & Exists(
                        models.Edge.objects.filter(rangenode_id=OuterRef("nodeid"))
                    )
                )
                | Exists(
                    models.Edge.objects.filter(
                        domainnode_id=Subquery(
                            models.Edge.objects.filter(
                                rangenode_id=OuterRef(OuterRef("nodeid"))
                            ).values("domainnode_id")[:1]
                        ),
                        rangenode__sortorder=OuterRef("sortorder"),
                        rangenode__sortorder__isnull=False,
                    ).exclude(rangenode_id=OuterRef("nodeid"))
                ),
            ),
            fix_action=FixActions.FIX_NODE_SORTORDERS,
        )
        # CXNxW records with NULL sortorder, or a duplicate sortorder within
        # the same card.
        _dup_widget = models.CardXNodeXWidget.objects.filter(
            card_id=OuterRef("card_id"),
            sortorder=OuterRef("sortorder"),
            sortorder__isnull=False,
        ).exclude(pk=OuterRef("pk"))
        self.check_integrity(
            check=IntegrityCheck.NULL_OR_DUPLICATE_WIDGET_SORTORDER,  # 1021
            queryset=models.CardXNodeXWidget.objects.filter(
                card__source_identifier=None
            ).filter(Q(sortorder=None) | Exists(_dup_widget)),
            fix_action=FixActions.FIX_WIDGET_SORTORDERS,
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
                elif fix_action in (
                    FixActions.FIX_CARD_SORTORDERS,
                    FixActions.FIX_NODE_SORTORDERS,
                    FixActions.FIX_WIDGET_SORTORDERS,
                ):
                    fn_map = {
                        FixActions.FIX_CARD_SORTORDERS: (
                            fix_card_sortorders,
                            "Fixed card sortorders",
                        ),
                        FixActions.FIX_NODE_SORTORDERS: (
                            fix_node_sortorders,
                            "Fixed node sortorders",
                        ),
                        FixActions.FIX_WIDGET_SORTORDERS: (
                            fix_widget_sortorders,
                            "Fixed widget sortorders",
                        ),
                    }
                    fix_fn, label = fn_map[fix_action]
                    changes = fix_fn(queryset)
                    fix_status = self.style.SUCCESS("Yes")
                    if changes and self.options["verbosity"] > 0:
                        self.stdout.write()
                        self.stdout.write(f"\t{label}:")
                        for slug, items_changed in sorted(changes.items()):
                            self.stdout.write(
                                f"\t  {slug}: {len(items_changed)} item(s)"
                            )
                            if self.options["verbosity"] > 1:
                                for name, item_id in items_changed:
                                    self.stdout.write(f"\t    {name} ({item_id})")
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


def fix_card_sortorders(problem_cards):
    """Assign 0-based sequential sortorders to source cards within sibling
    groups that have NULL or duplicate sortorders.

    Groups cards by (graph_id, parentnodegroup_id), preserving the relative
    order of cards with unique existing sortorders (NULLs sort last).
    Republishes affected graphs.
    Returns {graph_slug: [(card_name, card_id), ...]} for each updated card.
    """
    from collections import defaultdict

    affected_pairs = set(
        problem_cards.values_list("graph_id", "nodegroup__parentnodegroup_id")
    )
    affected_graph_ids = {pair[0] for pair in affected_pairs}
    all_cards = list(
        models.CardModel.objects.filter(
            source_identifier=None,
            graph_id__in=affected_graph_ids,
        ).select_related("nodegroup")
    )

    groups: dict = defaultdict(list)
    for card in all_cards:
        key = (card.graph_id, card.nodegroup.parentnodegroup_id)
        groups[key].append(card)

    graph_ids_to_republish: set[uuid.UUID] = set()
    changes: dict[uuid.UUID, list[tuple[str, uuid.UUID]]] = {}

    with transaction.atomic():
        for key, group in groups.items():
            if key not in affected_pairs:
                continue
            sorted_group = sorted(
                group,
                key=lambda c: (
                    c.sortorder is None,
                    c.sortorder if c.sortorder is not None else 0,
                ),
            )
            db_updates = []
            for new_so, card in enumerate(sorted_group):
                if card.sortorder != new_so:
                    card.sortorder = new_so
                    db_updates.append(card)
            if db_updates:
                models.CardModel.objects.bulk_update(db_updates, ["sortorder"])
                graph_id = key[0]
                graph_ids_to_republish.add(graph_id)
                for card in db_updates:
                    changes.setdefault(graph_id, []).append(
                        (str(card.name), card.cardid)
                    )

    for graph in models.Graph.objects.filter(
        pk__in=graph_ids_to_republish,
        source_identifier=None,
    ):
        graph.publish(notes="Fixed card sortorders")

    slug_map = dict(
        models.GraphModel.objects.filter(pk__in=changes).values_list("pk", "slug")
    )
    return {slug_map.get(gid, str(gid)): items for gid, items in changes.items()}


def fix_node_sortorders(problem_nodes):
    """Assign 0-based sequential sortorders to nodes within parent-node
    sibling groups that have NULL or duplicate sortorders.

    Sibling groups are determined via the Edge table (nodes sharing the same
    domainnode are siblings). Preserves relative order of nodes with unique
    existing sortorders (NULLs sort last). Republishes affected graphs.
    Returns {graph_slug: [(node_name, node_id), ...]} for each updated node.
    """
    from collections import defaultdict

    affected_graph_ids = set(problem_nodes.values_list("graph_id", flat=True))
    problem_node_ids = set(problem_nodes.values_list("nodeid", flat=True))

    all_nodes = {
        n.nodeid: n for n in models.Node.objects.filter(graph_id__in=affected_graph_ids)
    }
    edges = models.Edge.objects.filter(graph_id__in=affected_graph_ids).values_list(
        "rangenode_id", "domainnode_id"
    )

    sibling_groups: dict = defaultdict(list)
    for child_id, parent_id in edges:
        child = all_nodes.get(child_id)
        if child is not None:
            sibling_groups[parent_id].append(child)

    graph_ids_to_republish: set[uuid.UUID] = set()
    changes: dict[uuid.UUID, list[tuple[str, uuid.UUID]]] = {}

    with transaction.atomic():
        for group in sibling_groups.values():
            if not any(n.nodeid in problem_node_ids for n in group):
                continue
            sorted_group = sorted(
                group,
                key=lambda n: (
                    n.sortorder is None,
                    n.sortorder if n.sortorder is not None else 0,
                ),
            )
            db_updates = []
            for new_so, node in enumerate(sorted_group):
                if node.sortorder != new_so:
                    node.sortorder = new_so
                    db_updates.append(node)
            if db_updates:
                models.Node.objects.bulk_update(db_updates, ["sortorder"])
                for node in db_updates:
                    graph_ids_to_republish.add(node.graph_id)
                    changes.setdefault(node.graph_id, []).append(
                        (str(node.name), node.nodeid)
                    )

    for graph in models.Graph.objects.filter(
        pk__in=graph_ids_to_republish,
        source_identifier=None,
    ):
        graph.publish(notes="Fixed node sortorders")

    slug_map = dict(
        models.GraphModel.objects.filter(pk__in=changes).values_list("pk", "slug")
    )
    return {slug_map.get(gid, str(gid)): items for gid, items in changes.items()}


def fix_widget_sortorders(problem_widgets):
    """Assign 0-based sequential sortorders to CXNxW records within cards
    that have NULL or duplicate widget sortorders.

    Groups widgets by card and re-sequences sortorders, preserving relative
    order of widgets with unique existing sortorders (NULLs sort last).
    Republishes affected graphs.
    Returns {graph_slug: [(node_name, widget_id), ...]} for each updated widget.
    """
    from collections import defaultdict

    affected_card_ids = set(problem_widgets.values_list("card_id", flat=True))
    all_widgets = list(
        models.CardXNodeXWidget.objects.filter(
            card_id__in=affected_card_ids,
            card__source_identifier=None,
        ).select_related("node", "card")
    )

    card_groups: dict = defaultdict(list)
    for widget in all_widgets:
        card_groups[widget.card_id].append(widget)

    graph_ids_to_republish: set[uuid.UUID] = set()
    changes: dict[uuid.UUID, list[tuple[str, uuid.UUID]]] = {}

    with transaction.atomic():
        for card_widgets in card_groups.values():
            sorted_widgets = sorted(
                card_widgets,
                key=lambda w: (
                    w.sortorder is None,
                    w.sortorder if w.sortorder is not None else 0,
                ),
            )
            db_updates = []
            for new_so, widget in enumerate(sorted_widgets):
                if widget.sortorder != new_so:
                    widget.sortorder = new_so
                    db_updates.append(widget)
            if db_updates:
                models.CardXNodeXWidget.objects.bulk_update(db_updates, ["sortorder"])
                for widget in db_updates:
                    graph_id = widget.node.graph_id
                    graph_ids_to_republish.add(graph_id)
                    changes.setdefault(graph_id, []).append(
                        (str(widget.node.name), widget.pk)
                    )

    for graph in models.Graph.objects.filter(
        pk__in=graph_ids_to_republish,
        source_identifier=None,
    ):
        graph.publish(notes="Fixed widget sortorders")

    slug_map = dict(
        models.GraphModel.objects.filter(pk__in=changes).values_list("pk", "slug")
    )
    return {slug_map.get(gid, str(gid)): items for gid, items in changes.items()}


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
