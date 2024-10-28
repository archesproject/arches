from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import OuterRef, Prefetch, QuerySet, Subquery, Value
from django.db.models.expressions import BaseExpression

from arches.app.models.utils import field_names


class TileQuerySet(QuerySet):
    @staticmethod
    def _root_node_for_nodegroup(graph_slug, root_node_alias):
        from arches.app.models.models import Node

        qs = (
            Node.objects.filter(graph__slug=graph_slug, alias=root_node_alias)
            .select_related("nodegroup")
            .prefetch_related("nodegroup__node_set")
            # Prefetching to a depth of 2 seems like a good trade-off for now.
            .prefetch_related("nodegroup__children")
            .prefetch_related("nodegroup__children__children")
        )
        # TODO: get last
        # https://github.com/archesproject/arches/issues/11565
        ret = qs.filter(source_identifier=None).first()
        if ret is None:
            raise Node.DoesNotExist(f"graph: {graph_slug} node: {root_node_alias}")
        return ret

    def with_node_values(
        self, nodes, *, defer=None, only=None, lhs=None, outer_ref, depth=1
    ):
        from arches.app.models.models import TileModel

        node_alias_annotations = _generate_tile_annotations(
            nodes,
            defer=defer,
            only=only,
            invalid_names=field_names(self.model),
            lhs=lhs,
            outer_ref=outer_ref,
        )

        prefetches = []
        if depth:
            prefetches.append(
                Prefetch(
                    "children",
                    queryset=TileModel.objects.with_node_values(
                        nodes,
                        defer=defer,
                        only=only,
                        depth=depth - 1,
                        lhs="parenttile",
                        outer_ref="tileid",
                    ),
                )
            )

        self._fetched_nodes = [n for n in nodes if n.alias in node_alias_annotations]
        return (
            self.filter(data__has_any_keys=[n.pk for n in self._fetched_nodes])
            .prefetch_related(*prefetches)
            .annotate(
                **node_alias_annotations,
            )
            .order_by("sortorder")
        )

    def as_nodegroup(self, root_node_alias, *, graph_slug, defer=None, only=None):
        """
        Entry point for filtering arches data by nodegroups (instead of grouping by
        resource.)

        >>> statements = TileModel.objects.as_nodegroup("statement", graph_slug="concept")
        >>> results = statements.filter(statement_content__0__en__value__startswith="F")  # todo: make more ergonomic, remove limitation of 0
        >>> for result in results:
                print(result.resourceinstance)
                print("\t", result.statement_content[0]["en"]["value"])  # TODO: unwrap/string viewmodel

        <Concept: x-ray fluorescence (aec56d59-9292-42d6-b18e-1dd260ff446f)>
            Fluorescence stimulated by x-rays; ...
        <Concept: vellum (parchment) (34b081cd-6fcc-4e00-9a43-0a8a73745b45)>
            Fine-quality calf or lamb parchment ...
        """

        root_node = self._root_node_for_nodegroup(graph_slug, root_node_alias)

        def accumulate_nodes_below(nodegroup, acc):
            acc.extend(list(nodegroup.node_set.all()))
            for child_nodegroup in nodegroup.children.all():
                accumulate_nodes_below(child_nodegroup, acc)

        branch_nodes = []
        accumulate_nodes_below(root_node.nodegroup, acc=branch_nodes)

        return (
            self.filter(nodegroup_id=root_node.pk)
            .with_node_values(
                branch_nodes, defer=defer, only=only, lhs="pk", outer_ref="tileid"
            )
            .annotate(_nodegroup_alias=Value(root_node_alias))
        )

    def _prefetch_related_objects(self):
        """Call datatype to_python() methods when materializing the QuerySet.
        Discard annotations that do not pertain to this nodegroup.
        """
        from arches.app.datatypes.datatypes import DataTypeFactory

        super()._prefetch_related_objects()

        datatype_factory = DataTypeFactory()
        NOT_PROVIDED = object()
        for tile in self._result_cache:
            for node in self._fetched_nodes:
                if node.nodegroup_id == tile.nodegroup_id:
                    tile_val = getattr(tile, node.alias, NOT_PROVIDED)
                    if tile_val is not NOT_PROVIDED:
                        datatype_instance = datatype_factory.get_instance(node.datatype)
                        python_val = datatype_instance.to_python(tile_val)
                        setattr(tile, node.alias, python_val)
                else:
                    delattr(tile, node.alias)

    def _clone(self):
        ret = super()._clone()
        if hasattr(self, "_fetched_nodes"):
            ret._fetched_nodes = self._fetched_nodes
        return ret


