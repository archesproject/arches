import uuid
from collections import defaultdict
from slugify import slugify

from django.core.exceptions import FieldError, ValidationError
from django.db import models
from django.db.models.query import ModelIterable
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from arches import VERSION as arches_version
from arches.app.models.models import Node

from arches_querysets.datatypes.datatypes import DataTypeFactory
from arches_querysets.utils.models import (
    generate_node_alias_expressions,
    get_recursive_prefetches,
)

NOT_PROVIDED = object()


class NodeAliasValuesMixin:
    def values(self, *args, **kwargs):
        """Allow using a node_alias as a field name in a values() query."""
        # This is just sugar so that the following works:
        # .values("my_alias")
        # rather than the long form:
        # .values(my_alias=models.F("my_alias"))
        args_copy = list(set(args))
        kwargs_copy = {**kwargs}
        for arg in args:
            field_name = arg.split(models.constants.LOOKUP_SEP)[0]
            if (
                field_name in self.query.annotations
                and field_name not in self.query.annotation_select
                and arg not in kwargs
            ):
                # values() can promote aliases to annotations via **kwargs
                kwargs_copy[arg] = models.F(arg)
                args_copy.remove(arg)
        return super().values(*args_copy, **kwargs_copy)

    def values_list(self, *args, **kwargs):
        """Allow using a node_alias as a field name in a values_list() query."""
        qs = self
        for arg in args:
            field_name = arg.split(models.constants.LOOKUP_SEP)[0]
            if (
                field_name in qs.query.annotations
                and field_name not in qs.query.annotation_select
            ):
                # values_list() cannot promote aliases via kwargs like annotate().
                qs = qs.annotate(**{arg: models.F(arg)})
        return models.QuerySet.values_list(qs, *args, **kwargs)

    def aggregate(self, *args, **kwargs):
        """Handle the "promotion" of .alias() to .annotate() for .aggregate()."""
        try:
            return super().aggregate(*args, **kwargs)
        except FieldError as e:
            # Hopefully Django will support this out of the box, see:
            # https://code.djangoproject.com/ticket/36480#comment:3
            node_alias = e.args[0].split("'")[1]
            with_annotation = self.annotate(**{node_alias: models.F(node_alias)})
            return with_annotation.aggregate(*args, **kwargs)


class TileTreeManager(models.Manager):
    # TODO: evaluate whether some of these should get pushed into get_tiles()
    def get_queryset(self):
        qs = super().get_queryset().select_related("resourceinstance")
        # arches_version==9.0.0
        if arches_version >= (8, 0):
            # TODO: could get this once?
            qs = qs.prefetch_related("resourceinstance__from_resxres__to_resource")
            qs = qs.select_related("nodegroup__grouping_node")
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


