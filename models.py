import logging
import uuid
from types import SimpleNamespace
from typing import Mapping

from django.core.exceptions import (
    MultipleObjectsReturned,
    ObjectDoesNotExist,
    ValidationError,
)
from django.db import models
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
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.permission_backend import user_is_resource_reviewer

from arches_querysets.bulk_operations.tiles import TileTreeOperation
from arches_querysets.datatypes.datatypes import DataTypeFactory
from arches_querysets.lookups import *  # registers lookups
from arches_querysets.querysets import (
    GraphWithPrefetchingQuerySet,
    ResourceTileTreeQuerySet,
    TileTreeManager,
    TileTreeQuerySet,
)
from arches_querysets.utils.models import (
    append_tiles_recursively,
    ensure_request,
    pop_arches_model_kwargs,
)


logger = logging.getLogger(__name__)


class AliasedData(SimpleNamespace):
    """Provides dot access into node values and nested nodegroups by alias.

    >>> ResourceTileTree.get_tiles('new_resource_model_1').get(...).aliased_data
    AliasedData(string_node={'en': {'value': 'abcde', 'direction': 'ltr'}},
                child_node=<TileTree: child_node (c3637412-9b13-4f05-8f4a-5a80560b8b6e)>)
    """

    def serialize(self, **kwargs):
        serializer = JSONSerializer()
        serializer.force_recalculation = kwargs.get("force_recalculation", False)
        return {
            key: serializer.handle_object(val, **kwargs)
            for key, val in vars(self).items()
        }


class AliasedDataMixin:
    """Don't implement properties: https://github.com/archesproject/arches/issues/12310"""

    def _refresh_aliased_data(self, using, fields, from_queryset):
        try:
            del self._tile_trees
        except AttributeError:
            pass

        # Commandeer the responsibility for filtering on pk from Django
        # so we can retrieve aliased data from the queryset cache.
        from_queryset = from_queryset.filter(pk=self.pk)
        # arches_version==9.0.0
        if arches_version >= (8, 0):
            # Patch out filter(pk=...) so that when refresh_from_db() calls get(),
            # it populates the cache. TODO: ask on forum about happier path.
            from_queryset.filter = lambda pk=None: from_queryset
            models.Model.refresh_from_db(self, using, fields, from_queryset)
            # Retrieve aliased data from the queryset cache.
            self.aliased_data = from_queryset[0].aliased_data
            self._tile_trees = from_queryset[0]._tile_trees
        else:
            # Django 4: good-enough riff on refresh_from_db(), but not bulletproof.
            db_instance = from_queryset.get()
            for field in db_instance._meta.concrete_fields:
                setattr(self, field.attname, getattr(db_instance, field.attname))
            self.aliased_data = db_instance.aliased_data
            if isinstance(self, TileModel) and self.parenttile_id:
                self.parenttile = TileModel.objects.get(pk=self.parenttile_id)
            self._tile_trees = from_queryset[0]._tile_trees


