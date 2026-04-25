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

import datetime
import re
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from arches.app.models.models import GraphXPublishedGraph, PublishedGraph


class Command(BaseCommand):
    """Compare the serialized_graph between two graph publications."""

    help = (
        "Compare two graph publications and report structural differences.\n\n"
        "Usage:\n"
        "  Pass two publication IDs to compare them directly:\n"
        "    compare_graph_publications <pub_a> <pub_b>\n\n"
        "  Or pass a graph slug to compare its two most recent publications:\n"
        "    compare_graph_publications --slug <graph-slug>"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "publication_a",
            nargs="?",
            default=None,
            help="The publicationid of the older/base publication.",
        )
        parser.add_argument(
            "publication_b",
            nargs="?",
            default=None,
            help="The publicationid of the newer publication to compare against.",
        )
        parser.add_argument(
            "--slug",
            dest="slug",
            default=None,
            help="Graph slug whose two most recent publications will be compared.",
        )
        parser.add_argument(
            "--language",
            default="en",
            dest="language",
            help="Language code to use when fetching serialized_graph (default: en).",
        )

    def handle(self, *args, **options):
        lang = options["language"]

        if options["slug"]:
            pub_a, pub_b = self._get_two_most_recent_publications(options["slug"])
        elif options["publication_a"] and options["publication_b"]:
            pub_a = GraphXPublishedGraph.objects.get(
                publicationid=options["publication_a"]
            )
            pub_b = GraphXPublishedGraph.objects.get(
                publicationid=options["publication_b"]
            )
        else:
            raise CommandError(
                "Provide either two publication IDs as positional arguments, "
                "or a graph slug via --slug."
            )

        graph_a = self._get_serialized_graph(pub_a.publicationid, lang)
        graph_b = self._get_serialized_graph(pub_b.publicationid, lang)

        comparator = GraphPublicationComparator(graph_a, graph_b)

        self.stdout.write(f"\nComparing publications for graph: {graph_a.get('name')}")
        self.stdout.write(
            f"  A (older): {pub_a.publicationid}  [{pub_a.published_time}]"
        )
        self.stdout.write(
            f"  B (newer): {pub_b.publicationid}  [{pub_b.published_time}]"
        )
        self.stdout.write("")

        checks = [
            ("Nodes created / deleted", comparator.check_nodes_created_or_deleted),
            (
                "Nodegroups created / deleted",
                comparator.check_nodegroups_created_or_deleted,
            ),
            ("Nodegroup parent changed", comparator.check_nodegroup_parent_changed),
            (
                "Node → nodegroup assignment changed",
                comparator.check_node_nodegroup_changed,
            ),
            ("Node alias changed", comparator.check_node_alias_changed),
            ("Node datatype changed", comparator.check_node_datatype_changed),
            ("Node config changed", comparator.check_node_config_changed),
        ]

        all_operations = []
        any_changes = False

        for label, method in checks:
            ops = method()
            if ops:
                any_changes = True
                all_operations.extend(ops)
                self.stdout.write(self.style.WARNING(f"[{label}]"))
                for op in ops:
                    self.stdout.write(f"  {_format_op_for_display(op)}")
                self.stdout.write("")

        if not any_changes:
            self.stdout.write(
                self.style.SUCCESS("No differences found. No migration created.")
            )
            return

        graph_slug = graph_b.get("slug", "")
        app_label = settings.APP_NAME
        base_dir = Path(apps.get_app_config(app_label).path)
        migrations_dir = base_dir / "migrations" / "data_migrations"

        pub_b_id = str(pub_b.publicationid)
        if migrations_dir.exists():
            for existing_file in migrations_dir.glob("*.py"):
                if pub_b_id in existing_file.read_text():
                    self.stdout.write(
                        self.style.WARNING(
                            f"Migration for publication {pub_b_id} already exists in {existing_file.name}. Skipping."
                        )
                    )
                    return

        dependencies = self._compute_dependencies(app_label, migrations_dir)
        writer = MigrationWriter(
            graph_name=graph_a.get("name", ""),
            graph_slug=graph_slug,
            pub_a=pub_a,
            pub_b=pub_b,
            operations=all_operations,
            dependencies=dependencies,
        )
        output_path = self._next_migration_path(
            migrations_dir, graph_slug, all_operations
        )
        migrations_dir.mkdir(parents=True, exist_ok=True)
        output_path.write_text(writer.as_string())
        self.stdout.write(self.style.SUCCESS(f"Migration written to {output_path}"))

    def _compute_dependencies(
        self,
        app_label: str,
        data_migrations_dir: Path,
    ) -> list[tuple[str, str]]:
        if not data_migrations_dir.exists():
            return []
        data = sorted(
            f
            for f in data_migrations_dir.glob("[0-9][0-9][0-9][0-9]_*.py")
            if f.is_file()
        )
        if not data:
            return []
        return [(app_label, f"data_migrations.{data[-1].stem}")]

    def _next_migration_path(
        self, directory: Path, graph_slug: str, operations: list
    ) -> Path:
        nums = []
        if directory.exists():
            for f in directory.iterdir():
                m = re.match(r"^(\d+)", f.name)
                if m:
                    nums.append(int(m.group(1)))
        next_num = (max(nums) + 1) if nums else 1
        summary = self._build_migration_summary(graph_slug, operations)
        return directory / f"{next_num:04d}_{summary}.py"

    def _build_migration_summary(self, graph_slug: str, operations: list) -> str:
        op_types = {op["op"] for op in operations}
        parts = []
        if graph_slug:
            parts.append(re.sub(r"[^a-z0-9]+", "_", graph_slug.lower()).strip("_"))
        if "CreateNode" in op_types or "CreateNodeGroup" in op_types:
            parts.append("add_nodes")
        if "DeleteNode" in op_types or "DeleteNodeGroup" in op_types:
            parts.append("delete_nodes")
        if "AlterNodeDatatype" in op_types:
            parts.append("alter_datatype")
        if "AlterNodeAlias" in op_types:
            parts.append("alter_alias")
        if "AlterNodeConfig" in op_types:
            parts.append("alter_config")
        if "AlterNodeGroupParent" in op_types or "AlterNodeGroup" in op_types:
            parts.append("alter_nodegroup")
        if len(parts) <= (1 if graph_slug else 0):
            parts.append("update_publication")
        return "_".join(parts)[:80]

    def _get_two_most_recent_publications(self, slug):
        pubs = GraphXPublishedGraph.objects.filter(graph__slug=slug).order_by(
            "-published_time"
        )[:2]
        if len(pubs) < 2:
            raise CommandError(
                f"Graph with slug {slug!r} has fewer than two publications."
            )
        # pubs[0] is newer, pubs[1] is older — return (older, newer)
        return pubs[1], pubs[0]

    def _get_serialized_graph(self, publication_id, language):
        try:
            pub = PublishedGraph.objects.get(
                publication_id=publication_id, language_id=language
            )
        except PublishedGraph.DoesNotExist:
            raise CommandError(
                f"No PublishedGraph found for publicationid={publication_id!r} "
                f"and language={language!r}."
            )
        return pub.serialized_graph