class TileTreeQuerySet(NodeAliasValuesMixin, models.QuerySet):
    def get_tiles(
        self,
        graph_slug,
        nodegroup_alias=None,
        *,
        resource_ids=None,
        as_representation=False,
        depth=20,
        nodes=None,
        graph_query=None,
    ):
        """
        Entry point for filtering arches data by nodegroups.

        >>> statements = TileTree.get_tiles("datatype_lookups", "statement")
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
        from arches_querysets.models import GraphWithPrefetching

        if nodegroup_alias:
            qs = self.filter(
                nodegroup__node__alias=nodegroup_alias,
                nodegroup__node__graph__slug=graph_slug,
            )
        else:
            qs = self.filter(nodegroup__node__graph__slug=graph_slug)
        if resource_ids:
            qs = qs.filter(resourceinstance_id__in=resource_ids)

        if not nodes:
            # Violates laziness of QuerySets, but can be made fully lazy
            # by providing a `nodes` argument doing the same query.
            filters = models.Q(graph__slug=graph_slug)
            # arches_version==9.0.0
            if arches_version >= (8, 0):
                filters &= models.Q(source_identifier=None)
            nodes = (
                Node.objects.filter(filters)
                .exclude(datatype="semantic")
                .exclude(nodegroup=None)
                .select_related("nodegroup__parentnodegroup")
            )
            if not nodes:
                raise ValueError(f"No nodes found for graph with slug: {graph_slug}")

        alias_expressions = generate_node_alias_expressions(self.model, nodes)

        # arches_version==9.0.0
        if arches_version < (8, 0):
            msg = "arches-querysets requires all nodes to have an alias."
            assert None not in alias_expressions, msg

        if graph_query is None:
            if "graph_query" in qs._hints:
                graph_query = qs._hints["graph_query"]
            else:
                graph_query = GraphWithPrefetching.objects.prefetch(graph_slug)

        qs._add_hints(
            as_representation=as_representation,
            graph_slug=graph_slug,
            graph_query=graph_query,
        )

        # Future: see various solutions mentioned here for avoiding
        # "magic number" depth traversal (but the magic number is harmless,
        # causes no additional queries beyond actual depth):
        # https://forum.djangoproject.com/t/prefetching-relations-to-arbitrary-depth/39328
        if depth:
            child_tile_query = self.model.objects.get_queryset().get_tiles(
                graph_slug=graph_slug,
                as_representation=as_representation,
                depth=depth - 1,
                nodes=nodes,
                graph_query=graph_query,
            )

            qs = qs.prefetch_related(
                models.Prefetch(
                    # arches_version==9.0.0
                    "children" if arches_version >= (8, 0) else "tilemodel_set",
                    queryset=child_tile_query,
                    # Using to_attr ensures the query results materialize into
                    # TileTree objects rather than TileModel objects. This isn't
                    # usually an issue, but something in the way we're overriding
                    # ORM internals seems to require this.
                    to_attr="_tile_trees",
                )
            )

        # Provide the alias_expressions to the ORM.
        # Use .distinct() because the inner join above ("nodegroup__node__graph__slug")
        # can produce duplicates.
        return qs.alias(**alias_expressions).order_by("sortorder").distinct()

    @cached_property
    def grouping_node_lookup(self):
        graph_nodes = next(iter(self._hints["graph_query"])).node_set.all()
        return {node.pk: node for node in graph_nodes if node.pk == node.nodegroup_id}

    def _fetch_all(self):
        """Hook into QuerySet evaluation to customize the result."""
        if issubclass(self._iterable_class, ModelIterable):
            if "graph_query" in self._hints:
                self._iterable_class = TileTreeIterable
            # else: .get_tiles() was not called: no need to set richer representations.
        # else: values()/values_list() queries: no need to set richer representations.
        super()._fetch_all()

        if issubclass(self._iterable_class, ModelIterable):
            try:
                self._set_aliased_data()
            except (TypeError, ValueError, ValidationError) as e:
                # These errors are caught by DRF, so re-raise as something else.
                raise RuntimeError(e) from e

    def _set_aliased_data(self):
        """
        Call datatype to_python() methods when materializing the QuerySet.
        Memoize fetched nodes.
        Fetch display values in bulk.
        Attach child tiles to parent tiles and vice versa.
        """
        from arches_querysets.models import AliasedData

        aliased_data_to_update = {}
        values_by_datatype = defaultdict(list)
        datatype_contexts = {}
        for tile in self._result_cache:
            if tile.aliased_data is None:
                tile.aliased_data = AliasedData()
            else:
                return  # already set
            tile.sync_private_attributes(self)
            for node in tile.nodegroup.node_set.all():
                if node.datatype == "semantic":
                    continue
                datatype_instance = DataTypeFactory().get_instance(node.datatype)
                tile_data = datatype_instance.get_tile_data(tile)
                node_value = tile_data.get(str(node.pk))
                if node_value is None:
                    # Datatype methods assume tiles always have all keys, but we've
                    # seen problems in the wild.
                    tile_data[str(node.pk)] = None
                aliased_data_to_update[(tile, node)] = node_value
                values_by_datatype[node.datatype].append(node_value)

        # Get datatype context querysets.
        for datatype, values in values_by_datatype.items():
            datatype_instance = DataTypeFactory().get_instance(datatype)
            bulk_values = datatype_instance.get_display_value_context_in_bulk(values)
            datatype_instance.set_display_value_context_in_bulk(bulk_values)
            datatype_contexts[datatype] = bulk_values

        # Set aliased_data property.
        for tile_node_pair, node_value in aliased_data_to_update.items():
            tile, node = tile_node_pair
            tile.set_aliased_data(node, node_value, datatype_contexts)

        for tile in self._result_cache:
            self._set_child_tile_data(tile)

    def _set_child_tile_data(self, tile):
        child_tiles = getattr(tile, "_tile_trees", [])
        for child_tile in sorted(
            child_tiles, key=lambda tile_item: tile_item.sortorder or 0
        ):
            child_nodegroup_alias = child_tile.find_nodegroup_alias(
                self.grouping_node_lookup
            )
            if child_tile.nodegroup.cardinality == "1" and child_nodegroup_alias:
                # TODO(arches_version==9.0.0): remove `and child_nodegroup_alias`
                # which can no longer be null as of v8.
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
            # arches_version==9.0.0
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


class TileTreeIterable(ModelIterable):
    def __iter__(self):
        """
        Ensure every tile and nodegroup in the tree has a reference to the
        prefetched graph via
        - tile -> resourceinstance -> graph
        - tile -> nodegroup -> grouping_node & node_set

        Set .aliased_data to None as a sentinel so that TileTreeQuerySet._set_aliased_data()
        knows to run only once.
        """
        graph = next(iter(self.queryset._hints["graph_query"]))
        nodegroup_map = {
            node.nodegroup_id: node.nodegroup for node in graph.node_set.all()
        }
        for tile_tree in super().__iter__():
            if not tile_tree.sealed:
                tile_tree.resourceinstance.graph = graph
                tile_tree.nodegroup = nodegroup_map[tile_tree.nodegroup_id]
                tile_tree.sealed = True
                tile_tree.aliased_data = None
            yield tile_tree


class ResourceTileTreeQuerySet(NodeAliasValuesMixin, models.QuerySet):
    def get_tiles(
        self,
        graph_slug,
        *,
        resource_ids=None,
        as_representation=False,
        nodes=None,
        depth=20,
    ):
        """Aliases a ResourceTileTreeQuerySet with tile data unpacked
        and mapped onto nodegroup aliases, e.g.:

        >>> concepts = ResourceTileTree.objects.get_tiles("concept")

        With slightly fewer keystrokes:

        >>> concepts = ResourceTileTree.get_tiles("concept")

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

        graph_query = GraphWithPrefetching.objects.prefetch(graph_slug)
        self._add_hints(as_representation=as_representation, graph_query=graph_query)

        if not nodes:
            # Violates laziness of QuerySets, but can be made fully lazy
            # by providing a `nodes` argument doing the same query.
            filters = models.Q(graph__slug=graph_slug)
            # arches_version==9.0.0
            if arches_version >= (8, 0):
                filters &= models.Q(source_identifier=None)
            nodes = (
                Node.objects.filter(filters)
                .exclude(datatype="semantic")
                .exclude(nodegroup=None)
                .select_related("nodegroup__parentnodegroup")
                .order_by()
            )
            if not nodes:
                raise ValueError(f"No nodes found for graph with slug: {graph_slug}")

        alias_expressions = generate_node_alias_expressions(self.model, nodes)

        if resource_ids:
            qs = self.filter(pk__in=resource_ids)
        else:
            filters = models.Q(graph__slug=graph_slug)
            # arches_version==9.0.0
            if arches_version >= (8, 0):
                filters &= models.Q(graph__source_identifier=None)
            qs = self.filter(filters)

        return (
            qs.select_related("graph")
            .prefetch_related(
                models.Prefetch(
                    "tilemodel_set",
                    queryset=TileTree.objects.get_tiles(
                        graph_slug=graph_slug,
                        as_representation=as_representation,
                        nodes=nodes,
                        graph_query=graph_query,
                        depth=depth,
                    ),
                    to_attr="_tile_trees",
                ),
            )
            .alias(**alias_expressions)
        )

    def _fetch_all(self):
        """Hook into QuerySet evaluation to customize the result."""
        if issubclass(self._iterable_class, ModelIterable):
            if "graph_query" in self._hints:
                self._iterable_class = ResourceTileTreeIterable
            # else: .get_tiles() was not called: no need to set richer representations.
        # else: values()/values_list() queries: no need to set richer representations.

        super()._fetch_all()

        if issubclass(self._iterable_class, ModelIterable):
            try:
                self._set_aliased_data()
            except (TypeError, ValueError, ValidationError) as e:
                # These errors are caught by DRF, so re-raise as something else.
                raise RuntimeError(e) from e
        # else: values()/values_list() queries

    def _set_aliased_data(self):
        """
        Attach top-level tiles to resource instances.
        Attach resource instances to all fetched tiles.
        Memoize fetched grouping node aliases (and graph source nodes).
        """
        from arches_querysets.models import AliasedData, GraphWithPrefetching

        if not self._result_cache:
            return
        for resource in self._result_cache:
            if resource.aliased_data is None:
                resource.aliased_data = AliasedData()
            else:
                return  # already processed
        for resource in self._result_cache:
            for tile in getattr(resource, "_tile_trees", []):
                graph = tile.resourceinstance.graph
                break
            else:
                continue
            break
        else:
            graph = GraphWithPrefetching.objects.prefetch(
                graph_slug=self._result_cache[0].graph.slug
            ).get()

        grouping_nodes = {}
        for node in graph.node_set.all():
            if not node.nodegroup:
                continue
            if getattr(node, "source_identifier", None):
                continue
            if node.pk == node.nodegroup_id:
                grouping_nodes[node.pk] = node

        for resource in self._result_cache:
            resource._as_representation = self._hints.get("as_representation", False)

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


