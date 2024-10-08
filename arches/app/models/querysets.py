from django.db import models


class PythonicModelQuerySet(models.QuerySet):
    def with_unpacked_tiles(self, graph_slug, *, defer=None, only=None):
        """Annotates a ResourceInstance QuerySet with tile data unpacked
        and mapped onto node aliases, e.g.:

        ResourceInstance.objects.with_unpacked_tiles("mymodel")

        With slightly fewer keystrokes:

        ResourceInstance.as_model("mymodel")

        Or with defer/only as in the QuerySet interface:

        ResourceInstance.as_model("mymodel", only="my_node_alias")

        ...although this is a pessimization if you will end up
        manipulating other node data besides "my_node_alias".

        Use it like:
        MyModel = ResourceInstance.as_model("mymodel")
        MyModel.filter(my_node_alias="some tile value")
        """
        from arches.app.models.models import GraphModel

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
        for node in source_graph.node_set.prefetch_related("nodegroup"):
            if defer and node.alias in defer:
                continue
            if only and node.alias not in only:
                continue
            # TODO: unwrap with datatype-aware transforms
            # TODO: don't worry about name collisions for now, e.g. "name"
            # TODO: how to group cardinality N tiles?
            node_alias_annotations[node.alias] = models.F(f"tilemodel__data__{node.pk}")

        return (
            self.filter(graph=source_graph)
            .prefetch_related("tilemodel_set")
            .annotate(
                **node_alias_annotations,
            )
        )
