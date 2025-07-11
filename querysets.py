import uuid
from operator import attrgetter
from slugify import slugify

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from arches import VERSION as arches_version
from arches.app.models.models import Node

from arches_querysets.datatypes.datatypes import DataTypeFactory
from arches_querysets.utils.models import (
    generate_node_alias_expressions,
    filter_nodes_by_highest_parent,
)

NOT_PROVIDED = object()


class TileTreeManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().select_related("nodegroup")
        if arches_version >= (8, 0):
            qs = qs.select_related("nodegroup__grouping_node")
            qs = qs.prefetch_related(
                "nodegroup__children__node_set",
                "resourceinstance__from_resxres__to_resource",
            )
        else:
            # Annotate nodegroup_alias on Arches 7.6.
            qs = qs.annotate(
                _nodegroup_alias=Node.objects.filter(
                    pk=models.F("nodegroup_id"),
                    nodegroup__tilemodel=models.OuterRef("tileid"),
                ).values("alias")[:1]
            )
            qs = qs.prefetch_related(
                "nodegroup__nodegroup_set__node_set",
                "resourceinstance__resxres_resource_instance_ids_from__resourceinstanceidto",
            )
        return qs


class TileTreeQuerySet(models.QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._as_representation = False
        self._queried_nodes = []
        self._permitted_nodes = []
        self._entry_node = None

    def get_tiles(
        self,
        graph_slug,
        nodegroup_alias=None,
        *,
        permitted_nodes,
        defer=None,
        only=None,
        as_representation=False,
        depth=20,
        entry_node=None,
    ):
        """
        Entry point for filtering arches data by nodegroups (instead of grouping by
        resource.)

        >>> statements = TileTree.get_tiles("concept", "statement")
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
            - True: calls to_json() datatype methods
            - False: calls to_python() datatype methods
        """
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
        queried_nodes, alias_expressions = generate_node_alias_expressions(
            permitted_nodes,
            defer=deferred_node_aliases,
            only=only_node_aliases,
            model=self.model,
        )

        self._permitted_nodes = permitted_nodes  # permitted nodes below entry point
        self._queried_nodes = queried_nodes
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
                    queryset=self.model.objects.get_queryset().get_tiles(
                        graph_slug=graph_slug,
                        permitted_nodes=permitted_nodes,
                        defer=defer,
                        only=only,
                        as_representation=as_representation,
                        depth=depth - 1,
                    ),
                    # Using to_attr ensures the query results materialize into
                    # TileTree objects rather than TileModel objects. This isn't
                    # usually an issue, but something in the way we're overriding
                    # ORM internals seems to require this.
                    to_attr="_tile_trees",
                )
            )

        return qs.alias(**alias_expressions)

    def _prefetch_related_objects(self):
        """Hook into QuerySet evaluation to customize the result."""
        # Overriding _fetch_all() doesn't work here: causes dupe child tiles.
        # Perhaps these manual annotations could be scheduled another way?
        super()._prefetch_related_objects()
        try:
            self._set_aliased_data()
        except (TypeError, ValueError, ValidationError) as e:
            # These errors are caught by DRF, so re-raise as something else.
            raise RuntimeError(e) from e

    def _set_aliased_data(self):
        """Call datatype to_python() methods when materializing the QuerySet.
        Memoize fetched nodes. Attach child tiles to parent tiles and vice versa.
        """
        for tile in self._result_cache:
            if not isinstance(tile, self.model):
                return
            break

        for tile in self._result_cache:
            tile.sync_private_attributes(self)
            for node in self._queried_nodes:
                if node.nodegroup_id == tile.nodegroup_id:
                    datatype_instance = DataTypeFactory().get_instance(node.datatype)
                    tile_data = datatype_instance.get_tile_data(tile)
                    node_val = tile_data.get(str(node.pk))
                    if node_val is None:
                        # Datatype methods assume tiles always have all keys, but we've
                        # seen problems in the wild.
                        tile_data[str(node.pk)] = None
                    tile.set_aliased_data(node, node_val)
                elif node.nodegroup.parentnodegroup_id == tile.nodegroup_id:
                    empty_value = None if node.nodegroup.cardinality == "1" else []
                    setattr(tile.aliased_data, tile.find_nodegroup_alias(), empty_value)

            self._set_child_tile_data(tile)

    def _set_child_tile_data(self, tile):
        child_tiles = getattr(tile, "_tile_trees", [])
        for child_tile in sorted(child_tiles, key=attrgetter("sortorder")):
            child_nodegroup_alias = child_tile.find_nodegroup_alias()
            if child_tile.nodegroup.cardinality == "1":
                setattr(tile.aliased_data, child_nodegroup_alias, child_tile)
            else:
                children = getattr(tile.aliased_data, child_nodegroup_alias, [])
                children.append(child_tile)
                setattr(tile.aliased_data, child_nodegroup_alias, children)
            # Attach parent to this child.
            child_tile.parent = tile
            child_tile.sync_private_attributes(tile)

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


