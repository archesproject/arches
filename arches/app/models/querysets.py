from django.db import models

from arches.app.models.utils import field_names


# TODO: figure out best layer for reuse
def _generate_annotations(nodes, defer, only, invalid_names, for_resource=True):
    from arches.app.datatypes.datatypes import DataTypeFactory

    if defer and only and (overlap := set(defer).intersection(set(only))):
        raise ValueError(f"Got intersecting defer/only args: {overlap}")
    datatype_factory = DataTypeFactory()
    node_alias_annotations = {}
    node_aliases_by_node_id = {}
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
        tile_lookup = datatype_instance.get_orm_lookup(node, for_resource=for_resource)
        node_alias_annotations[node.alias] = tile_lookup
        node_aliases_by_node_id[str(node.pk)] = node.alias

    if not node_alias_annotations:
        raise ValueError("All fields were excluded.")
    for given_alias in only or []:
        if given_alias not in node_alias_annotations:
            raise ValueError(f'"{given_alias}" is not a valid node alias.')

    return node_alias_annotations, node_aliases_by_node_id


class TileQuerySet(models.QuerySet):
    @staticmethod
    def _root_node_for_nodegroup(graph_slug, root_node_alias):
        from arches.app.models.models import Node

        qs = (
            Node.objects.filter(graph__slug=graph_slug, alias=root_node_alias)
            .select_related("nodegroup")
            .prefetch_related("nodegroup__node_set")
            # Prefetching to a depth of 2 seems like a good trade-off for now.
            .prefetch_related("nodegroup__nodegroup_set")
            .prefetch_related("nodegroup__nodegroup_set__nodegroup_set")
        )
        # TODO: make deterministic by checking source_identifier
        # https://github.com/archesproject/arches/issues/11565
        ret = qs.last()
        if ret is None:
            raise Node.DoesNotExist(f"graph: {graph_slug} node: {root_node_alias}")
        return ret

    def with_node_values(self, nodes, *, defer=None, only=None, depth=1):
        from arches.app.models.models import TileModel

        node_alias_annotations, node_aliases_by_node_id = _generate_annotations(
            nodes,
            defer=defer,
            only=only,
            invalid_names=field_names(self.model),
            for_resource=False,
        )

        prefetches = ["resourceinstance__graph__node_set"]
        if depth:
            prefetches.append(
                models.Prefetch(
                    "parenttile",
                    queryset=TileModel.objects.with_node_values(
                        nodes, defer=defer, only=only, depth=depth - 1
                    ),
                )
            )
        return (
            self.prefetch_related(*prefetches)
            .annotate(
                **node_alias_annotations,
            )
            .annotate(
                _fetched_nodes=models.Value(
                    node_aliases_by_node_id,
                    output_field=models.JSONField(),
                )
            )
            .order_by("sortorder")
        )

    def as_nodegroup(self, root_node_alias, *, graph_slug, defer=None, only=None):
        root_node = self._root_node_for_nodegroup(graph_slug, root_node_alias)

        def accumulate_nodes_below(nodegroup, acc):
            acc.extend(list(nodegroup.node_set.all()))
            for child_nodegroup in nodegroup.nodegroup_set.all():
                accumulate_nodes_below(child_nodegroup, acc)

        branch_nodes = []
        accumulate_nodes_below(root_node.nodegroup, acc=branch_nodes)

        return (
            self.filter(nodegroup_id=root_node.pk)
            .with_node_values(branch_nodes, defer=defer, only=only)
            .annotate(_nodegroup_alias=models.Value(root_node_alias))
        )

    def _fetch_all(self):
        """Call datatype to_python() methods when materializing the QuerySet."""
        from arches.app.datatypes.datatypes import DataTypeFactory

        super()._fetch_all()

        datatype_factory = DataTypeFactory()
        datatypes_by_nodeid = {}

        try:
            first_tile = self._result_cache[0]
        except IndexError:
            return
        for node in first_tile.resourceinstance.graph.node_set.all():
            datatypes_by_nodeid[str(node.pk)] = datatype_factory.get_instance(
                node.datatype
            )

        NOT_PROVIDED = object()
        for tile in self._result_cache:
            for nodeid, alias in getattr(tile, "_fetched_nodes", {}).items():
                tile_val = getattr(tile, alias, NOT_PROVIDED)
                if tile_val is not NOT_PROVIDED:
                    datatype_instance = datatypes_by_nodeid[nodeid]
                    try:
                        python_val = datatype_instance.to_python(tile_val)
                    except:
                        # TODO: some things break because datatype orm lookups
                        # need to be reoriented around nodegroups (next)
                        continue
                    setattr(tile, alias, python_val)


class ResourceInstanceQuerySet(models.QuerySet):
    def with_tiles(self, graph_slug=None, *, resource_ids=None, defer=None, only=None):
        """Annotates a ResourceInstance QuerySet with tile data unpacked
        and mapped onto node aliases, e.g.:

        >>> ResourceInstance.objects.with_tiles("concept")

        With slightly fewer keystrokes:

        >>> ResourceInstance.as_model("concept")

        Or with defer/only as in the QuerySet interface:

        >>> ResourceInstance.as_model("concept", only=["alias1", "alias2"])

        Example:

        >>> concepts = ResourceInstance.as_model("concepts")
        >>> result = concepts.filter(my_node_alias="some tile value")
        >>> result.first().my_node_alias
        "some tile value"

        Provisional edits are completely ignored.
        """
        from arches.app.models.models import GraphModel, TileModel

        if resource_ids and not graph_slug:
            graph_query = GraphModel.objects.filter(resourceinstance__in=resource_ids)
        else:
            graph_query = GraphModel.objects.filter(
                slug=graph_slug, source_identifier=None
            )
        try:
            source_graph = graph_query.prefetch_related("node_set__nodegroup").get()
        except GraphModel.DoesNotExist as e:
            e.add_note(f"No graph found with slug: {graph_slug}")
            raise

        nodes = source_graph.node_set.all()
        node_alias_annotations, node_aliases_by_node_id = _generate_annotations(
            nodes,
            defer=defer,
            only=only,
            invalid_names=field_names(self.model),
            for_resource=True,
        )

        if resource_ids:
            qs = self.filter(pk__in=resource_ids)
        else:
            qs = self.filter(graph=source_graph)
        return (
            qs.prefetch_related(
                "graph__node_set__nodegroup",
                models.Prefetch(
                    "tilemodel_set",
                    queryset=TileModel.objects.with_node_values(
                        nodes, defer=defer, only=only
                    ),
                    to_attr="_pythonic_nodegroups",
                ),
            )
            .annotate(
                **node_alias_annotations,
            )
            .annotate(
                _fetched_nodes=models.Value(
                    node_aliases_by_node_id,
                    output_field=models.JSONField(),
                )
            )
        )

    def _prefetch_related_objects(self):
        """Attach annotated tiles to resource instances."""
        super()._prefetch_related_objects()

        for resource in self._result_cache:
            annotated_tiles = getattr(resource, "_pythonic_nodegroups", [])
            for annotated_tile in annotated_tiles:
                # TODO: move responsibility for cardinality N compilation to here.
                # TODO: remove queries as part of filtering in with_node_values().
                setattr(resource, annotated_tile.nodegroup_alias, annotated_tile)
                if (
                    annotated_tile.parenttile
                    and annotated_tile.parenttile.nodegroup_alias
                ):
                    setattr(
                        annotated_tile,
                        annotated_tile.parenttile.nodegroup_alias,
                        annotated_tile.parenttile,
                    )