class GraphPublicationComparator:
    """
    Compares two serialized_graph dicts (from published_graphs.serialized_graph).

    Each check_* method returns a (possibly empty) list of operation dicts that
    describe a single detected change.  The 'op' key names the operation type;
    all remaining keys are the operation's parameters.
    """

    def __init__(self, graph_a: dict, graph_b: dict):
        self.graph_a = graph_a
        self.graph_b = graph_b

        self.nodes_a: dict[str, dict] = {
            n["nodeid"]: n for n in graph_a.get("nodes", [])
        }
        self.nodes_b: dict[str, dict] = {
            n["nodeid"]: n for n in graph_b.get("nodes", [])
        }

        self.nodegroups_a: dict[str, dict] = {
            ng["nodegroupid"]: ng for ng in graph_a.get("nodegroups", [])
        }
        self.nodegroups_b: dict[str, dict] = {
            ng["nodegroupid"]: ng for ng in graph_b.get("nodegroups", [])
        }

    def check_nodes_created_or_deleted(self) -> list[dict]:
        ops = []
        ids_a, ids_b = set(self.nodes_a), set(self.nodes_b)

        for nodeid in sorted(ids_b - ids_a):
            n = self.nodes_b[nodeid]
            nodegroup_id = n.get("nodegroup_id")
            node_config = n.get("config") or {}
            ops.append(
                {
                    "op": "CreateNode",
                    "nodeid": nodeid,
                    "alias": n.get("alias"),
                    "datatype": n.get("datatype"),
                    "nodegroup_id": nodegroup_id,
                    "nodegroup_is_existing": nodegroup_id in self.nodegroups_a,
                    "default_value": node_config.get("defaultValue"),
                }
            )

        for nodeid in sorted(ids_a - ids_b):
            n = self.nodes_a[nodeid]
            nodegroup_id = n.get("nodegroup_id")
            ops.append(
                {
                    "op": "DeleteNode",
                    "nodeid": nodeid,
                    "alias": n.get("alias"),
                    "datatype": n.get("datatype"),
                    "nodegroup_id": nodegroup_id,
                    "nodegroup_is_existing": nodegroup_id in self.nodegroups_a,
                }
            )

        return ops

    def check_nodegroups_created_or_deleted(self) -> list[dict]:
        ops = []
        ids_a, ids_b = set(self.nodegroups_a), set(self.nodegroups_b)

        for ngid in sorted(ids_b - ids_a):
            ng = self.nodegroups_b[ngid]
            ops.append(
                {
                    "op": "CreateNodeGroup",
                    "nodegroupid": ngid,
                    "parent_nodegroup_id": ng.get("parentnodegroup_id"),
                }
            )

        for ngid in sorted(ids_a - ids_b):
            ng = self.nodegroups_a[ngid]
            ops.append(
                {
                    "op": "DeleteNodeGroup",
                    "nodegroupid": ngid,
                    "parent_nodegroup_id": ng.get("parentnodegroup_id"),
                }
            )

        return ops

    def check_nodegroup_parent_changed(self) -> list[dict]:
        ops = []
        for ngid in sorted(set(self.nodegroups_a) & set(self.nodegroups_b)):
            old = self.nodegroups_a[ngid].get("parentnodegroup_id")
            new = self.nodegroups_b[ngid].get("parentnodegroup_id")
            if old != new:
                ops.append(
                    {
                        "op": "AlterNodeGroupParent",
                        "nodegroupid": ngid,
                        "old_parent_nodegroup_id": old,
                        "new_parent_nodegroup_id": new,
                    }
                )
        return ops

    def check_node_nodegroup_changed(self) -> list[dict]:
        ops = []
        for nodeid in sorted(set(self.nodes_a) & set(self.nodes_b)):
            old = self.nodes_a[nodeid].get("nodegroup_id")
            new = self.nodes_b[nodeid].get("nodegroup_id")
            if old != new:
                ops.append(
                    {
                        "op": "AlterNodeGroup",
                        "nodeid": nodeid,
                        "alias": self.nodes_b[nodeid].get("alias"),
                        "old_nodegroup_id": old,
                        "new_nodegroup_id": new,
                    }
                )
        return ops

    def check_node_alias_changed(self) -> list[dict]:
        ops = []
        for nodeid in sorted(set(self.nodes_a) & set(self.nodes_b)):
            old = self.nodes_a[nodeid].get("alias")
            new = self.nodes_b[nodeid].get("alias")
            if old != new:
                ops.append(
                    {
                        "op": "AlterNodeAlias",
                        "nodeid": nodeid,
                        "old_alias": old,
                        "new_alias": new,
                    }
                )
        return ops

    # 6. Node datatype changed
    def check_node_datatype_changed(self) -> list[dict]:
        ops = []
        for nodeid in sorted(set(self.nodes_a) & set(self.nodes_b)):
            old = self.nodes_a[nodeid].get("datatype")
            new = self.nodes_b[nodeid].get("datatype")
            if old != new:
                ops.append(
                    {
                        "op": "AlterNodeDatatype",
                        "nodeid": nodeid,
                        "alias": self.nodes_b[nodeid].get("alias"),
                        "old_datatype": old,
                        "new_datatype": new,
                    }
                )
        return ops

    # 7. Node config changed
    def check_node_config_changed(self) -> list[dict]:
        ops = []
        for nodeid in sorted(set(self.nodes_a) & set(self.nodes_b)):
            old = self.nodes_a[nodeid].get("config")
            new = self.nodes_b[nodeid].get("config")
            if old != new:
                ops.append(
                    {
                        "op": "AlterNodeConfig",
                        "nodeid": nodeid,
                        "alias": self.nodes_b[nodeid].get("alias"),
                        "old_config": old,
                        "new_config": new,
                    }
                )
        return ops


