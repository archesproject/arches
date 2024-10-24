from django.db import models

from arches.app.models.utils import field_names


# TODO: figure out best layer for reuse
def _generate_annotation_maps(nodes, defer, only, invalid_names, for_resource=True):
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
    def _top_node_for_nodegroup(graph_slug, top_node_alias):
        from arches.app.models.models import Node

        # TODO: avoidable if I already have a node_set?
        qs = (
            Node.objects.filter(graph__slug=graph_slug, alias=top_node_alias)
            .select_related("nodegroup")
            .prefetch_related("nodegroup__node_set")
        )
        # TODO: make deterministic by checking source_identifier
        # https://github.com/archesproject/arches/issues/11565
        ret = qs.last()
        if ret is None:
            raise Node.DoesNotExist
        return ret

    def with_node_values(self, top_node_or_alias, *, graph_slug, defer=None, only=None):
        if isinstance(top_node_or_alias, str):
            node_for_group = self._top_node_for_nodegroup(graph_slug, top_node_or_alias)
        else:
            node_for_group = top_node_or_alias
        node_alias_annotations, node_aliases_by_node_id = _generate_annotation_maps(
            node_for_group.nodegroup.node_set.all(),
            defer=defer,
            only=only,
            invalid_names=field_names(self.model),
            for_resource=False,
        )
        return self.annotate(
            **node_alias_annotations,
        ).annotate(
            _fetched_nodes=models.Value(
                node_aliases_by_node_id,
                output_field=models.JSONField(),
            )
        )

    def as_nodegroup(self, top_node_alias, *, graph_slug, defer=None, only=None):
        node_for_group = self._top_node_for_nodegroup(graph_slug, top_node_alias)
        return self.filter(nodegroup_id=node_for_group.pk).with_node_values(
            node_for_group, graph_slug=graph_slug, defer=defer, only=only
        )


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
        from arches.app.models.models import GraphModel, NodeGroup, TileModel

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

        node_alias_annotations, node_aliases_by_node_id = _generate_annotation_maps(
            source_graph.node_set.all(),
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
                    queryset=TileModel.objects.filter(
                        nodegroup_id__in=NodeGroup.objects.filter(
                            node__alias__in=node_alias_annotations
                        )
                    ).order_by("sortorder"),
                    to_attr="_sorted_tiles_for_fetched_nodes",
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

    def _fetch_all(self):
        """Call datatype to_python() methods when evaluating queryset."""
        from arches.app.datatypes.datatypes import DataTypeFactory

        super()._fetch_all()

        datatype_factory = DataTypeFactory()
        datatypes_by_nodeid = {}
        nodegroups_by_nodeid = {}

        try:
            first_resource = self._result_cache[0]
        except IndexError:
            return
        for node in first_resource.graph.node_set.all():
            datatypes_by_nodeid[str(node.pk)] = datatype_factory.get_instance(
                node.datatype
            )
            nodegroups_by_nodeid[str(node.pk)] = node.nodegroup

        for resource in self._result_cache:
            if not hasattr(resource, "_fetched_nodes"):
                # On the first fetch, annotations haven't been applied yet.
                continue
            for nodeid, alias in resource._fetched_nodes.items():
                python_val = []
                all_tile_values = getattr(resource, alias)
                if all_tile_values is None:
                    continue
                datatype_instance = datatypes_by_nodeid[nodeid]
                nodegroup = nodegroups_by_nodeid[nodeid]
                if nodegroup.cardinality == "1":
                    all_tile_values = list(all_tile_values)
                for inner_tile_val in all_tile_values:
                    # TODO: add prefetching/lazy for RI-list?
                    python_val.append(datatype_instance.to_python(inner_tile_val))
                if all_tile_values != python_val:
                    if nodegroup.cardinality == "1":
                        setattr(resource, alias, python_val[0])
                    else:
                        setattr(resource, alias, python_val)
