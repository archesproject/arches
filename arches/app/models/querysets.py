from django.db import models

from arches.app.models.utils import field_names


class PythonicModelQuerySet(models.QuerySet):
    def with_unpacked_tiles(self, graph_slug, *, defer=None, only=None):
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
        from arches.app.models.models import GraphModel, TileModel

        if defer and only and (overlap := set(defer).intersection(set(only))):
            raise ValueError(f"Got intersecting defer/only args: {overlap}")
        try:
            source_graph = (
                GraphModel.objects.filter(
                    slug=graph_slug,
                    # TODO: Verify that source_identifier=None is really what I want?
                    source_identifier=None,
                )
                .prefetch_related("node_set")
                .get()
            )
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

        return (
            self.filter(graph=source_graph)
            .prefetch_related(
                "graph__node_set",
                models.Prefetch(
                    "tilemodel_set",
                    queryset=TileModel.objects.order_by("sortorder"),
                    to_attr="sorted_tiles",
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
