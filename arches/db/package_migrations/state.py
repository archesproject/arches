"""In-memory state for package migrations: each graph's state is its canonical
dict, keyed by graphid, so diffing two states is dict comparison.
"""

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

# (state key, serialized_graph key, model)
COLLECTIONS = (
    ("nodes", "nodes", models.Node),
    ("nodegroups", "nodegroups", models.NodeGroup),
    ("edges", "edges", models.Edge),
    ("cards", "cards", models.CardModel),
    ("widgets", "cards_x_nodes_x_widgets", models.CardXNodeXWidget),
)

STATE_COLLECTIONS = tuple(entry[0] for entry in COLLECTIONS)


def collection_for(model):
    """The state key holding a model's rows, and the field that identifies them."""
    for state_key, _serialized_key, collection_model in COLLECTIONS:
        if collection_model is model:
            return state_key, collection_model._meta.pk.attname
    raise KeyError(f"{model.__name__} holds no package content")


def fields_for(model):
    """The package-content columns of a model, in declaration order."""
    return tuple(
        field.attname
        for field in model._meta.concrete_fields
        if field.attname not in EXCLUDED_FIELDS
    )


def _normalize(value):
    # Django's migration serializer raises on a dict mixing UUID and str keys.
    if isinstance(value, dict):
        return {str(key): _normalize(inner) for key, inner in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    return str(value)


def _project(source, fields):
    # Absent is not null: older exports lack NOT NULL columns such as alias.
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
    def __init__(self, package_state):
        self.package_state = package_state

    def clone(self):
        return _RenderedPackageApps(self.package_state)


class PackageState:
    """The package-data counterpart of ProjectState: ``graphs`` maps graphid to
    the graph's canonical dict."""

    def __init__(self, graphs=None):
        self.graphs = graphs if graphs is not None else {}
        # Graphs not in _owned are shared with the state this was cloned from.
        self._owned = set(self.graphs)

    def add_graph(self, graph):
        graphid = str(graph["graphid"])
        self.graphs[graphid] = graph
        self._owned.add(graphid)

    def graph(self, graphid):
        """The state entry for a graph, seeded when it was installed outside
        migration history (e.g. by load_package)."""
        graphid = str(graphid)
        if graphid not in self.graphs:
            self.graphs[graphid] = dict(
                {collection: {} for collection in STATE_COLLECTIONS},
                graphid=graphid,
            )
            self._owned.add(graphid)
        return self.graphs[graphid]

    def graph_for_write(self, graphid):
        """The graph, copied on first write. Row dicts stay shared, so an
        operation must replace a row rather than mutate it."""
        graphid = str(graphid)
        graph = self.graph(graphid)
        if graphid not in self._owned:
            graph = {
                key: dict(value) if isinstance(value, dict) else value
                for key, value in graph.items()
            }
            self.graphs[graphid] = graph
            self._owned.add(graphid)
        return graph

    @cached_property
    def apps(self):
        # MigrationExecutor reads and deletes state.apps; there is nothing to render.
        return _RenderedPackageApps(self)

    def clone(self):
        # Django clones before every operation, so a deep copy here is quadratic.
        new_state = PackageState(graphs=dict(self.graphs))
        new_state._owned = set()
        if "apps" in self.__dict__:
            new_state.apps = self.apps.clone()
        return new_state

    def __eq__(self, other):
        return isinstance(other, PackageState) and self.graphs == other.graphs

    def __repr__(self):
        return f"<PackageState graphs={sorted(self.graphs)!r}>"
