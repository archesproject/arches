from functools import partial

from django.db import models
from django.utils.translation import gettext as _

from arches import __version__ as arches_version
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import Node

from arches_querysets.utils import datatype_transforms
from arches_querysets.utils.models import (
    generate_node_alias_expressions,
    filter_nodes_by_highest_parent,
)


class SemanticTileManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().select_related("nodegroup", "parenttile")
        if arches_version >= "8":
            qs = qs.select_related("nodegroup__grouping_node")
        else:
            # Annotate nodegroup_alias on Arches 7.6.
            qs = qs.annotate(
                _nodegroup_alias=Node.objects.filter(
                    pk=models.F("nodegroup_id"),
                    nodegroup__tilemodel=models.OuterRef("tileid"),
                ).values("alias")[:1]
            )
        return qs


class SemanticTileQuerySet(models.QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self._as_representation = False
        self._queried_nodes = []
        self._fetched_graph_nodes = []
        self._entry_node = None

    def with_node_values(
        self,
        nodes,
        *,
        defer=None,
        only=None,
        as_representation=False,
        allow_empty=False,
        depth=20,
        entry_node=None,
    ):
        """
        Entry point for filtering arches data by nodegroups (instead of grouping by
        resource.)

        >>> statements = SemanticTile.as_nodegroup("statement", graph_slug="concept")
        # TODO: show this with some test node that's actually a localized string.
        >>> results = statements.filter(statement_content__any_lang_startswith="F")
        >>> for result in results:
                print(result.resourceinstance)
                print("\t", result.statement_content["en"]["value"])  # TODO: unwrap?

        <Concept: x-ray fluorescence (aec56d59-9292-42d6-b18e-1dd260ff446f)>
            Fluorescence stimulated by x-rays; ...
        <Concept: vellum (parchment) (34b081cd-6fcc-4e00-9a43-0a8a73745b45)>
            Fine-quality calf or lamb parchment ...

        as_representation:
            - True: calls to_representation() / to_json() datatype methods
            - False: calls to_python() datatype methods

        allow_empty = True includes tiles with no data, e.g. in some creation
        workflows involving creating a blank tile before fetching the richer
        version from this factory.
        """
        self._as_representation = as_representation

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
        node_alias_annotations = generate_node_alias_expressions(
            nodes,
            defer=deferred_node_aliases,
            only=only_node_aliases,
            model=self.model,
        )

        self._fetched_graph_nodes = nodes  # (partial) graph below entry point
        self._queried_nodes = [n for n in nodes if n.alias in node_alias_annotations]
        self._entry_node = entry_node

        qs = self
        qs = qs.filter(nodegroup_id__in={n.nodegroup_id for n in nodes})
        if not allow_empty:
            qs = qs.filter(data__has_any_keys=[n.pk for n in self._queried_nodes])

        # Future: see various solutions mentioned here for avoiding
        # "magic number" depth traversal (but the magic number is harmless,
        # causes no additional queries beyond actual depth):
        # https://forum.djangoproject.com/t/prefetching-relations-to-arbitrary-depth/39328
        if depth:
            qs = qs.prefetch_related(
                models.Prefetch(
                    "children" if arches_version >= "8" else "tilemodel_set",
                    queryset=self.model.objects.get_queryset().with_node_values(
                        nodes=nodes,
                        defer=defer,
                        only=only,
                        as_representation=as_representation,
                        allow_empty=allow_empty,
                        depth=depth - 1,
                    ),
                )
            )

        # TODO: some of these can just be aliases.
        return qs.annotate(**node_alias_annotations).order_by("sortorder")

    def _prefetch_related_objects(self):
        """Call datatype to_python() methods when materializing the QuerySet.
        Discard annotations that do not pertain to this nodegroup.
        Memoize fetched nodes.
        Attach child tiles to parent tiles and vice versa.
        """
        from arches_querysets.models import SemanticResource

        super()._prefetch_related_objects()

        NOT_PROVIDED = object()
        enriched_resource = None

        for tile in self._result_cache:
            if not isinstance(tile, self.model):
                # For a .values() query, we will lack instances.
                continue
            if not enriched_resource:
                # One prefetch per tile depth. Later look into improving.
                # TODO: move -- this only makes sense for tiles for a single resource.
                enriched_resource = (
                    SemanticResource.objects.filter(pk=tile.resourceinstance_id)
                    .with_related_resource_display_names()
                    .get()
                )
            tile._enriched_resource = enriched_resource
            tile._queried_nodes = self._queried_nodes
            tile._fetched_graph_nodes = self._fetched_graph_nodes
            for node in self._queried_nodes:
                if node.nodegroup_id == tile.nodegroup_id:
                    # This is on the tile itself (ORM annotation).
                    tile_val = getattr(tile, node.alias, NOT_PROVIDED)
                    if tile_val is not NOT_PROVIDED:
                        instance_val = self._get_node_value_for_python_annotation(
                            tile, node, tile_val
                        )
                        setattr(tile.aliased_data, node.alias, instance_val)
            if arches_version >= "8":
                fallback = getattr(tile, "children")
            else:
                fallback = getattr(tile, "tilemodel_set")
            for child_tile in getattr(tile, "_annotated_tiles", fallback.all()):
                setattr(
                    child_tile.aliased_data,
                    tile.find_nodegroup_alias(),
                    child_tile.parenttile,
                )
                try:
                    child_nodegroup_alias = child_tile.find_nodegroup_alias()
                except:
                    child_nodegroup_alias = Node.objects.get(
                        pk=child_tile.nodegroup_id
                    ).alias
                children = getattr(tile.aliased_data, child_nodegroup_alias, [])
                children.append(child_tile)
                if child_tile.nodegroup.cardinality == "1":
                    setattr(tile.aliased_data, child_nodegroup_alias, children[0])
                else:
                    setattr(tile.aliased_data, child_nodegroup_alias, children)
                # Attach parent to this child.
                setattr(child_tile.aliased_data, tile.find_nodegroup_alias(), tile)

    def _clone(self):
        clone = super()._clone()
        clone._queried_nodes = self._queried_nodes
        clone._fetched_graph_nodes = self._fetched_graph_nodes
        clone._entry_node = self._entry_node
        clone._as_representation = self._as_representation
        return clone

    def _get_node_value_for_python_annotation(self, tile, node, tile_val):
        datatype_instance = DataTypeFactory().get_instance(node.datatype)

        if self._as_representation:
            snake_case_datatype = node.datatype.replace("-", "_")
            if repr_fn := getattr(
                datatype_transforms,
                f"{snake_case_datatype}_to_representation",
                None,
            ):
                instance_val = repr_fn(datatype_instance, tile_val)
            elif repr_fn := getattr(datatype_instance, "to_representation", None):
                instance_val = repr_fn(tile_val)
            elif tile_val and node.datatype in {
                # Some datatypes have to_json() methods that fit our purpose.
                "resource-instance",
                "resource-instance-list",
                "concept",
                "concept-list",
            }:
                if to_json_fn := getattr(
                    datatype_transforms,
                    f"{snake_case_datatype}_to_json",
                    None,
                ):
                    to_json_fn = partial(to_json_fn, datatype_instance)
                else:
                    to_json_fn = datatype_instance.to_json
                try:
                    to_json_result = to_json_fn(tile, node)
                except TypeError:  # StringDataType workaround.
                    tile.data[str(node.pk)] = {}
                    to_json_result = to_json_fn(tile, node)
                instance_val = to_json_result
            else:
                instance_val = tile_val
        else:
            if py_fn := getattr(datatype_instance, "to_python", None):
                instance_val = py_fn(tile_val)
            elif node.datatype == "resource-instance":
                # TODO: move, once dust settles.
                if tile_val is None or len(tile_val) != 1:
                    instance_val = tile_val
                instance_val = tile_val[0]
            else:
                instance_val = tile_val

        return instance_val


class SemanticResourceQuerySet(models.QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self._as_representation = False
        self._queried_nodes = []
        self._fetched_graph_nodes = []

    def with_nodegroups(
        self,
        graph_slug=None,
        *,
        resource_ids=None,
        defer=None,
        only=None,
        as_representation=False,
    ):
        """Annotates a SemanticResourceQuerySet with tile data unpacked
        and mapped onto nodegroup aliases, e.g.:

        >>> concepts = SemanticResource.objects.with_nodegroups("concept")

        With slightly fewer keystrokes:

        >>> concepts = SemanticResource.as_model("concept")

        Or direct certain nodegroups with defer/only as in the QuerySet interface:

        >>> partial_concepts = SemanticResource.as_model("concept", only=["ng1", "ng2"])

        Django QuerySet methods are available for efficient queries:
        >>> concepts.count()
        785

        Filter on any nested node at the top level ("shallow query").
        In this example, statement_content is a cardinality-N node, thus an array.

        >>> subset = concepts.filter(statement_content__len__gt=0)[:4]
        >>> for concept in subset:
                print(concept)
                for stmt in concept.aliased_data.statement:
                    print("\t", stmt)
                    print("\t\t", stmt.aliased_data.statement_content)

        <Concept: consignment (method of acquisition) (f3fed7aa-eae6-41f6-aa0f-b889d84c0552)>
            <TileModel: statement (46efcd06-a5e5-43be-8847-d7cd94cbc9cb)>
                'Individual objects or works. Most works ...
        ...

        Access child and parent tiles by nodegroup aliases:

        # TODO: replace this example.
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
        to_representation() / to_json() depending on the datatype.
        """
        from arches_querysets.models import GraphWithPrefetching, SemanticTile

        self._as_representation = as_representation

        source_graph = GraphWithPrefetching.prepare_for_annotations(
            graph_slug, resource_ids=resource_ids
        )
        self._fetched_graph_nodes = source_graph.node_set.all()
        deferred_node_aliases = {
            n.alias
            for n in filter_nodes_by_highest_parent(
                self._fetched_graph_nodes, defer or []
            )
        }
        only_node_aliases = {
            n.alias
            for n in filter_nodes_by_highest_parent(
                self._fetched_graph_nodes, only or []
            )
        }
        node_sql_aliases = generate_node_alias_expressions(
            self._fetched_graph_nodes,
            defer=deferred_node_aliases,
            only=only_node_aliases,
            model=self.model,
        )
        self._queried_nodes = [
            node
            for node in self._fetched_graph_nodes
            if node.alias in node_sql_aliases
            and not getattr(node, "source_identifier_id", None)
        ]

        if resource_ids:
            qs = self.filter(pk__in=resource_ids)
        else:
            qs = self.filter(graph=source_graph)
        return qs.prefetch_related(
            models.Prefetch(
                "tilemodel_set",
                queryset=SemanticTile.objects.with_node_values(
                    self._queried_nodes,
                    as_representation=as_representation,
                ),
                to_attr="_annotated_tiles",
            ),
        ).annotate(**node_sql_aliases)

    def with_related_resource_display_names(self):
        # Future: consider exposing nodegroups param.
        return self.prefetch_related(
            "resxres_resource_instance_ids_from__resourceinstanceidto"
        )

    def _prefetch_related_objects(self):
        """
        Attach top-level tiles to resource instances.
        Attach resource instances to all fetched tiles.
        Memoize fetched grouping node aliases (and graph source nodes).
        """
        super()._prefetch_related_objects()

        grouping_nodes = {}
        for node in self._queried_nodes:
            grouping_node = node.nodegroup.grouping_node
            grouping_nodes[grouping_node.pk] = grouping_node

        for resource in self._result_cache:
            if not isinstance(resource, self.model):
                # For a .values() query, we will lack instances.
                continue
            resource._fetched_graph_nodes = self._fetched_graph_nodes
            resource._queried_nodes = self._queried_nodes

            # Prepare resource annotations.
            # TODO: this might move to a method on AliasedData.
            for grouping_node in grouping_nodes.values():
                default = None if grouping_node.nodegroup.cardinality == "1" else []
                setattr(resource.aliased_data, grouping_node.alias, default)

            # Fill aliased data with top nodegroup data.
            annotated_tiles = getattr(resource, "_annotated_tiles", [])
            for annotated_tile in annotated_tiles:
                annotated_tile._enriched_resource = resource
                if annotated_tile.nodegroup.parentnodegroup_id:
                    continue
                ng_alias = grouping_nodes[annotated_tile.nodegroup_id].alias
                if annotated_tile.nodegroup.cardinality == "n":
                    tile_array = getattr(resource.aliased_data, ng_alias)
                    tile_array.append(annotated_tile)
                else:
                    setattr(resource.aliased_data, ng_alias, annotated_tile)

    def _clone(self):
        clone = super()._clone()
        clone._queried_nodes = self._queried_nodes
        clone._fetched_graph_nodes = self._fetched_graph_nodes
        clone._as_representation = self._as_representation
        return clone
