from django.db import models

from arches.app.models.utils import field_names


class PythonicModelQuerySet(models.QuerySet):
    def with_unpacked_tiles(
        self, graph_slug=None, *, resource_id=None, defer=None, only=None
    ):
        """Annotates a ResourceInstance QuerySet with tile data unpacked
        and mapped onto node aliases, e.g.:

        >>> ResourceInstance.objects.with_unpacked_tiles("mymodel")

        With slightly fewer keystrokes:

        >>> ResourceInstance.as_model("mymodel")

        Or with defer/only as in the QuerySet interface:

        >>> ResourceInstance.as_model("mymodel", only=["alias1", "alias2"])

        Example:

        >>> MyModel = ResourceInstance.as_model("mymodel")
        >>> result = MyModel.filter(my_node_alias="some tile value")
        >>> result.first().my_node_alias
        "some tile value"

        Provisional edits are completely ignored.
        """
        from arches.app.datatypes.datatypes import DataTypeFactory
        from arches.app.models.models import GraphModel, NodeGroup, TileModel

        if defer and only and (overlap := set(defer).intersection(set(only))):
            raise ValueError(f"Got intersecting defer/only args: {overlap}")
        if resource_id and not graph_slug:
            graph_query = GraphModel.objects.filter(resourceinstance=resource_id)
        else:
            graph_query = GraphModel.objects.filter(
                slug=graph_slug, source_identifier=None
            )
        try:
            source_graph = graph_query.prefetch_related("node_set__nodegroup").get()
        except GraphModel.DoesNotExist as e:
            e.add_note(f"No graph found with slug: {graph_slug}")
            raise

        invalid_names = field_names(self.model)
        datatype_factory = DataTypeFactory()
        node_alias_annotations = {}
        node_aliases_by_node_id = {}
        for node in source_graph.node_set.all():
            if node.datatype == "semantic":
                continue
            if node.nodegroup_id is None:
                continue
            if (defer and node.alias in defer) or (only and node.alias not in only):
                continue
            if node.alias in invalid_names:
                raise ValueError(f'"{node.alias}" clashes with a model field name.')

            datatype_instance = datatype_factory.get_instance(node.datatype)
            tile_lookup = datatype_instance.get_orm_lookup(node)
            node_alias_annotations[node.alias] = tile_lookup
            node_aliases_by_node_id[str(node.pk)] = node.alias

        if not node_alias_annotations:
            raise ValueError("All fields were excluded.")
        for given_alias in only or []:
            if given_alias not in node_alias_annotations:
                raise ValueError(f'"{given_alias}" is not a valid node alias.')

        if resource_id:
            qs = self.filter(pk=resource_id)
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
                    to_attr="_sorted_tiles_for_pythonic_model_fields",
                ),
            )
            .annotate(
                **node_alias_annotations,
            )
            .annotate(
                _pythonic_model_fields=models.Value(
                    node_aliases_by_node_id,
                    output_field=models.JSONField(),
                )
            )
        )

    def as_resource(self, resource_id):
        return self.with_unpacked_tiles(resource_id=resource_id).get()

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
            if not hasattr(resource, "_pythonic_model_fields"):
                # On the first fetch, annotations haven't been applied yet.
                continue
            for nodeid, alias in resource._pythonic_model_fields.items():
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
