import uuid
from functools import partial
from slugify import slugify

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from arches import VERSION as arches_version
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import Node, ResourceXResource

from arches_querysets.utils import datatype_transforms
from arches_querysets.utils.models import (
    generate_node_alias_expressions,
    filter_nodes_by_highest_parent,
)


class SemanticTileManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().select_related("nodegroup", "parenttile")
        if arches_version >= (8, 0):
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._as_representation = False
        self._queried_nodes = []
        self._permitted_nodes = []
        self._entry_node = None

    def with_node_values(
        self,
        permitted_nodes,
        *,
        defer=None,
        only=None,
        as_representation=False,
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
        """
        from arches_querysets.models import SemanticResource

        self._as_representation = as_representation

        deferred_node_aliases = {
            n.alias
            for n in permitted_nodes
            if getattr(n.nodegroup, "nodegroup_alias", None) in (defer or [])
        }
        only_node_aliases = {
            n.alias
            for n in permitted_nodes
            if getattr(n.nodegroup, "nodegroup_alias", None) in (only or [])
        }
        node_alias_annotations = generate_node_alias_expressions(
            permitted_nodes,
            defer=deferred_node_aliases,
            only=only_node_aliases,
            model=self.model,
        )

        self._permitted_nodes = permitted_nodes  # permitted nodes below entry point
        self._queried_nodes = [
            n for n in permitted_nodes if n.alias in node_alias_annotations
        ]
        self._entry_node = entry_node

        qs = self.filter(nodegroup_id__in={n.nodegroup_id for n in self._queried_nodes})

        # Future: see various solutions mentioned here for avoiding
        # "magic number" depth traversal (but the magic number is harmless,
        # causes no additional queries beyond actual depth):
        # https://forum.djangoproject.com/t/prefetching-relations-to-arbitrary-depth/39328
        if depth:
            qs = qs.prefetch_related(
                models.Prefetch(
                    "children" if arches_version >= (8, 0) else "tilemodel_set",
                    queryset=self.model.objects.get_queryset().with_node_values(
                        permitted_nodes=permitted_nodes,
                        defer=defer,
                        only=only,
                        as_representation=as_representation,
                        depth=depth - 1,
                    ),
                )
            )

        # TODO: some of these can just be aliases.
        qs = qs.annotate(**node_alias_annotations).order_by("sortorder")

        qs = qs.prefetch_related(
            models.Prefetch(
                "resourceinstance",
                SemanticResource.objects.with_related_resource_display_names(
                    nodes=self._queried_nodes
                ),
            ),
        )
        return qs

    def _prefetch_related_objects(self):
        """Call datatype to_python() methods when materializing the QuerySet.
        Discard annotations that do not pertain to this nodegroup.
        Memoize fetched nodes.
        Attach child tiles to parent tiles and vice versa.
        """

        # Overriding _fetch_all() doesn't work here: causes dupe child tiles.
        # Perhaps these manual annotations could be scheduled another way?
        super()._prefetch_related_objects()
        try:
            self._perform_custom_annotations()
        except (TypeError, ValueError, ValidationError) as e:
            # These errors are caught by DRF, so re-raise as something else.
            raise RuntimeError(e) from e

    def _perform_custom_annotations(self):
        NOT_PROVIDED = object()

        for tile in self._result_cache:
            if not isinstance(tile, self.model):
                return
            break

        for tile in self._result_cache:
            tile._queried_nodes = self._queried_nodes
            tile._permitted_nodes = self._permitted_nodes
            for node in self._queried_nodes:
                if node.nodegroup_id == tile.nodegroup_id:
                    # This is on the tile itself (ORM annotation).
                    tile_val = getattr(tile, node.alias, NOT_PROVIDED)
                    if tile_val is not NOT_PROVIDED:
                        instance_val = self._get_node_value_for_python_annotation(
                            tile, node, tile_val
                        )
                        setattr(tile.aliased_data, node.alias, instance_val)
                elif node.nodegroup.parentnodegroup_id == tile.nodegroup_id:
                    empty_value = None if node.nodegroup.cardinality == "1" else []
                    setattr(tile.aliased_data, tile.find_nodegroup_alias(), empty_value)
                delattr(tile, node.alias)
            if arches_version >= (8, 0):
                fallback = getattr(tile, "children")
            else:
                fallback = getattr(tile, "tilemodel_set")
            child_tiles = getattr(tile, "_annotated_tiles", fallback.all())
            for child_tile in child_tiles:
                setattr(
                    child_tile.aliased_data,
                    tile.find_nodegroup_alias(),
                    child_tile.parenttile,
                )
                child_nodegroup_alias = child_tile.find_nodegroup_alias()
                if child_tile.nodegroup.cardinality == "1":
                    setattr(tile.aliased_data, child_nodegroup_alias, child_tile)
                else:
                    children = getattr(tile.aliased_data, child_nodegroup_alias, [])
                    children.append(child_tile)
                    setattr(tile.aliased_data, child_nodegroup_alias, children)
                # Attach parent to this child.
                setattr(child_tile.aliased_data, tile.find_nodegroup_alias(), tile)

            child_nodegroups = (
                getattr(tile.nodegroup, "children")
                if arches_version >= (8, 0)
                else getattr(tile.nodegroup, "nodegroup_set")
            )
            for child_nodegroup in child_nodegroups.all():
                for node in child_nodegroup.node_set.all():
                    if node.pk == child_nodegroup.pk:
                        grouping_node = node
                        break

                if (
                    getattr(tile.aliased_data, grouping_node.alias, NOT_PROVIDED)
                    is NOT_PROVIDED
                ):
                    setattr(
                        tile.aliased_data,
                        grouping_node.alias,
                        None if child_nodegroup.cardinality == "1" else [],
                    )

    def _clone(self):
        """Persist private attributes through the life of the QuerySet."""
        clone = super()._clone()
        clone._queried_nodes = self._queried_nodes
        clone._permitted_nodes = self._permitted_nodes
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
                else:
                    instance_val = tile_val[0]
            else:
                instance_val = tile_val

        return instance_val


class SemanticResourceQuerySet(models.QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._as_representation = False
        self._queried_nodes = []
        self._permitted_nodes = []

    def with_nodegroups(
        self,
        graph_slug=None,
        *,
        resource_ids=None,
        defer=None,
        only=None,
        as_representation=False,
        user=None,
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
            graph_slug, resource_ids=resource_ids, user=user
        )
        self._permitted_nodes = source_graph.permitted_nodes
        deferred_node_aliases = {
            n.alias
            for n in filter_nodes_by_highest_parent(self._permitted_nodes, defer or [])
        }
        only_node_aliases = {
            n.alias
            for n in filter_nodes_by_highest_parent(self._permitted_nodes, only or [])
        }
        node_sql_aliases = generate_node_alias_expressions(
            self._permitted_nodes,
            defer=deferred_node_aliases,
            only=only_node_aliases,
            model=self.model,
        )
        self._queried_nodes = [
            node
            for node in self._permitted_nodes
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
                    self._permitted_nodes,
                    as_representation=as_representation,
                ),
                to_attr="_annotated_tiles",
            ),
        ).annotate(**node_sql_aliases)

    def with_related_resource_display_names(self, nodes=None):
        if arches_version >= (8, 0):
            return self.prefetch_related(
                models.Prefetch(
                    "from_resxres",
                    queryset=ResourceXResource.objects.filter(
                        node__in=nodes
                    ).prefetch_related("to_resource"),
                    to_attr="filtered_from_resxres",
                ),
            )
        else:
            return self.prefetch_related(
                models.Prefetch(
                    "resxres_resource_instance_ids_from",
                    queryset=ResourceXResource.objects.filter(
                        nodeid__in=nodes
                    ).prefetch_related("resourceinstanceidto"),
                    to_attr="filtered_from_resxres",
                ),
            )

    def _fetch_all(self):
        """
        Attach top-level tiles to resource instances.
        Attach resource instances to all fetched tiles.
        Memoize fetched grouping node aliases (and graph source nodes).
        """
        super()._fetch_all()
        try:
            self._perform_custom_annotations()
        except (TypeError, ValueError, ValidationError) as e:
            # These errors are caught by DRF, so re-raise as something else.
            raise RuntimeError from e

    def _perform_custom_annotations(self):
        grouping_nodes = {}
        for node in self._permitted_nodes:
            grouping_node = node.nodegroup.grouping_node
            grouping_nodes[grouping_node.pk] = grouping_node

        for resource in self._result_cache:
            if not isinstance(resource, self.model):
                # For a .values() query, we will lack instances.
                continue
            resource._permitted_nodes = self._permitted_nodes
            resource._queried_nodes = self._queried_nodes

            # Prepare resource annotations.
            # TODO: this might move to a method on AliasedData.
            for grouping_node in grouping_nodes.values():
                if grouping_node.nodegroup.parentnodegroup_id:
                    continue
                default = None if grouping_node.nodegroup.cardinality == "1" else []
                setattr(resource.aliased_data, grouping_node.alias, default)

            # Fill aliased data with top nodegroup data.
            annotated_tiles = getattr(resource, "_annotated_tiles", [])
            for annotated_tile in annotated_tiles:
                if annotated_tile.nodegroup.parentnodegroup_id:
                    continue
                ng_alias = grouping_nodes[annotated_tile.nodegroup_id].alias
                if annotated_tile.nodegroup.cardinality == "n":
                    tile_array = getattr(resource.aliased_data, ng_alias)
                    tile_array.append(annotated_tile)
                else:
                    setattr(resource.aliased_data, ng_alias, annotated_tile)

    def _clone(self):
        """Persist private attributes through the life of the QuerySet."""
        clone = super()._clone()
        clone._queried_nodes = self._queried_nodes
        clone._permitted_nodes = self._permitted_nodes
        clone._as_representation = self._as_representation
        return clone


class GraphWithPrefetchingQuerySet(models.QuerySet):
    """Backport of Arches 8.0 GraphQuerySet."""

    def make_name_unique(self, name, names_to_check, suffix_delimiter="_"):
        """
        Makes a name unique among a list of names

        Arguments:
        name -- the name to check and modfiy to make unique in the list of "names_to_check"
        names_to_check -- a list of names that "name" should be unique among
        """

        i = 1
        temp_node_name = name
        while temp_node_name in names_to_check:
            temp_node_name = "{0}{1}{2}".format(name, suffix_delimiter, i)
            i += 1
        return temp_node_name

    def create(self, *args, **kwargs):
        raise NotImplementedError(
            "Use create_graph() to create new Graph instances with proper business logic."
        )

    def generate_slug(self, name, is_resource):
        if name:
            slug = slugify(name, separator="_")
        else:
            if is_resource:
                slug = "new_resource_model"
            else:
                slug = "new_branch"
        existing_slugs = self.values_list("slug", flat=True)
        slug = self.make_name_unique(slug, existing_slugs, "_")

        return slug

    def create_graph(self, name="", *, slug=None, user=None, is_resource=False):
        from arches.app.models import models as arches_models
        from arches.app.models.graph import Graph as OldGraphWithPrefetchingModel

        """
        Create a new Graph and related objects, encapsulating all creation side effects.
        """
        new_id = uuid.uuid4()
        nodegroup = None

        if not slug:
            slug = self.generate_slug(name, is_resource)

        graph_model = arches_models.GraphModel(
            name=name,
            subtitle="",
            author=(
                " ".join(filter(None, [user.first_name, user.last_name]))
                if user
                else ""
            ),
            description="",
            version="",
            isresource=is_resource,
            iconclass="",
            ontology=None,
            slug=slug,
        )
        graph_model.save()  # to access side-effects declared in save method

        if not is_resource:
            nodegroup = arches_models.NodeGroup.objects.create(pk=new_id)
            arches_models.CardModel.objects.create(
                nodegroup=nodegroup, name=name, graph=graph_model
            )

        # root node
        arches_models.Node.objects.create(
            pk=new_id,
            name=name,
            description="",
            istopnode=True,
            ontologyclass=None,
            datatype="semantic",
            nodegroup=nodegroup,
            graph=graph_model,
        )

        graph = OldGraphWithPrefetchingModel.objects.get(pk=graph_model.graphid)

        graph.publish(
            user=user,
            notes=_("Graph created."),
        )
        if arches_version >= (8, 0):
            graph.create_draft_graph()

        # ensures entity returned matches database entity
        return self.get(pk=graph_model.graphid)