class ResourceTileTree(ResourceInstance, AliasedDataMixin):
    objects = ResourceTileTreeQuerySet.as_manager()

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
        self._as_representation = False
        self._sealed = False

    @property
    def aliased_data(self):
        return self._aliased_data

    @aliased_data.setter
    def aliased_data(self, value):
        self._aliased_data = value

    @property
    def sealed(self):
        """
        A boolean set when this instance is yielded from a QuerySet signifying its
        related .graph has been replaced with an instance w/ related objects prefetched.
        """
        return self._sealed

    @sealed.setter
    def sealed(self, value):
        self._sealed = value

    def save(
        self, *, request=None, index=True, partial=True, force_admin=False, **kwargs
    ):
        """
        partial=True (HTTP PATCH): absent nodes ignored, absent child tiles ignored.
        partial=False (HTTP PUT): absent nodes reset to default, absent child tiles deleted.
        """
        # arches_version==9.0.0
        if (
            arches_version >= (8, 0)
            and self.graph_publication_id
            and (self.graph_publication_id != self.graph.publication_id)
        ):
            raise ValidationError(_("Graph Has Different Publication"))

        self._save_aliased_data(
            request=request,
            index=index,
            partial=partial,
            force_admin=force_admin,
            **kwargs,
        )

    @classmethod
    def get_tiles(
        cls,
        graph_slug,
        *,
        resource_ids=None,
        as_representation=False,
        nodes=None,
    ):
        """Return a chainable QuerySet for a requested graph's instances,
        with tile data keyed by node and nodegroup aliases.

        See `arches_querysets.querysets.ResourceTileTreeQuerySet.get_tiles`.
        """
        return cls.objects.get_tiles(
            graph_slug,
            resource_ids=resource_ids,
            as_representation=as_representation,
            nodes=nodes,
        )

    def append_tile(self, nodegroup_alias):
        grouping_node_aliases = {
            node.alias
            for node in self.graph.node_set.all()
            if node.pk == node.nodegroup_id
        }
        if nodegroup_alias not in grouping_node_aliases:
            raise ValueError(nodegroup_alias)

        TileTree.create_blank_tile(
            nodegroup_alias=nodegroup_alias,
            container=self,
            graph_nodes=self.graph.node_set.all(),
        )

    def fill_blanks(self):
        """Initialize a blank tile with empty values for each nodegroup lacking a tile."""
        append_tiles_recursively(self)

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

    def refresh_from_db(self, using=None, fields=None, from_queryset=None):
        if from_queryset is None:
            # TODO: symptom that we need a backreference to the queryset args.
            from_queryset = self.__class__.get_tiles(
                self.graph.slug,
                as_representation=getattr(self, "_as_representation", False),
            )
        self._refresh_aliased_data(using, fields, from_queryset)

    def _save_aliased_data(
        self, *, request=None, index=True, partial=True, force_admin=False, **kwargs
    ):
        """Raises a compound ValidationError with any failing tile values."""
        request = ensure_request(request, force_admin)
        operation = TileTreeOperation(
            entry=self, request=request, partial=partial, save_kwargs=kwargs
        )
        # This will also call ResourceInstance.save()
        operation.validate_and_save_tiles()

        # Run side effects trapped on Resource.save()
        proxy_resource = (
            Resource.objects.filter(pk=self.pk)
            .select_related("graph__publication")
            .get()
        )
        proxy_resource.save_descriptors()
        if index:
            proxy_resource.index()

        if request:
            self.save_edit(user=request.user, transaction_id=operation.transaction_id)

        self.refresh_from_db(
            using=kwargs.get("using"), fields=kwargs.get("update_fields")
        )