class ResourceTileTreeIterable(ModelIterable):
    def __iter__(self):
        """
        Set .aliased_data to None as a sentinel so that
        ResourceTileTreeQuerySet._set_aliased_data() knows to run only once.
        """
        graph = next(iter(self.queryset._hints["graph_query"]))
        for resource_tile_tree in super().__iter__():
            if not resource_tile_tree.sealed:
                resource_tile_tree.graph = graph
                resource_tile_tree.sealed = True
                resource_tile_tree.aliased_data = None
            yield resource_tile_tree


# TODO (arches_version==9.0.0): remove all but prefetch() method dropping 7.6
class GraphWithPrefetchingQuerySet(models.QuerySet):  # pragma: no cover
    """Backport of Arches 8.0 GraphQuerySet, plus one method for custom prefetches."""

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

    def prefetch(self, graph_slug=None, *, resource_ids=None):
        """Return a graph with necessary prefetches for setting aliased_data."""
        qs = self
        if resource_ids and not graph_slug:
            qs = qs.filter(resourceinstance__in=resource_ids)
        elif graph_slug:
            # arches_version==9.0.0
            if arches_version >= (8, 0):
                qs = qs.filter(slug=graph_slug, source_identifier=None)
            else:
                qs = qs.filter(slug=graph_slug)
        else:
            raise ValueError("graph_slug or resource_ids must be provided")

        # arches_version==9.0.0
        if arches_version >= (8, 0):
            children = "children"
        else:
            children = "nodegroup_set"

        prefetches = [
            "node_set__cardxnodexwidget_set",
            "node_set__nodegroup__parentnodegroup",
            "node_set__nodegroup__node_set__cardxnodexwidget_set",
            "node_set__nodegroup__cardmodel_set",
            *get_recursive_prefetches(
                f"node_set__nodegroup__{children}", depth=12, recursive_part=children
            ),
            *get_recursive_prefetches(
                f"node_set__nodegroup__{children}__node_set__cardxnodexwidget_set",
                depth=12,
                recursive_part=children,
            ),
            *get_recursive_prefetches(
                f"node_set__nodegroup__{children}__cardmodel_set",
                depth=12,
                recursive_part=children,
            ),
        ]

        return qs.prefetch_related(*prefetches)[:1]

    def _fetch_all(self):
        """Derive each grouping_node instead of fetching it."""
        super()._fetch_all()
        if not isinstance(self._iterable_class, ModelIterable):
            return
        for graph in self._result_cache or []:  # XXX consider memo'ing this as done.
            for node in graph.node_set.all():
                if node.nodegroup:
                    for sibling_node in node.nodegroup.node_set.all():
                        if sibling_node.pk == node.nodegroup.pk:
                            node.nodegroup.grouping_node = sibling_node
                            break
