"""In-memory state for package migrations.

The counterpart of ``django.db.migrations.state.ProjectState``, with one
deliberate difference.

Django needs ``ModelState`` because a Django model is not data: it is a class
with fields, managers, options and bases, and ModelState is a serializable
projection of it. An Arches graph is already JSON -- ``Graph.serialize()``
returns a dict, the canonical projection returns a dict, and the committed
``pkg/graphs/*.json`` is a dict. Wrapping that in a state class would buy a
JSON-to-object mapping layer, an object-to-JSON layer for diffing, and a
hand-written clone/eq, for three representations of one thing.

So a graph's state IS its canonical dict, keyed by graphid. Operations mutate
those dicts, and diffing two states is dict comparison.
"""

import copy

from django.utils.functional import cached_property


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
        self.is_delayed = False

    def add_graph(self, graph):
        self.graphs[str(graph["graphid"])] = graph

    def remove_graph(self, graphid):
        del self.graphs[str(graphid)]

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
        new_state.is_delayed = self.is_delayed
        return new_state

    def __eq__(self, other):
        return isinstance(other, PackageState) and self.graphs == other.graphs

    def __repr__(self):
        return "<PackageState graphs=%r>" % sorted(self.graphs)