class TileTree(TileModel, AliasedDataMixin):
    objects = TileTreeManager.from_queryset(TileTreeQuerySet)()

    class Meta:
        proxy = True
        db_table = "tiles"

    def __init__(self, *args, **kwargs):
        self._as_representation = kwargs.pop("__as_representation", False)
        self._request = kwargs.pop("__request", None)
        arches_model_kwargs, other_kwargs = pop_arches_model_kwargs(
            kwargs, self._meta.get_fields()
        )
        super().__init__(*args, **other_kwargs)
        self.aliased_data = arches_model_kwargs.pop(
            "aliased_data", None
        ) or AliasedData(**arches_model_kwargs)
        self._parent = None
        self._sealed = False

    @property
    def aliased_data(self):
        return self._aliased_data

    @aliased_data.setter
    def aliased_data(self, value):
        self._aliased_data = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def sealed(self):
        """
        A boolean set when this instance is yielded from a QuerySet signifying its
        related .nodegroup and .resourceinstance.graph have been replaced with
        instances w/ related objects prefetched.
        """
        return self._sealed

    @sealed.setter
    def sealed(self, value):
        self._sealed = value

    def save(
        self, *, request=None, index=True, partial=True, force_admin=False, **kwargs
    ):
        """
        partial=True (HTTP PATCH): absent nodes ignored, absent child tiles ignored.
        partial=False (HTTP PUT): absent nodes reset to default, absent child tiles deleted.
        """
        # arches_version==9.0.0
        if (
            arches_version >= (8, 0)
            and self.resourceinstance_id
            and self.resourceinstance.graph_publication_id
            and (
                self.resourceinstance.graph_publication_id
                != self.resourceinstance.graph.publication_id
            )
        ):
            raise ValidationError(_("Graph Has Different Publication"))

        request = request or self._request
        # Mimic some computations trapped on TileModel.save().
        # arches_version==9.0.0
        if (
            arches_version >= (8, 0)
            and self.sortorder is None
            or self.is_fully_provisional()
        ):
            self.set_next_sort_order()
        self._save_aliased_data(
            request=request,
            index=index,
            partial=partial,
            force_admin=force_admin,
            **kwargs,
        )

    @classmethod
    def get_tiles(
        cls,
        graph_slug,
        nodegroup_alias,
        *,
        resource_ids=None,
        as_representation=False,
        nodes=None,
        depth=20,
    ):
        """See `arches_querysets.querysets.TileTreeQuerySet.get_tiles`."""
        return cls.objects.get_tiles(
            graph_slug=graph_slug,
            nodegroup_alias=nodegroup_alias,
            resource_ids=resource_ids,
            as_representation=as_representation,
            nodes=nodes,
            depth=depth,
        )

    def serialize(self, **kwargs):
        """Prevent serialization of the vanilla .data field, as well as properties
        (serializing .parent would cause cycles)."""
        options = {**kwargs}
        ignored_props = {"data", "parent", "sealed"}
        options["exclude"] = ignored_props | set(options.pop("exclude", {}))
        return JSONSerializer().handle_model(self, **options)

    def clean_fields(self, exclude=None):
        if (
            self.nodegroup
            and self.nodegroup.parentnodegroup_id
            and "parenttile" not in exclude
        ):
            if (
                not self.parenttile_id
                or self.nodegroup.parentnodegroup_id != self.parenttile.nodegroup_id
            ):
                msg = _("Wrong parent tile for parent nodegroup.")
                raise ValidationError({self.find_nodegroup_alias(): msg})
        # Exclude parenttile to ensure batch creations of parent & child do not fail.
        new_exclude = [*(exclude or []), "parenttile"]
        super().clean_fields(exclude=new_exclude)

    def find_nodegroup_alias(self, grouping_node_lookup=None):
        # arches_version==9.0.0
        if arches_version >= (8, 0):
            if grouping_node_lookup:
                self.nodegroup.grouping_node = grouping_node_lookup[self.nodegroup_id]
            return super().find_nodegroup_alias()
        if not getattr(self, "_nodegroup_alias", None):
            # TileTreeManager provides "_nodegroup_alias" annotation on 7.6, but perform
            # a last-minute check just in case. Also runs if the node alias is null.
            for node in self.nodegroup.node_set.all():
                if node.pk == self.nodegroup.pk:
                    self._nodegroup_alias = node.alias
        return self._nodegroup_alias

    @classmethod
    def deserialize(cls, tile_dict, parent_tile: TileModel | None):
        """
        If you're not using the Django REST Framework optional dependency,
        e.g. if you evaluate a queryset with as_representation=True and resave
        the instance, you'll need a way to deserialize dicts into TileTrees.
        """
        if not isinstance(tile_dict, Mapping):
            raise TypeError(
                f'Expected a mapping, got: "{tile_dict}". '
                "Did you mistakenly provide node data directly under a nodegroup alias?"
            )
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

        # arches_version==9.0.0
        if arches_version < (8, 0):
            # Simulate the default supplied by v8.
            tile.data = {}

        return tile

    def sync_private_attributes(self, source):
        if isinstance(source, models.QuerySet):
            self._as_representation = source._hints.get("as_representation", False)
        else:
            self._as_representation = source._as_representation

    def append_tile(self, nodegroup_alias):
        grouping_node_aliases = {
            node.alias
            for node in self.resourceinstance.graph.node_set.all()
            if node.pk == node.nodegroup_id
        }
        if nodegroup_alias not in grouping_node_aliases:
            raise ValueError(nodegroup_alias)
        TileTree.create_blank_tile(
            nodegroup_alias=nodegroup_alias,
            container=self,
            graph_nodes=(
                self.resourceinstance.graph.node_set.all()
                if self.resourceinstance_id
                else None
            ),
        )

    @classmethod
    def create_blank_tile(
        cls,
        *,
        nodegroup=None,
        nodegroup_alias=None,
        container,
        graph_nodes,
        caller=None,
    ):
        """
        Provide either a nodegroup model instance or a nodegroup_alias for which
        to create a blank tile populated with default node values. If `container`
        is a ResourceTileTree or TileTree, the new tile will be inserted into the
        container's aliased_data, and blank child tiles will be created as well.
        If `container` is None, the operation is done in the reverse direction:
        the new tile becomes the container (parent), and `caller` is inserted into
        the new tile's aliased_data.
        """
        if not nodegroup and not nodegroup_alias:
            raise ValueError("nodegroup or nodegroup_alias is required.")
        nodegroup, nodegroup_alias = cls.find_nodegroup_and_alias_from_alias_or_pk(
            nodegroup_alias,
            pk=nodegroup.pk if nodegroup else None,
            graph_nodes=graph_nodes,
        )

        parent_tile = None
        if container is None:
            if not isinstance(caller, TileTree):
                raise ValueError
            resource = caller.resourceinstance
        elif isinstance(container, ResourceInstance):
            resource = container
            caller = container
        elif isinstance(container, TileModel):
            resource = container.resourceinstance
            parent_tile = container
            caller = container
        else:  # pragma: no cover
            raise ValueError

        blank_tile = cls(
            resourceinstance=resource,
            nodegroup=nodegroup,
            parenttile=parent_tile,
            data={
                str(node.pk): cls.get_default_value(node)
                for node in nodegroup.node_set.all()
                if node.datatype != "semantic"
            },
        )
        blank_tile.sync_private_attributes(caller)

        # Finalize the aliased data according to the value of self._as_representation.
        # (e.g. either a dict of node_value, display_value, & details, or call to_python().)
        for node in nodegroup.node_set.all():
            if node.datatype != "semantic":
                node_value = blank_tile.data.get(str(node.pk))
                blank_tile.set_aliased_data(node, node_value)

        def insert_into_aliased_data(nodegroup_alias, item, target):
            try:
                aliased_data_value = getattr(target.aliased_data, nodegroup_alias)
            except AttributeError:
                aliased_data_value = None if nodegroup.cardinality == "1" else []
                setattr(target.aliased_data, nodegroup_alias, aliased_data_value)
            if isinstance(aliased_data_value, list):
                aliased_data_value.append(item)
            elif aliased_data_value is None:
                setattr(target.aliased_data, nodegroup_alias, item)
            else:
                msg = "Attempted to append to a populated cardinality-1 nodegroup"
                raise RuntimeError(msg)

        if container is None:
            insert_into_aliased_data(
                caller.find_nodegroup_alias(), item=caller, target=blank_tile
            )
        else:
            insert_into_aliased_data(nodegroup_alias, item=blank_tile, target=container)

            children = (
                nodegroup.children.all()
                # arches_version==9.0.0
                if arches_version >= (8, 0)
                else nodegroup.nodegroup_set.all()
            )
            for child_nodegroup in children:
                cls.create_blank_tile(
                    nodegroup=child_nodegroup,
                    container=blank_tile,
                    graph_nodes=graph_nodes,
                )

        return blank_tile

    def fill_blanks(self):
        """Initialize a blank tile with empty values for each nodegroup lacking a tile."""
        append_tiles_recursively(self)

    @staticmethod
    def find_nodegroup_and_alias_from_alias_or_pk(alias=None, *, graph_nodes, pk=None):
        for node in graph_nodes:
            # arches_version==9.0.0: `if alias` is redundant, alias is not nullable in v8
            if (alias and node.alias == alias) or node.pk == pk:
                return (node.nodegroup, node.alias)
        raise RuntimeError

    @staticmethod
    def get_default_value(node):
        datatype_factory = DataTypeFactory()
        # TODO: When ingesting this into core, make this a method on the node.
        try:
            widget_config = node.cardxnodexwidget_set.all()[0].config
            localized_config = widget_config.serialize()
        except (IndexError, ObjectDoesNotExist, MultipleObjectsReturned):
            d_data_type = datatype_factory.datatypes[node.datatype]
            default_widget = d_data_type.defaultwidget
            localized_config = default_widget.defaultconfig
        default_value = localized_config.get("defaultValue")
        return TileTree.get_cleaned_default_value(node, default_value)

    @staticmethod
    def get_cleaned_default_value(node, default_value):
        """
        Empty strings can break type coercion at the DRF layer, e.g.
        float(""), or datatype methods that expect UUID | None.
        There should probably be some validation in the datatype
        methods to ensure that poor types don't end up in defaultValue.
        https://github.com/archesproject/arches/issues/8715#issuecomment-3033192406
        """
        dt_instance = DataTypeFactory().get_instance(node.datatype)
        node_id_str = str(node.pk)
        mock_tile = SimpleNamespace(data={node_id_str: default_value})
        dt_instance.clean(mock_tile, node_id_str)
        cleaned_default = mock_tile.data[node_id_str]

        return cleaned_default

    def get_value_with_context(self, node, node_value, datatype_contexts=None):
        datatype_instance = DataTypeFactory().get_instance(node.datatype)
        empty_display_values = (None, "", '{"url": "", "url_label": ""}')
        compiled_json = datatype_instance.to_json(self, node)
        if datatype_contexts is None:
            datatype_contexts = {}
        ret = {
            "node_value": node_value,
            "display_value": compiled_json["@display_value"],
            "details": datatype_instance.get_details(
                node_value,
                datatype_context=datatype_contexts.get(node.datatype),
                # An optional extra hint for the ResourceInstance{list} types
                # so that prefetched related resources can be used.
                resource=self.resourceinstance if self.resourceinstance_id else None,
            ),
        }
        if ret["details"] is None:
            ret["details"] = []
        if ret["display_value"] in empty_display_values:
            # Future: upstream this into datatype methods (another hook?)
            ret["display_value"] = ""
        return ret

    def set_aliased_data(self, node, node_value, datatype_contexts=None):
        """Format node_value according to the self._as_representation flag and
        set it on self.aliased_data."""
        datatype_instance = DataTypeFactory().get_instance(node.datatype)

        if self._as_representation:
            final_val = self.get_value_with_context(
                node, node_value, datatype_contexts=datatype_contexts
            )
        else:
            if hasattr(datatype_instance, "to_python"):
                resource = self.resourceinstance if self.resourceinstance_id else None
                final_val = datatype_instance.to_python(node_value, resource=resource)
            else:
                final_val = node_value

        setattr(self.aliased_data, node.alias, final_val)

    def _save_aliased_data(
        self, *, request=None, index=True, partial=True, force_admin=False, **kwargs
    ):
        request = ensure_request(request, force_admin)
        # The `entry` for the TileTreeOperation is usually self, but it could
        # be a higher parent tile in the tree if blank parents were backfilled.
        entry = self.backfill_parent_tiles()
        operation = TileTreeOperation(
            entry=entry, request=request, partial=partial, save_kwargs=kwargs
        )
        operation.validate_and_save_tiles()

        proxy_resource = (
            Resource.objects.filter(pk=self.resourceinstance_id)
            .select_related("graph__publication")
            .get()
        )
        proxy_resource.save_descriptors()
        if index:
            proxy_resource.index()

        self.refresh_from_db(
            using=kwargs.get("using", None),
            fields=kwargs.get("update_fields", None),
        )

    def refresh_from_db(self, using=None, fields=None, from_queryset=None):
        if from_queryset is None:
            # TODO: symptom that we need a backreference to the queryset args.
            from_queryset = self.__class__.get_tiles(
                self.resourceinstance.graph.slug,
                nodegroup_alias=self.find_nodegroup_alias(),
                as_representation=getattr(self, "_as_representation", False),
            )
        self._refresh_aliased_data(using, fields, from_queryset)

    def backfill_parent_tiles(self):
        if self.nodegroup.parentnodegroup_id and not self.parenttile_id:
            self.parenttile = self.parent = TileTree.create_blank_tile(
                nodegroup=self.nodegroup.parentnodegroup,
                container=None,
                graph_nodes=self.resourceinstance.graph.node_set.all(),
                caller=self,
            )
            return self.parenttile.backfill_parent_tiles()
        return self

    def _tile_update_is_noop(self, original_data):
        """Skipping no-op tile saves avoids regenerating RxR rows, at least
        given the current implementation that doesn't serialize them."""

        datatype_factory = DataTypeFactory()
        for node in self.nodegroup.node_set.all():
            if node.datatype == "semantic":
                continue
            node_id_str = str(node.nodeid)
            old = original_data.get(node_id_str)
            datatype_instance = datatype_factory.get_instance(node.datatype)
            new = self.data[node_id_str]
            if not datatype_instance.values_match(old, new):
                return False

        return True

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
