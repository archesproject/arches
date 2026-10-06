"""Where a database sits in a plan of package migrations, and what would break.

Package migrations are generated from the database they were authored on, not
from the database being migrated, and a graph is rows a curator can edit in the
Graph Designer at runtime.

On a graph that has diverged, the failures are silent. An AlterNode for a node
the site deleted updates zero rows and reports success. A CreateNode for a node
the site already added collides, or quietly writes over it.

So before applying, check the rows the plan is about to write: whether they are
there, not what they contain. Field-level comparison is deliberately out of scope
-- it needs a three-way merge against the last-applied package snapshot, and it
would report false conflicts for i18n fields, which serialize per active language.
"""

import collections

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    _AlterRowOperation,
    _CreateRowOperation,
    _DeleteRowOperation,
)
from arches.db.package_migrations.operations.graph import CreateGraph, PublishGraph
from arches.db.package_migrations.operations.nodegroup import CreateNodeGroup
from arches.db.package_migrations.state import COLLECTIONS

# Rows the migrations create themselves; anything else a row points at has to be
# installed already.
GRAPH_ROW_MODELS = {entry[2] for entry in COLLECTIONS} | {models.GraphModel}


# kind is "present" (a row the plan creates is already there), "missing" (a row it
# changes or deletes is not), "reference" (something outside the graph that a row
# points at is not installed), "destructive" or "orphans" (what unapplying would
# destroy). Which one it is decides what the operator should do next.
Problem = collections.namedtuple("Problem", "kind message")

# position: how many of the migrations this database already has, None when no
# point fits. ambiguous: every fitting position, when rows are deleted and
# recreated between them.
Fit = collections.namedtuple("Fit", "position problems ambiguous")


def fit(migrations, using):
    """Where this database sits in one app's forward plan, in plan order."""
    transitions = [_transitions(migration) for migration in migrations]
    existing = _existing(
        {key for rows in transitions for key, _before, _after in rows}, using
    )
    earliest = _earliest_position(migrations, using)
    consistent = [
        position
        for position in range(earliest, len(migrations) + 1)
        if not _mismatches(transitions, existing, position)
    ]
    if not consistent:
        return Fit(
            None,
            [
                _mismatch_problem(migrations[index], model, primary_key, expected)
                for index, (model, primary_key), expected in _mismatches(
                    transitions, existing, earliest
                )
            ],
            [],
        )
    if _recreated(transitions[consistent[0] : consistent[-1]]):
        return Fit(consistent[0], [], consistent)
    return Fit(consistent[0], [], [])


def missing_references(plan, using):
    """A graph is not self-contained: it points at an ontology, a template, card
    components and widgets, which a package installs through load_package rather
    than through graph rows. Without this the first sign of trouble is a
    DoesNotExist raised deep inside Graph.publish().
    """
    wanted = collections.defaultdict(dict)
    for migration, backwards in plan:
        if backwards:
            continue
        for operation in migration.operations:
            for model, primary_key in _references(operation):
                wanted[model].setdefault(primary_key, migration)

    found = []
    for model, users in wanted.items():
        present = {
            str(primary_key)
            for primary_key in model.objects.using(using)
            .filter(pk__in=users)
            .values_list("pk", flat=True)
        }
        for primary_key in sorted(set(users) - present):
            migration = users[primary_key]
            found.append(
                Problem(
                    "reference",
                    f"{model.__name__} {primary_key}, used by "
                    f"{migration.app_label}.{migration.name}",
                )
            )
    return found


def reverse_problems(plan, using):
    """Unapplying recreates rows from replayed state, so the forward checks do
    not hold in reverse. What does matter is what a reversal destroys."""
    found = []
    for migration, backwards in plan:
        if not backwards:
            continue
        label = f"{migration.app_label}.{migration.name}"
        for operation in migration.operations:
            if isinstance(operation, CreateGraph) and operation.has_resources(using):
                found.append(
                    Problem(
                        "destructive",
                        f"{label}: graph {operation.graphid} has resources",
                    )
                )
            elif isinstance(operation, CreateNodeGroup):
                tile_count = (
                    models.TileModel.objects.using(using)
                    .filter(nodegroup_id=operation._pk)
                    .count()
                )
                if tile_count:
                    found.append(
                        Problem(
                            "orphans",
                            f"{label}: nodegroup {operation._pk} has {tile_count} tiles",
                        )
                    )
    return found


def _transitions(migration):
    rows = []
    for operation in migration.operations:
        if isinstance(operation, CreateGraph):
            rows.append(((models.GraphModel, operation.graphid), False, True))
        elif isinstance(operation, _CreateRowOperation):
            rows.append(((operation.model, operation._pk), False, True))
        elif isinstance(operation, _DeleteRowOperation):
            rows.append(((operation.model, operation._pk), True, False))
        elif isinstance(operation, _AlterRowOperation):
            rows.append(((operation.model, operation._pk), True, True))
    return rows


def _existing(keys, using):
    primary_keys_by_model = collections.defaultdict(set)
    for model, primary_key in keys:
        primary_keys_by_model[model].add(primary_key)
    existing = set()
    for model, primary_keys in primary_keys_by_model.items():
        existing.update(
            (model, str(primary_key))
            for primary_key in model.objects.using(using)
            .filter(pk__in=primary_keys)
            .values_list("pk", flat=True)
        )
    return existing


def _earliest_position(migrations, using):
    """A new publication only exists where its migration ran. Not finding one
    proves nothing: a site that faked its history has publications of its own."""
    earliest = 0
    for index, migration in enumerate(migrations):
        published = [
            operation.publication_id
            for operation in migration.operations
            if isinstance(operation, PublishGraph) and not operation.updates_in_place
        ]
        if (
            published
            and models.GraphXPublishedGraph.objects.using(using)
            .filter(pk__in=published)
            .exists()
        ):
            earliest = index + 1
    return earliest


def _mismatches(transitions, existing, position):
    expected = {}
    for index, rows in enumerate(transitions):
        for key, before, after in rows:
            if index < position:
                expected[key] = (index, after)
            elif key not in expected:
                expected[key] = (index, before)
    return [
        (index, key, present)
        for key, (index, present) in expected.items()
        if present != (key in existing)
    ]


def _recreated(transitions):
    """Rows deleted and then created again. Creating a row and later deleting it
    destroys nothing when replayed, so only this order makes positions ambiguous."""
    deleted, recreated = set(), set()
    for rows in transitions:
        for key, before, after in rows:
            if before and not after:
                deleted.add(key)
            elif after and not before and key in deleted:
                recreated.add(key)
    return recreated


def _mismatch_problem(migration, model, primary_key, expected):
    label = f"{migration.app_label}.{migration.name}"
    if expected:
        return Problem("missing", f"{label}: {model.__name__} {primary_key} is missing")
    return Problem(
        "present", f"{label}: {model.__name__} {primary_key} is already here"
    )


def _references(operation):
    """(model, pk) an operation points at outside the graph's own rows."""
    model = getattr(operation, "model", None)
    values = getattr(operation, "fields", None) or getattr(operation, "changes", None)
    if model is None or not values:
        return
    for name, value in values.items():
        if value is None or not name.endswith("_id"):
            continue
        try:
            field = model._meta.get_field(name[: -len("_id")])
        except Exception:
            continue
        if not field.is_relation or field.related_model in GRAPH_ROW_MODELS:
            continue
        yield field.related_model, str(value)