def _format_op_for_display(op: dict) -> str:
    match op["op"]:
        case "CreateNode":
            return f"CREATED  node {op['nodeid']!r}  alias={op['alias']!r}  datatype={op['datatype']!r}"
        case "DeleteNode":
            return f"DELETED  node {op['nodeid']!r}  alias={op['alias']!r}  datatype={op['datatype']!r}"
        case "CreateNodeGroup":
            return f"CREATED  nodegroup {op['nodegroupid']!r}  parent={op['parent_nodegroup_id']!r}"
        case "DeleteNodeGroup":
            return f"DELETED  nodegroup {op['nodegroupid']!r}  parent={op['parent_nodegroup_id']!r}"
        case "AlterNodeGroupParent":
            return (
                f"nodegroup {op['nodegroupid']!r}  "
                f"parentnodegroup_id: {op['old_parent_nodegroup_id']!r} → {op['new_parent_nodegroup_id']!r}"
            )
        case "AlterNodeNodeGroup":
            return (
                f"node {op['nodeid']!r}  alias={op['alias']!r}  "
                f"nodegroup_id: {op['old_nodegroup_id']!r} → {op['new_nodegroup_id']!r}"
            )
        case "AlterNodeAlias":
            return f"node {op['nodeid']!r}  alias: {op['old_alias']!r} → {op['new_alias']!r}"
        case "AlterNodeDatatype":
            return (
                f"node {op['nodeid']!r}  alias={op['alias']!r}  "
                f"datatype: {op['old_datatype']!r} → {op['new_datatype']!r}"
            )
        case "AlterNodeConfig":
            return (
                f"node {op['nodeid']!r}  alias={op['alias']!r}  "
                f"config: {op['old_config']!r} → {op['new_config']!r}"
            )
        case _:
            return repr(op)