class ResourceInstanceQuerySet(QuerySet):
    def with_tiles(self, graph_slug=None, *, resource_ids=None, defer=None, only=None):
        """Annotates a ResourceInstance QuerySet with tile data unpacked
        and mapped onto node aliases, e.g.:

        >>> concepts = ResourceInstance.objects.with_tiles("concept")

        With slightly fewer keystrokes:

        >>> concepts = ResourceInstance.as_model("concept")

        Or with defer/only as in the QuerySet interface:

        >>> partial_concepts = ResourceInstance.as_model("concept", only=["n1", "n2"])

        Example:

        >>> from arches.app.models.models import *
        >>> concepts = ResourceInstance.as_model("concept")

        Django QuerySet methods are available for efficient queries:
        >>> concepts.count()
        785

        Filter on any nested node at the top level ("shallow query")

        >>> subset = concepts.filter(statement_content__isnull=False)[:4]

        Access through nodegroup names:

        >>> for concept in subset:
                print(concept)
                for stmt in concept.statement:  # TODO: should name with _set (?)
                    print("\t", stmt)
                    print("\t\t", stmt.statement_content)

        <Concept: consignment (method of acquisition) (f3fed7aa-eae6-41f6-aa0f-b889d84c0552)>
            <TileModel: statement (46efcd06-a5e5-43be-8847-d7cd94cbc9cb)>
                [{'en': {'value': 'Method of acquiring property ...
        ...

        Provisional edits are completely ignored.
        """
        from arches.app.models.models import GraphModel, NodeGroup, TileModel

        if resource_ids and not graph_slug:
            graph_query = GraphModel.objects.filter(resourceinstance__in=resource_ids)
        else:
            graph_query = GraphModel.objects.filter(
                slug=graph_slug, source_identifier=None
            )
        try:
            # Prefetch sibling nodes for use in _prefetch_related_objects()
            source_graph = graph_query.prefetch_related(
                "node_set__nodegroup__node_set"
            ).get()
        except GraphModel.DoesNotExist as e:
            e.add_note(f"No graph found with slug: {graph_slug}")
            raise

        nodes = source_graph.node_set.all()
        node_alias_annotations = _generate_tile_annotations(
            nodes,
            defer=defer,
            only=only,
            invalid_names=field_names(self.model),
            lhs=None,  # TODO: AWKWARD
            outer_ref="resourceinstanceid",
        )
        self._fetched_nodes = [n for n in nodes if n.alias in node_alias_annotations]
        # TODO: there might be some way to prune unused annotations.

        if resource_ids:
            qs = self.filter(pk__in=resource_ids)
        else:
            qs = self.filter(graph=source_graph)
        return qs.prefetch_related(
            "graph__node_set__nodegroup",
            Prefetch(
                "tilemodel_set",
                queryset=TileModel.objects.with_node_values(
                    self._fetched_nodes,
                    defer=defer,
                    only=only,
                    lhs="pk",
                    outer_ref="tileid",
                ).annotate(
                    cardinality=NodeGroup.objects.filter(
                        pk=OuterRef("nodegroup_id")
                    ).values("cardinality")
                ),
                to_attr="_annotated_tiles",
            ),
        ).annotate(
            **node_alias_annotations,
        )

    def _prefetch_related_objects(self):
        """Attach annotated tiles to resource instances, at the root, by
        nodegroup alias. TODO: consider building as a nested structure.
        Discard annotations only used for shallow filtering.
        """
        super()._prefetch_related_objects()

        root_nodes = []
        for node in self._fetched_nodes:
            # TODO: less roundabout lookup, see earlier siblings prefetch.
            root_node = None
            for sibling_node in node.nodegroup.node_set.all():
                if sibling_node.pk == node.nodegroup_id:
                    root_node = sibling_node
                    break
            root_nodes.append(root_node)

        for resource in self._result_cache:
            for node in self._fetched_nodes:
                delattr(resource, node.alias)
            for root_node in root_nodes:
                setattr(
                    resource,
                    root_node.alias,
                    None if root_node.nodegroup.cardinality == "1" else [],
                )
            annotated_tiles = getattr(resource, "_annotated_tiles", [])
            for annotated_tile in annotated_tiles:
                for root_node in root_nodes:
                    if root_node.pk == annotated_tile.nodegroup_id:
                        ng_alias = root_node.alias
                        break
                else:
                    raise RuntimeError("missing root node for annotated tile")

                if annotated_tile.cardinality == "n":
                    tile_array = getattr(resource, ng_alias)
                    tile_array.append(annotated_tile)
                else:
                    setattr(resource, ng_alias, annotated_tile)

                for child_tile in annotated_tile.children.all():
                    setattr(child_tile, ng_alias, annotated_tile.parenttile)

    def _clone(self):
        ret = super()._clone()
        if hasattr(self, "_fetched_nodes"):
            ret._fetched_nodes = self._fetched_nodes
        return ret