class ResourceTileTreeQuerySet(models.QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._as_representation = False
        self._queried_nodes = []
        self._permitted_nodes = []

    def get_tiles(
        self,
        graph_slug=None,
        *,
        resource_ids=None,
        defer=None,
        only=None,
        as_representation=False,
        user=None,
    ):
        """Annotates a ResourceTileTreeQuerySet with tile data unpacked
        and mapped onto nodegroup aliases, e.g.:

        >>> concepts = ResourceTileTree.objects.get_tiles("concept")

        With slightly fewer keystrokes:

        >>> concepts = ResourceTileTree.get_tiles("concept")

        Or direct certain nodegroups with defer/only as in the QuerySet interface:

        >>> partial_concepts = ResourceTileTree.get_tiles("concept", only=["ng1", "ng2"])

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

        as_representation:
            - True: calls to_json() datatype methods
            - False: calls to_python() datatype methods
        """
        from arches_querysets.models import GraphWithPrefetching, TileTree

        self._as_representation = as_representation

        source_graph = GraphWithPrefetching.prefetch(
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
        queried_nodes, alias_expressions = generate_node_alias_expressions(
            self._permitted_nodes,
            defer=deferred_node_aliases,
            only=only_node_aliases,
            model=self.model,
        )

        self._queried_nodes = queried_nodes

        if resource_ids:
            qs = self.filter(pk__in=resource_ids)
        else:
            qs = self.filter(graph=source_graph)
        return qs.prefetch_related(
            models.Prefetch(
                "tilemodel_set",
                queryset=TileTree.objects.get_tiles(
                    graph_slug=graph_slug,
                    permitted_nodes=self._permitted_nodes,
                    as_representation=as_representation,
                ),
                to_attr="_tile_trees",
            ),
        ).alias(**alias_expressions)

    def _fetch_all(self):
        """Hook into QuerySet evaluation to customize the result."""
        super()._fetch_all()
        try:
            self._set_aliased_data()
        except (TypeError, ValueError, ValidationError) as e:
            # These errors are caught by DRF, so re-raise as something else.
            raise RuntimeError from e

    def _set_aliased_data(self):
        """
        Attach top-level tiles to resource instances.
        Attach resource instances to all fetched tiles.
        Memoize fetched grouping node aliases (and graph source nodes).
        """
        grouping_nodes = {}
        for node in self._permitted_nodes:
            if not node.nodegroup:
                continue
            grouping_node = node.nodegroup.grouping_node
            grouping_nodes[grouping_node.pk] = grouping_node

        for resource in self._result_cache:
            if not isinstance(resource, self.model):
                # For a .values() query, we will lack instances.
                continue
            resource._permitted_nodes = self._permitted_nodes
            resource._queried_nodes = self._queried_nodes
            resource._as_representation = self._as_representation

            # Prepare empty aliased data containers.
            for grouping_node in grouping_nodes.values():
                if grouping_node.nodegroup.parentnodegroup_id:
                    continue
                default = None if grouping_node.nodegroup.cardinality == "1" else []
                setattr(resource.aliased_data, grouping_node.alias, default)

            # Fill aliased data with top nodegroup data.
            for tile in getattr(resource, "_tile_trees", []):
                if tile.nodegroup.parentnodegroup_id:
                    continue
                nodegroup_alias = grouping_nodes[tile.nodegroup_id].alias
                if tile.nodegroup.cardinality == "n":
                    tile_array = getattr(resource.aliased_data, nodegroup_alias)
                    tile_array.append(tile)
                else:
                    setattr(resource.aliased_data, nodegroup_alias, tile)

    def _clone(self):
        """Persist private attributes through the life of the QuerySet."""
        clone = super()._clone()
        clone._queried_nodes = self._queried_nodes
        clone._permitted_nodes = self._permitted_nodes
        clone._as_representation = self._as_representation
        return clone


# TODO (arches_version): remove when dropping 7.6
class GraphWithPrefetchingQuerySet(models.QuerySet):  # pragma: no cover
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
