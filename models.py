import logging
import sys
import uuid
from itertools import chain
from types import SimpleNamespace

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models, transaction
from django.utils.translation import gettext as _

from arches import VERSION as arches_version
from arches.app.models.models import (
    GraphModel,
    Node,
    ResourceInstance,
    TileModel,
)
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.utils.permission_backend import (
    get_nodegroups_by_perm,
    user_is_resource_reviewer,
)

from arches_querysets.bulk_operations.tiles import BulkTileOperation
from arches_querysets.datatypes.datatypes import DataTypeFactory
from arches_querysets.lookups import *  # registers lookups
from arches_querysets.querysets import (
    GraphWithPrefetchingQuerySet,
    SemanticResourceQuerySet,
    SemanticTileManager,
    SemanticTileQuerySet,
)
from arches_querysets.utils.models import (
    find_nodegroup_by_alias,
    get_recursive_prefetches,
    get_nodegroups_here_and_below,
    pop_arches_model_kwargs,
)


logger = logging.getLogger(__name__)


class AliasedData(SimpleNamespace):
    pass


class SemanticResource(ResourceInstance):
    objects = SemanticResourceQuerySet.as_manager()

    class Meta:
        proxy = True
        db_table = "resource_instances"
        permissions = (("no_access_to_resourceinstance", "No Access"),)

    def __init__(self, *args, **kwargs):
        arches_model_kwargs, other_kwargs = pop_arches_model_kwargs(
            kwargs, self._meta.get_fields()
        )
        super().__init__(*args, **other_kwargs)
        self.aliased_data = AliasedData(**arches_model_kwargs)
        self._permitted_nodes = Node.objects.none()
        # Data-collecting nodes that were queried
        self._queried_nodes = Node.objects.none()

    def save(self, *, request=None, index=True, **kwargs):
        with transaction.atomic():
            self._save_aliased_data(request=request, index=index, **kwargs)

    @classmethod
    def as_model(
        cls,
        graph_slug=None,
        *,
        resource_ids=None,
        defer=None,
        only=None,
        as_representation=False,
        user=None,
    ):
        """Return a chainable QuerySet for a requested graph's instances,
        with tile data annotated onto node and nodegroup aliases.

        See `arches.app.models.querysets.ResourceInstanceQuerySet.with_nodegroups`.
        """
        return cls.objects.with_nodegroups(
            graph_slug,
            resource_ids=resource_ids,
            defer=defer,
            only=only,
            as_representation=as_representation,
            user=user,
        )

    def fill_blanks(self):
        """Initialize empty node values for each top nodegroup lacking a tile."""
        if not vars(self.aliased_data):
            raise RuntimeError("aliased_data is empty")

        for nodegroup_alias, value in vars(self.aliased_data).items():
            if value in (None, []):
                nodegroup = find_nodegroup_by_alias(
                    nodegroup_alias, self._permitted_nodes
                )
                blank_tile = SemanticTile(
                    resourceinstance=self,
                    nodegroup=nodegroup,
                )
                blank_tile = blank_tile.fill_blank_tile_from_child_nodegroup(nodegroup)
            if value == []:
                value.append(blank_tile)
            elif value is None:
                setattr(self.aliased_data, nodegroup_alias, blank_tile)

            # Recurse.
            if isinstance(value, list):
                for tile in value:
                    tile.fill_blanks()
            else:
                tile = value or blank_tile
                tile.fill_blanks()

    def save_edit(self, user=None, transaction_id=None):
        """Intended to replace proxy model method eventually."""
        if self._state.adding:
            edit_type = "create"
        else:
            return

        # Until save_edit() is a static method, work around it.
        ephemeral_proxy_instance = Resource()
        ephemeral_proxy_instance.graphid = self.graph_id
        ephemeral_proxy_instance.resourceinstanceid = str(self.pk)
        ephemeral_proxy_instance.save_edit(
            user=user, edit_type=edit_type, transaction_id=transaction_id
        )

    def save_without_related_objects(self, **kwargs):
        return super().save(**kwargs)

    def _save_aliased_data(self, *, request=None, index=True, **kwargs):
        """Raises a compound ValidationError with any failing tile values.

        It's not exactly idiomatic for a Django project to clean()
        values during a save(), but we can't easily express this logic
        in a "pure" DRF field validator, because:
            - the node values are phantom fields.
            - we have other entry points besides DRF.
        """
        bulk_operation = BulkTileOperation(
            entry=self, request=request, save_kwargs=kwargs
        )
        bulk_operation.run()

        # Instantiate proxy model for now, but refactor & expose this on vanilla model
        proxy_resource = Resource.objects.get(pk=self.pk)
        proxy_resource.save_descriptors()
        if index:
            proxy_resource.index()

        if request:
            self.save_edit(
                user=request.user, transaction_id=bulk_operation.transaction_id
            )

        self.refresh_from_db(
            using=kwargs.get("using"),
            fields=kwargs.get("update_fields"),
            user=request.user if request else None,
        )

    def refresh_from_db(self, using=None, fields=None, from_queryset=None, user=None):
        if from_queryset is None:
            from_queryset = self.__class__.as_model(
                self.graph.slug,
                only={node.alias for node in self._queried_nodes},
                as_representation=getattr(self, "_as_representation", False),
                user=user,
            )
        # Filter now so we can patch it out below.
        from_queryset = from_queryset.filter(pk=self.pk)
        if arches_version >= (8, 0):
            # Patch out filter(pk=...) so that when refresh_from_db() calls get(),
            # it populates the cache. TODO: ask on forum about happier path.
            from_queryset.filter = lambda pk=None: from_queryset
            super().refresh_from_db(using, fields, from_queryset)
            # Retrieve aliased data from the queryset cache.
            self.aliased_data = from_queryset[0].aliased_data
        else:
            # Django 4: good-enough riff on refresh_from_db(), but not bulletproof.
            db_instance = from_queryset.get()
            for field in db_instance._meta.concrete_fields:
                setattr(self, field.attname, getattr(db_instance, field.attname))
            self.aliased_data = db_instance.aliased_data


