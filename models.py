import logging
import sys
from itertools import chain

from django.db import models, transaction
from django.utils.translation import gettext as _

from arches import __version__ as arches_version
from arches.app.models.models import (
    GraphModel,
    Node,
    ResourceInstance,
    TileModel,
)
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.utils.permission_backend import user_is_resource_reviewer

from arches_querysets.bulk_operations.tiles import BulkTileOperation
from arches_querysets.lookups import *
from arches_querysets.querysets import (
    SemanticResourceQuerySet,
    SemanticTileManager,
    SemanticTileQuerySet,
)
from arches_querysets.utils.models import (
    get_recursive_prefetches,
    get_nodegroups_here_and_below,
    pop_arches_model_kwargs,
)


logger = logging.getLogger(__name__)


class AliasedData:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<AliasedData: {vars(self)}>"


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

    @classmethod
    def as_model(
        cls,
        graph_slug=None,
        *,
        resource_ids=None,
        defer=None,
        only=None,
        as_representation=False,
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
        )

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

    def save(self, index=False, user=None, **kwargs):
        with transaction.atomic():
            if getattr(self, "_annotated_tiles", None):
                self._save_aliased_data(user=user, index=index, **kwargs)
            else:
                super().save(**kwargs)

    def clean(self):
        """Raises a compound ValidationError with any failing tile values."""
        # Might be able to remove graph_nodes if we can just deal with grouping_node.
        bulk_operation = BulkTileOperation(entry=self, resource=self)
        bulk_operation.validate()

    def save_without_related_objects(self, **kwargs):
        return super().save(**kwargs)

    def _save_aliased_data(self, user=None, index=False, **kwargs):
        """Raises a compound ValidationError with any failing tile values.

        It's not exactly idiomatic for a Django project to clean()
        values during a save(), but we can't easily express this logic
        in a "pure" DRF field validator, because:
            - the node values are phantom fields.
            - we have other entry points besides DRF.
        """
        bulk_operation = BulkTileOperation(entry=self, user=user, save_kwargs=kwargs)
        bulk_operation.run()

        self.refresh_from_db(
            using=kwargs.get("using", None),
            fields=kwargs.get("update_fields", None),
        )

        # Instantiate proxy model for now, but refactor & expose this on vanilla model
        proxy_resource = Resource.objects.get(pk=self.pk)
        proxy_resource.save_descriptors()
        if index:
            proxy_resource.index()

        self.save_edit(user=user, transaction_id=bulk_operation.transaction_id)

    def refresh_from_db(self, using=None, fields=None, from_queryset=None):
        if from_queryset is None and (
            queried_nodes := getattr(self, "_queried_nodes", set())
        ):
            aliases = [n.alias for n in queried_nodes if n.nodegroup.pk == n.pk]
            from_queryset = self.__class__.as_model(
                self.graph.slug,
                only=aliases,
                as_representation=getattr(self, "_as_representation", False),
            ).filter(pk=self.pk)
            super().refresh_from_db(using, fields, from_queryset)
            # Copy over annotations and annotated tiles.
            refreshed_resource = from_queryset[0]
            for field in {*aliases, "_annotated_tiles"}.intersection(
                vars(refreshed_resource)
            ):
                setattr(self, field, getattr(refreshed_resource, field))
        else:
            super().refresh_from_db(using, fields, from_queryset)


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

    def find_nodegroup_alias(self):
        # SemanticTileManager provides grouping_node on 7.6
        if self.nodegroup and hasattr(self.nodegroup, "grouping_node"):
            return self.nodegroup.grouping_node.alias
        if not getattr(self, "_nodegroup_alias", None):
            self._nodegroup_alias = Node.objects.get(pk=self.nodegroup_id).alias
        return self._nodegroup_alias

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
        allow_empty=False,
        user=None,
    ):
        """See `arches.app.models.querysets.TileQuerySet.with_node_values`."""

        source_graph = GraphWithPrefetching.prepare_for_annotations(
            graph_slug, resource_ids=resource_ids
        )
        for node in source_graph.node_set.all():
            if node.alias == entry_node_alias:
                entry_node = node
                break
        else:
            raise Node.DoesNotExist(f"graph: {graph_slug} node: {entry_node_alias}")

        entry_node_and_nodes_below = []
        for nodegroup in get_nodegroups_here_and_below(entry_node.nodegroup, user):
            entry_node_and_nodes_below.extend(list(nodegroup.node_set.all()))

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
            allow_empty=allow_empty,
            entry_node=entry_node,
        ).annotate(_nodegroup_alias=models.Value(entry_node_alias))
        # TODO: determine if this annotation still needed / remove

    def save(self, index=False, user=None, **kwargs):
        with transaction.atomic():
            if self.sortorder is None or self.is_fully_provisional():
                self.set_next_sort_order()
            self._save_aliased_data(user=user, index=index, **kwargs)

    def save_without_related_objects(self, **kwargs):
        return super().save(**kwargs)

    def dummy_save(self, **kwargs):
        """Don't save this tile, but run any other side effects."""
        # update_fields=set() will abort the save.
        save_kwargs = {**kwargs, "update_fields": set()}
        return super().save(**save_kwargs)

    def _save_aliased_data(self, *, user=None, index=False, **kwargs):
        bulk_operation = BulkTileOperation(entry=self, user=user, save_kwargs=kwargs)
        bulk_operation.run()

        # TODO: add unique constraint for TileModel re: sortorder
        # TODO: determine whether this should be skippable, and how.
        self.refresh_from_db(
            using=kwargs.get("using", None),
            fields=kwargs.get("update_fields", None),
        )

        # TODO: refactor & expose this on vanilla model, at which point
        # we may want to refresh_from_db() here.
        proxy_resource = Resource.objects.get(pk=self.resourceinstance_id)
        proxy_resource.save_descriptors()
        if index:
            proxy_resource.index()

    def _tile_update_is_noop(self, original_data):
        """Skipping no-op tile saves avoids regenerating RxR rows, at least
        given the current implementation that doesn't serialize them."""
        from arches.app.datatypes.datatypes import DataTypeFactory

        datatype_factory = DataTypeFactory()
        # Not object-oriented because TileModel.nodegroup is a property.
        for node in Node.objects.filter(nodegroup_id=self.nodegroup_id).only(
            "datatype"
        ):
            if node.datatype == "semantic":
                continue
            node_id_str = str(node.nodeid)
            old = original_data[node_id_str]
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
        for grouping_node in resource._fetched_graph_nodes:
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
    class Meta:
        proxy = True
        db_table = "graphs"

    @classmethod
    def prepare_for_annotations(cls, graph_slug=None, *, resource_ids=None):
        """Return a graph with necessary prefetches for _prefetch_related_objects()
        and the rest_framework client."""
        if resource_ids and not graph_slug:
            graph_query = cls.objects.filter(resourceinstance__in=resource_ids)
        elif graph_slug:
            if arches_version >= "8":
                graph_query = GraphModel.objects.filter(
                    slug=graph_slug, source_identifier=None
                )
            else:
                graph_query = cls.objects.filter(slug=graph_slug)
        else:
            raise ValueError("graph_slug or resource_ids must be provided")
        try:
            if arches_version >= "8":
                prefetches = [
                    "node_set__cardxnodexwidget_set",
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
            graph = graph_query.prefetch_related(*prefetches).get()
        except cls.DoesNotExist as e:
            if sys.version_info >= (3, 11):
                e.add_note(f"No graph found with slug: {graph_slug}")
            raise

        if arches_version < "8":
            # 7.6: simulate .grouping_node attribute
            grouping_node_map = {}
            for node in graph.node_set.all():
                if node.nodegroup_id == node.pk:
                    grouping_node_map[node.pk] = node
            for node in graph.node_set.all():
                if nodegroup := node.nodegroup:
                    nodegroup.grouping_node = grouping_node_map.get(nodegroup.pk)
                    for child_nodegroup in nodegroup.nodegroup_set.all():
                        child_nodegroup.grouping_node = grouping_node_map.get(
                            child_nodegroup.pk
                        )

        return graph
