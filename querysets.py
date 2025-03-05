from functools import partial

from django.db import models
from django.utils.translation import gettext as _

from arches import __version__ as arches_version
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import Node, NodeGroup, TileModel

from arches_querysets.utils import datatype_transforms
from arches_querysets.utils.models import (
    generate_tile_annotations,
    filter_nodes_by_highest_parent,
)


class TileQuerySet(models.QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self._as_representation = False
        self._fetched_nodes = []

    def with_node_values(
        self,
        nodes,
        *,
        root_node=None,
        defer=None,
        only=None,
        depth=1,
        as_representation=False,
        allow_empty=False,
    ):
        """
        Entry point for filtering arches data by nodegroups (instead of grouping by
        resource.)

        >>> statements = TileModel.as_nodegroup("statement", graph_slug="concept")
        >>> results = statements.filter(statement_content__any_lang_startswith="F")
        >>> for result in results:
                print(result.resourceinstance)
                print("\t", result.statement_content["en"]["value"])  # TODO: unwrap?

        <Concept: x-ray fluorescence (aec56d59-9292-42d6-b18e-1dd260ff446f)>
            Fluorescence stimulated by x-rays; ...
        <Concept: vellum (parchment) (34b081cd-6fcc-4e00-9a43-0a8a73745b45)>
            Fine-quality calf or lamb parchment ...

        as_representation = True skips calling to_python() datatype methods and calls
        to_representation() instead (rather than to_json() just to ensure we are
        getting optimum performance and not yoking this feature to older use cases.)

        allow_empty = True includes tiles with no data, e.g. in some creation
        workflows involving creating a blank tile before fetching the richer
        version from this factory.
        """
        from arches_querysets.models import SemanticTile

        self._as_representation = as_representation

        # TODO: 7.6 compat
        deferred_node_aliases = {
            n.alias
            for n in nodes
            if getattr(n.nodegroup, "nodegroup_alias", None) in (defer or [])
        }
        only_node_aliases = {
            n.alias
            for n in nodes
            if getattr(n.nodegroup, "nodegroup_alias", None) in (only or [])
        }
        node_alias_annotations = generate_tile_annotations(
            nodes,
            defer=deferred_node_aliases,
            only=only_node_aliases,
            model=self.model,
        )

        max_depth = 5
        prefetches = []
        if root_node:
            child_attr = (
                root_node.nodegroup.children
                if arches_version >= "8"
                else root_node.nodegroup.nodegroup_set.annotate(
                    grouping_node_alias=Node.objects.filter(
                        pk=models.OuterRef("nodegroupid")
                    ).values("alias")
                )
            )
            child_nodegroup_aliases = {
                (
                    child.grouping_node.alias
                    if arches_version >= "8"
                    else child.grouping_node_alias
                )
                for child in child_attr.all()
            }
        else:
            child_nodegroup_aliases = None
        if depth < max_depth:
            tile_field = next(
                field
                for field in SemanticTile._meta.fields
                if field.name == "parenttile"
            )
            prefetches.append(
                models.Prefetch(
                    "__".join(
                        ["children" if tile_field._related_name else "tilemodel_set"]
                        * depth
                    ),
                    queryset=SemanticTile.objects.with_node_values(
                        nodes,
                        root_node=root_node,
                        defer=defer,
                        only=child_nodegroup_aliases,
                        depth=depth + 1,
                        allow_empty=allow_empty,
                    ),
                )
            )

        self._fetched_nodes = [n for n in nodes if n.alias in node_alias_annotations]

        qs = self
        qs = qs.filter(nodegroup_id__in={n.nodegroup_id for n in nodes})
        if not allow_empty:
            qs = qs.filter(data__has_any_keys=[n.pk for n in self._fetched_nodes])

        return (
            qs.prefetch_related(*prefetches)
            .annotate(**node_alias_annotations)
            .annotate(
                cardinality=NodeGroup.objects.filter(
                    pk=models.OuterRef("nodegroup_id")
                ).values("cardinality")
            )
            .order_by("sortorder")
        )

    def _prefetch_related_objects(self):
        """Call datatype to_python() methods when materializing the QuerySet.
        Discard annotations that do not pertain to this nodegroup.
        Memoize fetched nodes.
        """
        super()._prefetch_related_objects()

        datatype_factory = DataTypeFactory()
        NOT_PROVIDED = object()
        for tile in self._result_cache:
            if not isinstance(tile, self.model):
                # For a .values() query, we will lack instances.
                continue
            tile._fetched_nodes = self._fetched_nodes
            for node in self._fetched_nodes:
                if node.nodegroup_id == tile.nodegroup_id:
                    tile_val = getattr(tile, node.alias, NOT_PROVIDED)
                    if tile_val is not NOT_PROVIDED:
                        # TOOD: move, once dust settles.
                        datatype_instance = datatype_factory.get_instance(node.datatype)
                        dummy_tile = TileModel(
                            data={str(node.pk): tile_val},
                            provisionaledits=tile.provisionaledits,
                        )
                        if to_json_fn := getattr(
                            datatype_transforms, f"{node.datatype}_to_json", None
                        ):
                            to_json_fn = partial(to_json_fn, datatype_instance)
                        else:
                            to_json_fn = datatype_instance.to_json
                        try:
                            to_json_fn(dummy_tile, node)
                        except TypeError:  # StringDataType workaround.
                            dummy_tile.data[str(node.pk)] = {}
                            to_json_fn(dummy_tile, node)
                        if self._as_representation:
                            if repr_fn := getattr(
                                datatype_instance, "to_representation", None
                            ):
                                instance_val = repr_fn(tile_val)
                            else:
                                instance_val = tile_val
                        else:
                            if py_fn := getattr(datatype_instance, "to_python", None):
                                instance_val = py_fn(tile_val)
                            elif node.datatype == "resource-instance":
                                # TODO: move, once dust settles.
                                if tile_val is None or len(tile_val) != 1:
                                    return tile_val
                                return tile_val[0]
                            else:
                                instance_val = tile_val
                        setattr(tile, node.alias, instance_val)
                else:
                    delattr(tile, node.alias)
            if arches_version >= "8":
                child_tiles = getattr(tile, "children")
            else:
                child_tiles = getattr(tile, "tilemodel_set")
            for child_tile in child_tiles.all():
                setattr(child_tile, tile.nodegroup_alias, child_tile.parenttile)
                if arches_version >= "8":
                    child_nodegroup_alias = child_tile.nodegroup_alias
                else:
                    child_nodegroup_alias = (
                        child_tile.nodegroup.node_set.filter(pk=child_tile.nodegroup.pk)
                        .get()
                        .alias
                    )
                children = getattr(tile, child_nodegroup_alias, [])
                children.append(child_tile)
                if not (cardinality := getattr(child_tile, "cardinality", None)):
                    cardinality = child_tile.nodegroup.cardinality
                if cardinality == "1":
                    setattr(tile, child_nodegroup_alias, children[0])
                else:
                    setattr(tile, child_nodegroup_alias, children)

    def _clone(self):
        clone = super()._clone()
        clone._fetched_nodes = self._fetched_nodes
        clone._as_representation = self._as_representation
        return clone


class ResourceInstanceQuerySet(models.QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self._as_representation = False
        self._fetched_nodes = []
        self._fetched_graph = None

    def with_nodegroups(
        self,
        graph_slug=None,
        *,
        resource_ids=None,
        defer=None,
        only=None,
        as_representation=False,
    ):
        """Annotates a ResourceInstance QuerySet with tile data unpacked
        and mapped onto nodegroup aliases, e.g.:

        >>> concepts = ResourceInstance.objects.with_nodegroups("concept")

        With slightly fewer keystrokes:

        >>> concepts = ResourceInstance.as_model("concept")

        Or direct certain nodegroups with defer/only as in the QuerySet interface:

        >>> partial_concepts = ResourceInstance.as_model("concept", only=["ng1", "ng2"])

        Example:

        >>> from arches.app.models.models import *
        >>> concepts = ResourceInstance.as_model("concept")

        Django QuerySet methods are available for efficient queries:
        >>> concepts.count()
        785

        Filter on any nested node at the top level ("shallow query").
        In this example, statement_content is a cardinality-N node, thus an array.
        # TODO: should name with `_set`? But then would need to check for clashes.

        >>> subset = concepts.filter(statement_content__len__gt=0)[:4]
        >>> for concept in subset:
                print(concept)
                for stmt in concept.statement:
                    print("\t", stmt)
                    print("\t\t", stmt.statement_content)

        <Concept: consignment (method of acquisition) (f3fed7aa-eae6-41f6-aa0f-b889d84c0552)>
            <TileModel: statement (46efcd06-a5e5-43be-8847-d7cd94cbc9cb)>
                [{'en': {'value': 'Method of acquiring property ...
        ...

        Access child and parent tiles by nodegroup aliases:

        >>> has_child = concepts.filter(statement_data_assignment_statement_content__len__gt=0).first()
        >>> has_child
        <Concept: <appellative_status_ascribed_name_content> (751614c0-de7a-47d7-8e87-a4d18c7337ff)>
        >>> has_child.statement_data_assignment_statement
        <statement_data_assignment_statement (51e1f473-712e-447b-858e-cc7353a084a6)>
        >>> parent = has_child.statement[0]
        >>> parent.statement_data_assignment_statement[0].statement is parent
        True

        Provisional edits are completely ignored for the purposes of querying.

        as_representation = True skips calling to_python() datatype methods and calls
        to_representation() instead (rather than to_json() just to ensure we are
        getting optimum performance and not yoking this feature to older use cases.)
        """
        from arches_querysets.models import GraphWithPrefetching, SemanticTile

        self._as_representation = as_representation

        source_graph = GraphWithPrefetching.prepare_for_annotations(
            graph_slug, resource_ids=resource_ids
        )
        graph_nodes = source_graph.node_set.all()
        deferred_node_aliases = {
            n.alias for n in filter_nodes_by_highest_parent(graph_nodes, defer or [])
        }
        only_node_aliases = {
            n.alias for n in filter_nodes_by_highest_parent(graph_nodes, only or [])
        }
        node_alias_annotations = generate_tile_annotations(
            graph_nodes,
            defer=deferred_node_aliases,
            only=only_node_aliases,
            model=self.model,
        )
        self._fetched_nodes = [
            node
            for node in graph_nodes
            if node.alias in node_alias_annotations
            and not getattr(node, "source_identifier_id", None)
        ]
        self._fetched_graph = source_graph

        if resource_ids:
            qs = self.filter(pk__in=resource_ids)
        else:
            qs = self.filter(graph=source_graph)
        return qs.prefetch_related(
            models.Prefetch(
                "tilemodel_set",
                queryset=SemanticTile.objects.with_node_values(
                    self._fetched_nodes,
                    as_representation=as_representation,
                ).select_related("parenttile"),
                to_attr="_annotated_tiles",
            ),
        ).annotate(**node_alias_annotations)

    def _prefetch_related_objects(self):
        """
        Attach annotated tiles to resource instances in a nested structure.
        Discard annotations only used for shallow filtering.
        Memoize fetched root node aliases (and graph source nodes).
        """
        super()._prefetch_related_objects()

        root_nodes = set()
        for node in self._fetched_nodes:
            root_node = node.nodegroup.grouping_node
            root_nodes.add(root_node)

        for resource in self._result_cache:
            if not isinstance(resource, self.model):
                # For a .values() query, we will lack instances.
                continue
            # TODO: fix misnomer, since it's not just root nodes.
            resource._fetched_root_nodes = set()
            resource._fetched_graph = self._fetched_graph
            for node in self._fetched_nodes:
                delattr(resource, node.alias)
            for root_node in root_nodes:
                setattr(
                    resource,
                    root_node.alias,
                    None if root_node.nodegroup.cardinality == "1" else [],
                )
                resource._fetched_root_nodes.add(root_node)
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

                # Attach parent to this child.
                if annotated_tile.parenttile_id:
                    # TODO: improve performance: just getting the bones in.
                    parent_nodegroup = annotated_tile.parenttile.nodegroup
                    if arches_version >= "8":
                        nodegroup_alias = parent_nodegroup.grouping_node.alias
                    else:
                        nodegroup_alias = (
                            parent_nodegroup.node_set.filter(pk=parent_nodegroup.pk)
                            .get()
                            .alias
                        )
                    setattr(annotated_tile, nodegroup_alias, annotated_tile.parenttile)

            # Final pruning.
            for node in root_nodes:
                if node.nodegroup.parentnodegroup_id:
                    delattr(resource, node.alias)

    def _clone(self):
        clone = super()._clone()
        clone._fetched_nodes = self._fetched_nodes
        clone._fetched_graph = self._fetched_graph
        clone._as_representation = self._as_representation
        return clone
