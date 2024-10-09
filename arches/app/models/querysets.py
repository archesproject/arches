from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models


class PythonicModelQuerySet(models.QuerySet):
    def with_unpacked_tiles(self, graph_slug, *, defer=None, only=None):
        """Annotates a ResourceInstance QuerySet with tile data unpacked
        and mapped onto node aliases, e.g.:

        >>> ResourceInstance.objects.with_unpacked_tiles("mymodel")

        With slightly fewer keystrokes:

        >>> ResourceInstance.as_model("mymodel")

        Or with defer/only as in the QuerySet interface:

        >>> ResourceInstance.as_model("mymodel", only=["alias1", "alias2"])

        ...although this is a pessimization if you will end up
        manipulating other node data besides "my_node_alias".

        Example:

        >>> MyModel = ResourceInstance.as_model("mymodel")
        >>> result = MyModel.filter(my_node_alias="some tile value")
        >>> result.first().my_node_alias
        "some tile value"
        """
        from arches.app.models.models import GraphModel

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

        node_alias_annotations = {}
        node_aliases_by_node_id = {}
        for node in source_graph.node_set.all():
            if node.datatype == "semantic":
                continue
            if node.nodegroup_id is None:
                continue
            if (defer and node.alias in defer) or (only and node.alias not in only):
                continue
            # TODO: unwrap with datatype-aware transforms
            # TODO: don't worry about name collisions for now, e.g. "name"
            tile_lookup = models.F(f"tilemodel__data__{node.pk}")

            if node.nodegroup.cardinality == "n":
                # TODO: May produce duplicates until we add unique constraint
                # on TileModel.resourceinstance_id, nodegroup_id, sortorder
                tile_lookup = ArrayAgg(
                    tile_lookup,
                    filter=models.Q(tilemodel__nodegroup_id=node.nodegroup.pk),
                    ordering="tilemodel__sortorder",
                )
            node_alias_annotations[node.alias] = tile_lookup
            node_aliases_by_node_id[str(node.pk)] = node.alias

        if not node_alias_annotations:
            raise ValueError("All fields were excluded.")

        return (
            self.filter(graph=source_graph)
            .prefetch_related("tilemodel_set")
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