class MigrationWriter:
    def __init__(
        self,
        graph_name: str,
        graph_slug: str,
        pub_a: GraphXPublishedGraph,
        pub_b: GraphXPublishedGraph,
        operations: list[dict],
        dependencies: list[tuple[str, str]] | None = None,
    ):
        self.graph_name = graph_name
        self.graph_slug = graph_slug
        self.pub_a = pub_a
        self.pub_b = pub_b
        self.operations = operations
        self.dependencies = dependencies or []

    def as_string(self) -> str:
        now = datetime.datetime.now(tz=datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        imports = self._collect_imports()
        ops_block = self._render_operations()

        lines = [
            f"# Generated by Arches makedatamigrations on {now}",
            f"# Graph:            {self.graph_name} ({self.graph_slug})",
            f"# From publication: {self.pub_a.publicationid}  [{self.pub_a.published_time}]",
            f"# To publication:   {self.pub_b.publicationid}  [{self.pub_b.published_time}]",
            "",
            "from django.db import migrations",
            "from arches.db.migration_operations.data_migration_operations import (",
            *[f"    {name}," for name in imports],
            ")",
            "",
            "",
            "class Migration(migrations.Migration):",
            f"    # graph_slug = {self.graph_slug!r}",
            "",
            *self._render_dependencies(),
            "",
            "    operations = [",
            ops_block,
            "    ]",
            "",
        ]
        return "\n".join(lines)

    def _render_dependencies(self) -> list[str]:
        if not self.dependencies:
            return ["    initial = True", "    dependencies = []"]
        dep_lines = ["    dependencies = ["]
        for app, name in self.dependencies:
            dep_lines.append(f"        ({app!r}, {name!r}),")
        dep_lines.append("    ]")
        return dep_lines

    def _collect_imports(self) -> list[str]:
        needed = {"UpdateResourceInstancesPublicationId"}
        for op in self.operations:
            if op["op"] == "CreateNode" and op.get("nodegroup_is_existing"):
                needed.add("AddNodeToTileData")
            if op["op"] == "DeleteNode" and op.get("nodegroup_id"):
                needed.add("DeleteNodeFromTileData")
        return sorted(needed)

    def _render_operations(self) -> str:
        rendered = []
        for op in self.operations:
            rendered.append(self._render_op(op))
        rendered.append(self._render_update_publication_op())
        return "\n".join(rendered)

    def _render_op(self, op: dict) -> str:
        if op["op"] == "CreateNode" and op.get("nodegroup_is_existing"):
            return "\n".join(
                [
                    "        AddNodeToTileData(",
                    f"            publication_id={str(self.pub_a.publicationid)!r},",
                    f"            nodegroup_id={op['nodegroup_id']!r},",
                    f"            node_id={op['nodeid']!r},",
                    f"            value={op.get('default_value')!r},",
                    "        ),",
                ]
            )
        if op["op"] == "DeleteNode" and op.get("nodegroup_id"):
            return "\n".join(
                [
                    "        DeleteNodeFromTileData(",
                    f"            publication_id={str(self.pub_a.publicationid)!r},",
                    f"            nodegroup_id={op['nodegroup_id']!r},",
                    f"            node_id={op['nodeid']!r},",
                    f"            value=None,  # TODO: set default value for {op['alias']!r} ({op['datatype']!r})",
                    "        ),",
                ]
            )
        return f"        # {_format_op_for_display(op)}"

    def _render_update_publication_op(self) -> str:
        return "\n".join(
            [
                "        UpdateResourceInstancesPublicationId(",
                f"            current_publication_id={str(self.pub_a.publicationid)!r},",
                f"            updated_publication_id={str(self.pub_b.publicationid)!r},",
                "        ),",
            ]
        )