class SemanticTile(TileModel):
    objects = SemanticTileManager.from_queryset(SemanticTileQuerySet)()

    class Meta:
        proxy = True
        db_table = "tiles"

    def __init__(self, *args, **kwargs):
        arches_model_kwargs, other_kwargs = pop_arches_model_kwargs(
            kwargs, self._meta.get_fields()
        )
        super().__init__(*args, **other_kwargs)
        self.aliased_data = arches_model_kwargs.pop(
            "aliased_data", None
        ) or AliasedData(**arches_model_kwargs)
        self._permitted_nodes = Node.objects.none()
        # Data-collecting nodes that were queried
        self._queried_nodes = Node.objects.none()

    def find_nodegroup_alias(self):
        # SemanticTileManager provides grouping_node on 7.6
        if self.nodegroup and hasattr(self.nodegroup, "grouping_node"):
            return self.nodegroup.grouping_node.alias
        if not getattr(self, "_nodegroup_alias", None):
            # TODO: need a 7.6 solution for this for fresh tiles (SemanticTile())
            self._nodegroup_alias = Node.objects.get(pk=self.nodegroup_id).alias
        return self._nodegroup_alias

    @classmethod
    def deserialize(cls, tile_dict, parent_tile: TileModel | None):
        """
        DRF doesn't provide nested writable fields by default,
        so we have this little deserializer helper. Must be a better way.
        """
        attrs = {**tile_dict}
        if (tile_id := attrs.pop("tileid", None)) and isinstance(tile_id, str):
            attrs["tileid"] = uuid.UUID(tile_id)
        if (resourceinstance_id := attrs.pop("resourceinstance", None)) and isinstance(
            resourceinstance_id, str
        ):
            attrs["resourceinstance_id"] = uuid.UUID(resourceinstance_id)
        if (nodegroup_id := attrs.pop("nodegroup", None)) and isinstance(
            nodegroup_id, str
        ):
            attrs["nodegroup_id"] = uuid.UUID(nodegroup_id)
        if (parenttile_id := attrs.pop("parenttile", None)) and isinstance(
            parenttile_id, str
        ):
            attrs["parenttile_id"] = uuid.UUID(parenttile_id)

        attrs["parenttile"] = parent_tile

        tile = cls(**attrs)
        for attr in {"resourceinstance", "nodegroup", "parenttile"}:
            if attr in tile_dict:
                try:
                    tile_dict[attr] = getattr(tile, attr)
                except:
                    pass

        if arches_version < (8, 0):
            # Simulate the default supplied by v8.
            tile.data = {}

        return tile

    @classmethod
    def as_nodegroup(
        cls,
        entry_node_alias,
        *,
        graph_slug,
        resource_ids=None,
        defer=None,
        only=None,
        as_representation=False,
        user=None,
    ):
        """See `arches.app.models.querysets.TileQuerySet.with_node_values`."""

        source_graph = GraphWithPrefetching.prepare_for_annotations(
            graph_slug, resource_ids=resource_ids, user=user
        )
        for node in source_graph.permitted_nodes:
            if node.alias == entry_node_alias:
                entry_node = node
                break
        else:
            raise Node.DoesNotExist(f"graph: {graph_slug} node: {entry_node_alias}")

        entry_node_and_nodes_below = []
        for nodegroup in get_nodegroups_here_and_below(entry_node.nodegroup):
            entry_node_and_nodes_below.extend(
                [
                    node
                    for node in nodegroup.node_set.all()
                    if node in source_graph.permitted_nodes
                ]
            )

        qs = cls.objects.filter(nodegroup_id=entry_node.pk)
        if resource_ids:
            qs = qs.filter(resourceinstance_id__in=resource_ids)

        filtered_only = [
            branch_node.alias
            for branch_node in entry_node_and_nodes_below
            if not only or branch_node.alias in only
        ]

        return qs.with_node_values(
            entry_node_and_nodes_below,
            defer=defer,
            only=filtered_only,
            as_representation=as_representation,
            entry_node=entry_node,
        )

    def save(self, *, request=None, index=True, **kwargs):
        if arches_version < (8, 0) and self.nodegroup:
            # Cannot supply this too early, as nodegroup might be included
            # with the request and already instantiated to a fresh object.
            self.nodegroup.grouping_node = self.nodegroup.node_set.get(
                pk=models.F("nodegroup")
            )
        with transaction.atomic():
            if self.sortorder is None or self.is_fully_provisional():
                self.set_next_sort_order()
            self._save_aliased_data(request=request, index=index, **kwargs)

    def fill_blank_tile_from_child_nodegroup(self, child_nodegroup, parent_tile=None):
        grandchildren = (
            child_nodegroup.children.all()
            if arches_version >= (8, 0)
            else child_nodegroup.nodegroup_set.all()
        )

        blank_tile = self.__class__(
            resourceinstance=self.resourceinstance,
            nodegroup=child_nodegroup,
            parenttile=parent_tile,
            **{
                node.alias: self.get_default_value(node)
                for node in child_nodegroup.node_set.all()
                if node.datatype != "semantic"
            },
            **{
                SemanticTile(nodegroup=grandchild_nodegroup).find_nodegroup_alias(): (
                    self.fill_blank_tile_from_child_nodegroup(grandchild_nodegroup)
                    if grandchild_nodegroup.cardinality == "1"
                    else [
                        self.fill_blank_tile_from_child_nodegroup(grandchild_nodegroup)
                    ]
                )
                for grandchild_nodegroup in grandchildren
            },
        )

        # Signify that the tile is not yet saved.
        blank_tile.pk = None
        return blank_tile

    def fill_blanks(self):
        """Initialize empty node values for each nodegroup lacking a tile."""
        if not vars(self.aliased_data):
            return

        def find_nodegroup_from_alias(nodegroup_alias):
            for fetched_node in self._permitted_nodes:
                if (
                    fetched_node.alias == nodegroup_alias
                    and fetched_node.nodegroup.parentnodegroup_id == self.nodegroup_id
                ):
                    return fetched_node.nodegroup
            raise Exception

        for alias, value in vars(self.aliased_data).items():
            try:
                nodegroup = find_nodegroup_from_alias(alias)
            except:
                continue
            if value in (None, []):
                blank_tile = self.fill_blank_tile_from_child_nodegroup(nodegroup, self)
            if value == []:
                value.append(blank_tile)
            elif value is None:
                setattr(self.aliased_data, alias, blank_tile)

            # Recurse.
            if isinstance(value, list):
                for tile in value:
                    tile.fill_blanks()
            else:
                tile = value or blank_tile
                tile.fill_blanks()

    @staticmethod
    def get_default_value(node):
        # TODO: When ingesting this into core, make this a method on the node.
        datatype_factory = DataTypeFactory()
        d_data_type = datatype_factory.datatypes[node.datatype]
        datatype = datatype_factory.get_instance(node.datatype)
        try:
            widget_config = node.cardxnodexwidget_set.all()[0].config
            localized_config = widget_config.serialize()
        except (IndexError, ObjectDoesNotExist, MultipleObjectsReturned):
            default_widget = d_data_type.defaultwidget
            localized_config = default_widget.defaultconfig
        default_value = localized_config.get("defaultValue", None)
        try:
            default_value = datatype.get_interchange_value(default_value)
        except AttributeError:
            # 7.6: this might be missing.
            pass

        if node.datatype == "number":
            # Trying to call float("") breaks the integration with DRF.
            # There should probably be some validation in the datatype
            # methods to ensure that poor types don't end up in defaultValue.
            if default_value == "":
                default_value = None

        return default_value

    def save_without_related_objects(self, **kwargs):
        return super().save(**kwargs)

    def dummy_save(self, **kwargs):
        """Don't save this tile, but run any other side effects."""
        # update_fields=set() will abort the save.
        save_kwargs = {**kwargs, "update_fields": set()}
        return super().save(**save_kwargs)

    def _save_aliased_data(self, *, request=None, index=True, **kwargs):
        bulk_operation = BulkTileOperation(
            entry=self, request=request, save_kwargs=kwargs
        )
        bulk_operation.run()

        proxy_resource = Resource.objects.get(pk=self.resourceinstance_id)
        proxy_resource.save_descriptors()
        if index:
            proxy_resource.index()

        self.refresh_from_db(
            using=kwargs.get("using", None),
            fields=kwargs.get("update_fields", None),
        )

    def _tile_update_is_noop(self, original_data):
        """Skipping no-op tile saves avoids regenerating RxR rows, at least
        given the current implementation that doesn't serialize them."""

        datatype_factory = DataTypeFactory()
        # Not object-oriented because TileModel.nodegroup is a property.
        for node in Node.objects.filter(nodegroup_id=self.nodegroup_id).only(
            "datatype"
        ):
            if node.datatype == "semantic":
                continue
            node_id_str = str(node.nodeid)
            old = original_data.get(node_id_str)
            datatype_instance = datatype_factory.get_instance(node.datatype)
            new = self.data[node_id_str]
            if match_fn := getattr(datatype_instance, "values_match", None):
                if not match_fn(old, new):
                    return False
            if node.datatype in ("resource-instance", "resource-instance-list"):
                if not self._resource_values_match(old, new):
                    return False
            if old != new:
                return False

        return True

    @staticmethod
    def _resource_value_to_python(tile_val):
        if tile_val is None or len(tile_val) != 1:
            return tile_val
        return tile_val[0]

    @staticmethod
    def _resource_values_match(value1, value2):
        if not isinstance(value1, list) or not isinstance(value2, list):
            return value1 == value2
        copy1 = [{**inner_val} for inner_val in value1]
        copy2 = [{**inner_val} for inner_val in value2]
        for inner_val in chain(copy1, copy2):
            inner_val.pop("resourceXresourceId", None)
        return copy1 == copy2

    def _enrich(self, graph_slug, *, only=None):
        resource = SemanticResource.as_model(
            graph_slug, only=only, resource_ids=[self.resourceinstance_id]
        ).get()
        for grouping_node in resource._permitted_nodes:
            if grouping_node.pk != grouping_node.nodegroup_id:
                continue  # not a grouping node
            for node in grouping_node.nodegroup.node_set.all():
                setattr(self.aliased_data, node.alias, self.data.get(str(node.pk)))
        self.resourceinstance = resource

    def _apply_provisional_edit(
        self, proxy, existing_data, existing_provisional_edits, *, user=None
    ):
        # TODO: decompose this out of Tile.save() and call *that*.
        # this section moves the data over from self.data to self.provisionaledits if certain users permissions are in force
        # then self.data is restored from the previously saved tile data

        oldprovisionalvalue = None
        newprovisionalvalue = None
        provisional_edit_log_details = None
        creating_new_tile = self._state.adding
        existing_instance = Tile(data={**existing_data} if existing_data else None)
        existing_instance.provisional_edits = (
            {**existing_provisional_edits} if existing_provisional_edits else None
        )
        existing_instance._state.adding = creating_new_tile
        if user is not None and not user_is_resource_reviewer(user):
            if creating_new_tile:
                # the user has previously edited this tile
                proxy.apply_provisional_edit(
                    user, self.data, action="update", existing_model=existing_instance
                )
                oldprovisional = proxy.get_provisional_edit(existing_instance, user)
                if oldprovisional is not None:
                    oldprovisionalvalue = oldprovisional["value"]
            else:
                proxy.apply_provisional_edit(user, data=self.data, action="create")

            newprovisionalvalue = self.data
            self.provisionaledits = proxy.provisionaledits
            self.data = existing_data
            # Also update proxy, which will be used to run further side effects.
            proxy.provisionaledits = proxy.provisionaledits
            proxy.data = existing_data

            provisional_edit_log_details = {
                "user": user,
                "provisional_editor": user,
                "action": "create tile" if creating_new_tile else "add edit",
            }

        return oldprovisionalvalue, newprovisionalvalue, provisional_edit_log_details