def _generate_tile_annotations(nodes, *, defer, only, invalid_names, lhs, outer_ref):
    from arches.app.datatypes.datatypes import DataTypeFactory

    if defer and only and (overlap := set(defer).intersection(set(only))):
        raise ValueError(f"Got intersecting defer/only args: {overlap}")
    datatype_factory = DataTypeFactory()
    node_alias_annotations = {}
    for node in nodes:
        if node.datatype == "semantic":
            continue
        if node.nodegroup_id is None:
            continue
        if (defer and node.alias in defer) or (only and node.alias not in only):
            continue
        if node.alias in invalid_names:
            raise ValueError(f'"{node.alias}" clashes with a model field name.')

        datatype_instance = datatype_factory.get_instance(node.datatype)
        tile_values_query = _get_values_query(
            nodegroup=node.nodegroup,
            base_lookup=datatype_instance.get_base_orm_lookup(node),
            lhs=lhs,
            outer_ref=outer_ref,
        )
        node_alias_annotations[node.alias] = tile_values_query

    if not node_alias_annotations:
        raise ValueError("All fields were excluded.")
    for given_alias in only or []:
        if given_alias not in node_alias_annotations:
            raise ValueError(f'"{given_alias}" is not a valid node alias.')

    return node_alias_annotations


def _get_values_query(
    nodegroup, base_lookup, *, lhs=None, outer_ref=None
) -> BaseExpression:
    """Return a tile values query expression for use in a
    ResourceInstanceQuerySet or TileQuerySet.
    """
    from arches.app.models.models import TileModel

    # TODO: make this a little less fragile.
    if lhs is None:
        tile_query = TileModel.objects.filter(
            nodegroup_id=nodegroup.pk, resourceinstance_id=OuterRef(outer_ref)
        )
    elif lhs and outer_ref:
        tile_query = TileModel.objects.filter(**{lhs: OuterRef(outer_ref)})
    else:
        tile_query = TileModel.objects.filter(nodegroup_id=nodegroup.pk)
    if nodegroup.cardinality == "n":
        tile_query = tile_query.order_by("sortorder")

    tile_query = tile_query.values(base_lookup)

    if outer_ref == "tileid":
        return Subquery(tile_query)
    else:
        return ArraySubquery(tile_query)
