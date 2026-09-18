"""In-memory state for package migrations, and the projection that builds it.

The counterpart of ``django.db.migrations.state.ProjectState``, with one
deliberate difference.

Django needs ``ModelState`` because a Django model is not data: it is a class
with fields, managers, options and bases, and ModelState is a serializable
projection of it. An Arches graph is already JSON: ``Graph.serialize()``
returns a dict, the canonical projection returns a dict, and the committed
``pkg/graphs/*.json`` is a dict. Wrapping that in a state class would buy a
JSON-to-object mapping layer, an object-to-JSON layer for diffing, and a
hand-written clone/eq, for three representations of one thing.

So a graph's state IS its canonical dict, keyed by graphid. Operations mutate
those dicts, and diffing two states is dict comparison.
"""

import copy

from django.utils.functional import cached_property

from arches.app.models import models


# Real columns that are still not package content. Every entry needs a reason.
EXCLUDED_FIELDS = {
    # Implied by the graph that contains the row, and identical for every row in it.
    "graph_id",
    # Draft-graph linkage. Minted per install; says nothing about the package.
    "source_identifier_id",
    "sourcebranchpublication_id",
    # Publication state is owned by PublishGraph, not by the structural diff.
    "publication_id",
    "has_unpublished_changes",
}

# (state key, serialized_graph key, model). The pk field comes from the model.
COLLECTIONS = (
    ("nodes", "nodes", models.Node),
    ("nodegroups", "nodegroups", models.NodeGroup),
    ("edges", "edges", models.Edge),
    ("cards", "cards", models.CardModel),
    ("widgets", "cards_x_nodes_x_widgets", models.CardXNodeXWidget),
)


STATE_COLLECTIONS = tuple(entry[0] for entry in COLLECTIONS)


def collection_for(model):
    """Where a model's rows live in state, and what identifies them.

    COLLECTIONS is the one place this is written down; operations read it rather
    than each declaring their own copy.
    """
    for state_key, _serialized_key, collection_model in COLLECTIONS:
        if collection_model is model:
            return state_key, collection_model._meta.pk.attname
    raise KeyError("%s holds no package content" % model.__name__)


def fields_for(model):
    """The package-content columns of a model, in declaration order."""
    return tuple(
        field.attname
        for field in model._meta.concrete_fields
        if field.attname not in EXCLUDED_FIELDS
    )


def _normalize(value):
    """Coerce to JSON-native shapes so equality and hashing are stable.

    Tuples and lists compare unequal, and a dict mixing UUID and str keys raises
    inside Django's migration serializer, so keys are stringified here rather
    than blowing up later at codegen time.
    """
    if isinstance(value, dict):
        return {str(key): _normalize(inner) for key, inner in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    return str(value)


def _project(source, fields):
    """Only the fields the source actually carries.

    An absent key is not the same as null. A package exported by an older Arches
    has no `alias`, `hascustomalias` or `grouping_node_id`; projecting those to
    None would make every diff emit AlterNode(alias=None), which is written to
    disk, shipped, and only fails on the customer's database, because alias is NOT NULL.
    Absent keys simply produce no change, and the create path fills them from the
    model's own defaults.
    """
    return {field: _normalize(source[field]) for field in fields if field in source}


def canonical_graph(serialized_graph):
    """Project a serialized graph into PackageState's shape."""
    canonical = _project(serialized_graph, fields_for(models.GraphModel))
    canonical["graphid"] = str(canonical["graphid"])
    for state_key, serialized_key, model in COLLECTIONS:
        pk_field = model._meta.pk.attname
        entries = serialized_graph.get(serialized_key) or []
        canonical[state_key] = {
            str(entry[pk_field]): _project(entry, fields_for(model))
            for entry in entries
            if entry.get(pk_field) is not None
        }
    return canonical


class _RenderedPackageApps:
    """Inert stand-in for StateApps. See PackageState.apps."""

    def __init__(self, package_state):
        self.package_state = package_state

    def clone(self):
        return _RenderedPackageApps(self.package_state)


class PackageState:
    """The package-data counterpart of ProjectState.

    ``graphs`` maps graphid -> the graph's canonical dict, in exactly the shape
    the canonical projection emits and the committed package JSON stores:

        {
            "graphid": ..., "slug": ..., "name": {...}, "is_resource": bool,
            "nodes":      {nodeid: {...}},
            "nodegroups": {nodegroupid: {...}},
            "edges":      {edgeid: {...}},
            "cards":      {cardid: {...}},
            "widgets":    {cardxnodexwidgetid: {...}},
        }

    Collections are keyed maps rather than lists because Graph.serialize()
    assembles them from querysets with no guaranteed ordering, so list position
    is not a stable identity.
    """

    def __init__(self, graphs=None, real_apps=None):
        self.graphs = graphs if graphs is not None else {}
        self.real_apps = set(real_apps) if real_apps else set()

    def add_graph(self, graph):
        self.graphs[str(graph["graphid"])] = graph

    def graph(self, graphid):
        """The state entry for a graph, seeded if the history never created it.

        Unlike a Django model, an Arches graph can arrive outside migration
        history: `packages -o load_package` installs the graphs an application
        ships. A migration that modifies such a graph is legitimate and must not
        fail on replay just because no CreateGraph precedes it.

        The corollary is that replayed state is incomplete for those graphs, so
        the first package migration for an already-installed package has to be
        stamped rather than replayed.
        """
        graphid = str(graphid)
        if graphid not in self.graphs:
            self.graphs[graphid] = dict(
                {collection: {} for collection in STATE_COLLECTIONS},
                graphid=graphid,
            )
        return self.graphs[graphid]

    @cached_property
    def apps(self):
        """MigrationExecutor touches ``state.apps`` unconditionally on the
        forward path and does ``del state.apps`` on the reverse path, so the
        attribute must exist in the instance __dict__ and be deletable. There is
        no model registry to render for package data, so this is an inert
        sentinel that exists only to satisfy that caching dance.
        """
        return _RenderedPackageApps(self)

    def clone(self):
        # deepcopy because node/card dicts nest arbitrary `config` JSON that an
        # operation could otherwise mutate through a shared reference. unapply()
        # clones twice per operation, so if this ever shows up in a profile the
        # answer is structural sharing, not a shallower copy.
        new_state = PackageState(
            graphs=copy.deepcopy(self.graphs),
            real_apps=self.real_apps,
        )
        if "apps" in self.__dict__:
            new_state.apps = self.apps.clone()
        return new_state

    def __eq__(self, other):
        return isinstance(other, PackageState) and self.graphs == other.graphs

    def __repr__(self):
        return "<PackageState graphs=%r>" % sorted(self.graphs)
