"""Draft graphs are derived state, not a change to replay.

Every Arches graph carries a draft copy, and the Graph Designer's only save path
is promote_draft_graph_to_active_graph(), which rebuilds the live graph entirely
from that draft. A migration that leaves the draft stale is silently reverted by
the next publish, which also CASCADE-deletes tiles in any nodegroup it added --
while the ledger still says applied.

The draft is a function of the graph as it now stands, so it is reconciled once
at the end of a run rather than carried as an operation. That matters for more
than tidiness: as an operation it had no meaningful reverse, which made every
generated graph migration irreversible and blocked stepping a graph back through
its versions. Reconciling instead works in both directions, and a run that walks
ten versions rebuilds the draft once rather than ten times.
"""

from arches.app.models.graph import Graph


def graphs_in(plan):
    """The graph ids a migration plan touches, in the order it touches them."""
    graphids = []
    for migration, _backwards in plan:
        for operation in migration.operations:
            graphid = getattr(operation, "graphid", None)
            if graphid and str(graphid) not in graphids:
                graphids.append(str(graphid))
    return graphids


def reconcile(graphids, using):
    """Regenerate each graph's draft from its current state."""
    for graphid in graphids:
        graph = Graph.objects.using(using).filter(pk=graphid).first()
        if graph is None:
            # Reversed past the migration that created it.
            continue
        if graph.get_draft_graph():
            graph.delete_draft_graph()
        graph.create_draft_graph()
