import logging
import sys
from collections import defaultdict
from itertools import chain

from django.core.exceptions import ValidationError
from django.db import ProgrammingError, models, transaction
from django.http import HttpRequest
from django.utils.translation import gettext as _

from arches import __version__ as arches_version
from arches.app.models.models import (
    GraphModel,
    Language,
    Node,
    ResourceInstance,
    TileModel,
)
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile, TileValidationError
from arches.app.models.utils import field_names
from arches.app.utils.permission_backend import user_is_resource_reviewer

from arches_querysets.bulk_operations.tiles import BulkTileOperation
from arches_querysets.lookups import *
from arches_querysets.querysets import (
    SemanticResourceQuerySet,
    SemanticTileManager,
    SemanticTileQuerySet,
)
from arches_querysets.utils.models import (
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

    def save_edit(self, user=None):
        """Intended to replace proxy model method eventually."""
        if self._state.adding:
            edit_type = "create"
        else:
            edit_type = "update"

        # Until save_edit() is a static method, work around it.
        ephemeral_proxy_instance = Resource()
        ephemeral_proxy_instance.graphid = self.graph_id
        ephemeral_proxy_instance.resourceinstanceid = str(self.pk)
        ephemeral_proxy_instance.save_edit(user=user, edit_type=edit_type)

    def save(self, index=False, user=None, **kwargs):
        with transaction.atomic():
            # update_fields=set() will abort the save, but at least calling
            # into save() will run a sanity check on unsaved relations.
            super().save(update_fields=set())
            self._save_aliased_data(user=user, index=index, **kwargs)
            # TODO: document that this is not compatible with signals.
            self.save_edit(user=user)

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
        bulk_operation = BulkTileOperation(
            entry=self,
            resource=self,
            user=user,
            save_kwargs=kwargs,
        )
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
        root_node_alias,  # TODO: remove
        *,
        graph_slug,
        resource_ids=None,
        defer=None,
        only=None,
        as_representation=False,
        allow_empty=False,
    ):
        """See `arches.app.models.querysets.TileQuerySet.with_node_values`."""

        root_node = cls._root_node(graph_slug, root_node_alias)
        branch_nodes = []
        for nodegroup in get_nodegroups_here_and_below(root_node.nodegroup):
            branch_nodes.extend(list(nodegroup.node_set.all()))

        qs = cls.objects.filter(nodegroup_id=root_node.pk)
        if resource_ids:
            qs = qs.filter(resourceinstance_id__in=resource_ids)

        return qs.with_node_values(
            branch_nodes,
            defer=defer,
            only=[branch_node.alias for branch_node in branch_nodes],
            as_representation=as_representation,
            allow_empty=allow_empty,
        ).annotate(_nodegroup_alias=models.Value(root_node_alias))

    @staticmethod
    def _root_node(graph_slug, root_node_alias):
        qs = Node.objects.filter(graph__slug=graph_slug, alias=root_node_alias)
        if arches_version >= "8":
            qs = (
                qs.filter(source_identifier=None)
                .select_related("nodegroup__grouping_node__nodegroup")
                .prefetch_related(
                    "nodegroup__node_set",
                    "nodegroup__children",
                    "nodegroup__children__grouping_node",
                    "nodegroup__children__node_set",
                    "nodegroup__children__children",
                    "nodegroup__children__children__grouping_node",
                    "nodegroup__children__children__node_set",
                )
            )
        else:
            qs = qs.select_related("nodegroup").prefetch_related(
                "nodegroup__node_set",
                "nodegroup__nodegroup_set",
                "nodegroup__nodegroup_set__node_set",
                "nodegroup__nodegroup_set__nodegroup_set",
                "nodegroup__nodegroup_set__nodegroup_set__node_set",
            )

        ret = qs.first()
        if ret is None:
            raise Node.DoesNotExist(f"graph: {graph_slug} node: {root_node_alias}")
        return ret

    def save(self, index=False, user=None, **kwargs):
        nodegroup_alias = self.find_nodegroup_alias()
        try:
            with transaction.atomic():
                # update_fields=set() will abort the save, but at least calling
                # into save() will run a sanity check on unsaved relations.
                super().save(update_fields=set())
                if self.sortorder is None or self.is_fully_provisional():
                    self.set_next_sort_order()
                self._save_aliased_data(user=user, index=index, **kwargs)
                # TODO: document that this is not compatible with signals.
        except ProgrammingError as e:
            if e.args and "excess_tiles" in e.args[0]:
                msg = _("Tile Cardinality Error")
                raise ValidationError({nodegroup_alias: msg}) from e
            raise

    def _save_aliased_data(self, *, user=None, index=False, **kwargs):
        tile_data_changed = self._update_tile_from_pythonic_model_values()
        if not tile_data_changed:
            # TODO: double-check whether some user guard makes sense here.
            # And whether indexing or functions need to run.
            return super().save(**kwargs)

        # Instantiate a proxy model and sync data to it, to run all side effects.
        # Explanation: this is basically Tile.save() but with the serialized
        # graph and tile fetching skipped. Hence why we might
        # TODO: expose on vanilla model.
        proxy = Tile.objects.get(pk=self.pk)
        proxy.parenttile = self.parenttile
        proxy.sortorder = self.sortorder
        # TODO: handle create.
        # Capture these to avoid re-querying in _apply_provisional_edit().
        existing_data = proxy.data
        existing_provisional_edits = proxy.provisionaledits
        for field in vars(self):
            setattr(proxy, field, getattr(self, field))

        # Some functions expect to always drill into request.user
        # https://github.com/archesproject/arches/issues/8471
        dummy_request = HttpRequest()
        dummy_request.user = user
        with transaction.atomic():
            try:
                proxy._Tile__preSave(request=dummy_request)
                proxy.check_for_missing_nodes()
                proxy.check_for_constraint_violation()
            except TileValidationError as tve:
                raise ValidationError(tve.message) from tve
            oldprovisionalvalue, newprovisionalvalue, provisional_edit_log_details = (
                self._apply_provisional_edit(
                    proxy, existing_data, existing_provisional_edits, user=user
                )
            )

            super().save(**kwargs)
            # TODO: address performance.
            for node in self.nodegroup.node_set.all():
                datatype = proxy.datatype_factory.get_instance(node.datatype)
                datatype.post_tile_save(self, str(node.pk), request=dummy_request)
            proxy._Tile__postSave(request=dummy_request)

            if self._state.adding:
                proxy.save_edit(
                    user=user,
                    edit_type="tile create",
                    old_value={},
                    new_value=self.data,
                    newprovisionalvalue=newprovisionalvalue,
                    provisional_edit_log_details=provisional_edit_log_details,
                    transaction_id=None,
                    # TODO: get this information upstream somewhere.
                    new_resource_created=False,
                    note=None,
                )
            else:
                proxy.save_edit(
                    user=user,
                    edit_type="tile edit",
                    old_value=existing_data,
                    new_value=self.data,
                    newprovisionalvalue=newprovisionalvalue,
                    oldprovisionalvalue=oldprovisionalvalue,
                    provisional_edit_log_details=provisional_edit_log_details,
                    transaction_id=None,
                )

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

    def _update_tile_from_pythonic_model_values(self):
        if not self.data:
            self.data = Tile.get_blank_tile_from_nodegroup_id(self.nodegroup_id).data
        original_data = {**self.data}

        filtered_attrs = {
            k: v
            for k, v in vars(self).items()
            if k not in field_names(self) and not k.startswith("_")
        }
        self._incoming_tile = SemanticTile(
            aliased_data=filtered_attrs.get("aliased_data")
        )

        errors_by_alias = defaultdict(list)
        if not self.nodegroup:
            raise ValueError
        # TODO: Move. This shouldn't emit resource edit log entries.
        SemanticResource._validate_and_patch_from_tile_values(
            self,
            nodes=self.nodegroup.node_set.all(),
            languages=Language.objects.all(),
            errors_by_node_alias=errors_by_alias,
        )
        if not any(self.data.values()):
            raise ValidationError(_("Tile is blank."))
        if self._tile_update_is_noop(original_data):
            return False
        if errors_by_alias:
            raise ValidationError(
                {
                    alias: ValidationError([e["message"] for e in errors])
                    for alias, errors in errors_by_alias.items()
                }
            )
        return True

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
            # Prefetch sibling nodes for use in _prefetch_related_objects()
            # and generate_node_alias_expressions().

            if arches_version >= "8":
                prefetches = [
                    "node_set__nodegroup__children",
                    "node_set__nodegroup__children__node_set",
                    "node_set__nodegroup__children__children",
                    "node_set__nodegroup__children__children__node_set",
                    "node_set__nodegroup__children__children__children",
                    "node_set__nodegroup__children__children__children__node_set",
                    "node_set__nodegroup__children__children__children__children",
                    "node_set__nodegroup__children__children__children__children__node_set",
                    "node_set__nodegroup__node_set",
                    # TODO: seal grouping_node.nodegroup
                    "node_set__nodegroup__grouping_node__nodegroup",
                    "node_set__nodegroup__children__grouping_node",
                    "node_set__cardxnodexwidget_set",
                ]
            else:
                prefetches = [
                    "node_set__nodegroup__nodegroup_set",
                    "node_set__nodegroup__nodegroup_set__node_set",
                    "node_set__nodegroup__nodegroup_set__nodegroup_set",
                    "node_set__nodegroup__nodegroup_set__nodegroup_set__node_set",
                    "node_set__nodegroup__nodegroup_set__nodegroup_set__nodegroup_set",
                    "node_set__nodegroup__nodegroup_set__nodegroup_set__nodegroup_set__node_set",
                    "node_set__nodegroup__nodegroup_set__nodegroup_set__nodegroup_set__nodegroup_set",
                    "node_set__nodegroup__nodegroup_set__nodegroup_set__nodegroup_set__nodegroup_set__node_set",
                    "node_set__nodegroup__node_set",
                    "node_set__cardxnodexwidget_set",
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