class GraphWithPrefetching(GraphModel):
    objects = GraphWithPrefetchingQuerySet.as_manager()

    class Meta:
        proxy = True
        db_table = "graphs"

    @classmethod
    def prepare_for_annotations(cls, graph_slug=None, *, resource_ids=None, user=None):
        """Return a graph with necessary prefetches for
        SemanticTile._prefetch_related_objects(), which is what builds the shape
        of the tile graph.

        This method also checks nodegroup permissions for read.
        """
        if resource_ids and not graph_slug:
            graph_query = cls.objects.filter(resourceinstance__in=resource_ids)
        elif graph_slug:
            if arches_version >= (8, 0):
                graph_query = cls.objects.filter(
                    slug=graph_slug, source_identifier=None
                )
            else:
                graph_query = cls.objects.filter(slug=graph_slug)
        else:
            raise ValueError("graph_slug or resource_ids must be provided")

        if arches_version >= (8, 0):
            prefetches = [
                "node_set__cardxnodexwidget_set",
                "node_set__nodegroup__parentnodegroup",
                "node_set__nodegroup__node_set",
                "node_set__nodegroup__node_set__cardxnodexwidget_set",
                "node_set__nodegroup__cardmodel_set",
                *get_recursive_prefetches(
                    "node_set__nodegroup__children",
                    depth=12,
                    recursive_part="children",
                ),
                *get_recursive_prefetches(
                    "node_set__nodegroup__children__node_set",
                    depth=12,
                    recursive_part="children",
                ),
                *get_recursive_prefetches(
                    "node_set__nodegroup__children__node_set__cardxnodexwidget_set",
                    depth=12,
                    recursive_part="children",
                ),
                *get_recursive_prefetches(
                    "node_set__nodegroup__children__cardmodel_set",
                    depth=12,
                    recursive_part="children",
                ),
                # TODO: determine if these last two are still used?
                "node_set__nodegroup__grouping_node__nodegroup",
                "node_set__nodegroup__children__grouping_node",
            ]
        else:
            prefetches = [
                "node_set__cardxnodexwidget_set",
                "node_set__nodegroup__parentnodegroup",
                "node_set__nodegroup__node_set",
                "node_set__nodegroup__node_set__cardxnodexwidget_set",
                "node_set__nodegroup__cardmodel_set",
                *get_recursive_prefetches(
                    "node_set__nodegroup__nodegroup_set",
                    depth=12,
                    recursive_part="nodegroup_set",
                ),
                *get_recursive_prefetches(
                    "node_set__nodegroup__nodegroup_set__node_set",
                    depth=12,
                    recursive_part="nodegroup_set",
                ),
                *get_recursive_prefetches(
                    "node_set__nodegroup__nodegroup_set__cardmodel_set",
                    depth=12,
                    recursive_part="nodegroup_set",
                ),
                *get_recursive_prefetches(
                    "node_set__nodegroup__nodegroup_set__node_set__cardxnodexwidget_set",
                    depth=12,
                    recursive_part="nodegroup_set",
                ),
            ]

        if user:
            permitted_nodegroups = get_nodegroups_by_perm(user, "models.read_nodegroup")
            permitted_nodes_prefetch = models.Prefetch(
                "node_set",
                queryset=Node.objects.filter(nodegroup__in=permitted_nodegroups),
                # Intentionally not using to_attr until we can make that
                # play nicely with other prefetches.
            )
            prefetches.insert(0, permitted_nodes_prefetch)

        try:
            graph = graph_query.prefetch_related(*prefetches).get()
        except cls.DoesNotExist as e:
            if sys.version_info >= (3, 11):
                e.add_note(f"No graph found with slug: {graph_slug}")
            raise

        if arches_version < (8, 0):
            graph._annotate_grouping_node()

        return graph

    @property
    def permitted_nodes(self):
        """Permission filtering is accomplished by permitted_nodes_prefetch."""
        return self.node_set.all()

    def _annotate_grouping_node(self):
        grouping_node_map = {}
        for node in self.permitted_nodes:
            if node.nodegroup_id == node.pk:
                grouping_node_map[node.pk] = node
        for node in self.permitted_nodes:
            if nodegroup := node.nodegroup:
                nodegroup.grouping_node = grouping_node_map.get(nodegroup.pk)
                for child_nodegroup in nodegroup.nodegroup_set.all():
                    child_nodegroup.grouping_node = grouping_node_map.get(
                        child_nodegroup.pk
                    )
