import logging
import sys
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
from arches.app.utils.permission_backend import (
    get_nodegroups_by_perm,
    user_is_resource_reviewer,
)

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
    get_recursive_prefetches,
    get_nodegroups_here_and_below,
    pop_arches_model_kwargs,
)


logger = logging.getLogger(__name__)


class AliasedData(SimpleNamespace):
    """Provides dot access into node values and nested nodegroups by alias.

    >>> ResourceTileTree.get_tiles('new_resource_model_1').get(...).aliased_data
    namespace(string_node={'en': {'value': 'abcde', 'direction': 'ltr'}},
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
    def _refresh_aliased_data(self, using, fields, from_queryset):
        try:
            del self._tile_trees
        except AttributeError:
            pass

        # Commandeer the responsibility for filtering on pk from Django
        # so we can retrieve aliased data from the queryset cache.
        from_queryset = from_queryset.filter(pk=self.pk)
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
        self._permitted_nodes = Node.objects.none()
        # Data-collecting nodes that were queried
        self._queried_nodes = Node.objects.none()
        self._as_representation = False

    @property
    def aliased_data(self):
        return self._aliased_data

    @aliased_data.setter
    def aliased_data(self, value):
        self._aliased_data = value

    def save(self, *, request=None, index=True, **kwargs):
        self._save_aliased_data(request=request, index=index, **kwargs)

    @classmethod
    def get_tiles(
        cls,
        graph_slug,
        *,
        resource_ids=None,
        defer=None,
        only=None,
        as_representation=False,
        user=None,
    ):
        """Return a chainable QuerySet for a requested graph's instances,
        with tile data keyed by node and nodegroup aliases.

        See `arches_querysets.querysets.ResourceTileTreeQuerySet.get_tiles`.
        """
        return cls.objects.get_tiles(
            graph_slug,
            resource_ids=resource_ids,
            defer=defer,
            only=only,
            as_representation=as_representation,
            user=user,
        )

    def append_tile(self, nodegroup_alias):
        TileTree.create_blank_tile(
            nodegroup_alias=nodegroup_alias,
            container=self,
            permitted_nodes=self._permitted_nodes,
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

    def refresh_from_db(self, using=None, fields=None, from_queryset=None, user=None):
        if from_queryset is None:
            # TODO: symptom that we need a backreference to the queryset args.
            from_queryset = self.__class__.get_tiles(
                self.graph.slug,
                only={node.alias for node in self._queried_nodes},
                as_representation=getattr(self, "_as_representation", False),
                user=user,
            )
        self._refresh_aliased_data(using, fields, from_queryset)

    def _save_aliased_data(self, *, request=None, index=True, **kwargs):
        """Raises a compound ValidationError with any failing tile values."""
        operation = TileTreeOperation(entry=self, request=request, save_kwargs=kwargs)
        operation.validate_and_save_tiles()

        # Instantiate proxy model for now, but refactor & expose this on vanilla model
        proxy_resource = Resource.objects.get(pk=self.pk)
        proxy_resource.save_descriptors()
        if index:
            proxy_resource.index()

        if request:
            self.save_edit(user=request.user, transaction_id=operation.transaction_id)

        self.refresh_from_db(
            using=kwargs.get("using"),
            fields=kwargs.get("update_fields"),
            user=request.user if request else None,
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
        self._permitted_nodes = Node.objects.none()
        # Data-collecting nodes that were queried
        self._queried_nodes = Node.objects.none()

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

    def save(self, *, request=None, index=True, **kwargs):
        if arches_version < (8, 0) and self.nodegroup:
            # Cannot supply this too early, as nodegroup might be included
            # with the request and already instantiated to a fresh object.
            self.nodegroup.grouping_node = self.nodegroup.node_set.get(
                pk=models.F("nodegroup")
            )
        request = request or self._request
        # Mimic some computations trapped on TileModel.save().
        if (
            arches_version >= (8, 0)
            and self.sortorder is None
            or self.is_fully_provisional()
        ):
            self.set_next_sort_order()
        self._save_aliased_data(request=request, index=index, **kwargs)

    @classmethod
    def get_tiles(
        cls,
        graph_slug,
        nodegroup_alias,
        *,
        resource_ids=None,
        defer=None,
        only=None,
        as_representation=False,
        user=None,
    ):
        """See `arches_querysets.querysets.TileTreeQuerySet.get_tiles`."""

        source_graph = GraphWithPrefetching.prefetch(
            graph_slug, resource_ids=resource_ids, user=user
        )
        for node in source_graph.permitted_nodes:
            if node.alias == nodegroup_alias:
                entry_node = node
                break
        else:
            raise Node.DoesNotExist(f"graph: {graph_slug} node: {nodegroup_alias}")

        if not entry_node.nodegroup:
            raise ValueError(f'"{nodegroup_alias}" is a top node.')

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

        return qs.get_tiles(
            graph_slug=graph_slug,
            nodegroup_alias=nodegroup_alias,
            permitted_nodes=entry_node_and_nodes_below,
            defer=defer,
            only=filtered_only,
            as_representation=as_representation,
            entry_node=entry_node,
        )

    def serialize(self, **kwargs):
        """Prevent serialization of properties (would cause cycles)."""
        options = {**kwargs}
        options["exclude"] = {"data", "parent"} | set(options.pop("exclude", {}))
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
                raise ValidationError(_("Wrong parent tile for parent nodegroup."))
        # Exclude parenttile to ensure batch creations of parent & child do not fail.
        new_exclude = [*(exclude or []), "parenttile"]
        super().clean_fields(exclude=new_exclude)

    def find_nodegroup_alias(self):
        # TileTreeManager provides grouping_node on 7.6
        if self.nodegroup_id and hasattr(self.nodegroup, "grouping_node"):
            return self.nodegroup.grouping_node.alias
        if not getattr(self, "_nodegroup_alias", None):
            self._nodegroup_alias = self.nodegroup.alias if self.nodegroup_id else None
        return self._nodegroup_alias

    @classmethod
    def deserialize(cls, tile_dict, parent_tile: TileModel | None):
        """
        If you're not using the Django REST Framework optional dependency,
        e.g. if you request an evaluate a queryset with as_representation=True and
        resave the instance, you'll need a way to deserialize dicts into TileTrees.
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

        if arches_version < (8, 0):
            # Simulate the default supplied by v8.
            tile.data = {}

        return tile

    def sync_private_attributes(self, source):
        self._as_representation = source._as_representation
        self._queried_nodes = source._queried_nodes
        self._permitted_nodes = source._permitted_nodes

    def append_tile(self, nodegroup_alias):
        TileTree.create_blank_tile(
            nodegroup_alias=nodegroup_alias,
            container=self,
            permitted_nodes=self._permitted_nodes,
        )

    @classmethod
    def create_blank_tile(
        cls, *, nodegroup=None, nodegroup_alias=None, container, permitted_nodes
    ):
        if not nodegroup:
            if not nodegroup_alias:
                raise ValueError("nodegroup or nodegroup_alias is required.")
            nodegroup = cls.find_nodegroup_from_alias_or_pk(
                nodegroup_alias, permitted_nodes=permitted_nodes
            )

        if not nodegroup_alias:
            nodegroup_alias = cls.find_nodegroup_from_alias_or_pk(
                pk=nodegroup.pk, permitted_nodes=permitted_nodes
            )._nodegroup_alias

        if isinstance(container, ResourceInstance):
            resource = container
            parent_tile = None
        else:
            resource = container.resourceinstance
            parent_tile = container

        # Initialize a blank tile with nested data.
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
        blank_tile.sync_private_attributes(container)

        # Finalize the aliased data according to the value of self._as_representation.
        # (e.g. either a dict of display_value & interchange_value, or call to_python().)
        for node in nodegroup.node_set.all():
            if node.datatype != "semantic":
                node_value = blank_tile.data.get(str(node.pk))
                blank_tile.set_aliased_data(node, node_value)

        # Attach the blank tile to the container.
        try:
            aliased_data_value = getattr(container.aliased_data, nodegroup_alias)
        except AttributeError:
            aliased_data_value = None if nodegroup.cardinality == "1" else []
            setattr(container.aliased_data, nodegroup_alias, aliased_data_value)
        if isinstance(aliased_data_value, list):
            aliased_data_value.append(blank_tile)
        elif aliased_data_value is None:
            setattr(container.aliased_data, nodegroup_alias, blank_tile)
        else:
            msg = "Attempted to append to a populated cardinality-1 nodegroup"
            raise RuntimeError(msg)

        children = (
            nodegroup.children.all()
            if arches_version >= (8, 0)
            else nodegroup.nodegroup_set.all()
        )
        for child_nodegroup in children:
            cls.create_blank_tile(
                nodegroup=child_nodegroup,
                container=blank_tile,
                permitted_nodes=permitted_nodes,
            )

        return blank_tile

    def fill_blanks(self):
        """Initialize a blank tile with empty values for each nodegroup lacking a tile."""
        append_tiles_recursively(self)

    @staticmethod
    def find_nodegroup_from_alias_or_pk(alias=None, *, permitted_nodes, pk=None):
        """Some of this complexity can be removed when dropping 7.6."""
        for permitted_node in permitted_nodes:
            if permitted_node.alias == alias or permitted_node.pk == pk:
                permitted_node.nodegroup._nodegroup_alias = permitted_node.alias
                return permitted_node.nodegroup
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

    def get_display_interchange_pair(self, node, node_value):
        datatype_instance = DataTypeFactory().get_instance(node.datatype)
        empty_values = (None, "", '{"url": "", "url_label": ""}')
        compiled_json = datatype_instance.to_json(self, node)
        pair = {
            "display_value": compiled_json["@display_value"],
            "interchange_value": datatype_instance.get_interchange_value(
                node_value,
                # Provide details to avoid repetitive computations.
                details=compiled_json.get("details"),
                # An optional extra hint for the ResourceInstance{list} types
                # so that prefetched related resources can be used.
                resource=self.resourceinstance if self.resourceinstance_id else None,
            ),
        }
        if pair["display_value"] in empty_values:
            # Future: upstream this into datatype methods (another hook?)
            pair["display_value"] = _("(Empty)")
        return pair

    def set_aliased_data(self, node, node_value):
        """Format node_value according to the self._as_representation flag and
        set it on self.aliased_data."""
        datatype_instance = DataTypeFactory().get_instance(node.datatype)

        if self._as_representation:
            final_val = self.get_display_interchange_pair(node, node_value)
        else:
            if hasattr(datatype_instance, "to_python"):
                resource = self.resourceinstance if self.resourceinstance_id else None
                final_val = datatype_instance.to_python(node_value, resource=resource)
            else:
                final_val = node_value

        setattr(self.aliased_data, node.alias, final_val)

    def _save_aliased_data(self, *, request=None, index=True, **kwargs):
        operation = TileTreeOperation(entry=self, request=request, save_kwargs=kwargs)
        operation.validate_and_save_tiles()

        proxy_resource = Resource.objects.get(pk=self.resourceinstance_id)
        proxy_resource.save_descriptors()
        if index:
            proxy_resource.index()

        self.refresh_from_db(
            using=kwargs.get("using", None),
            fields=kwargs.get("update_fields", None),
        )

    def refresh_from_db(self, using=None, fields=None, from_queryset=None, user=None):
        if from_queryset is None:
            # TODO: symptom that we need a backreference to the queryset args.
            from_queryset = self.__class__.get_tiles(
                self.resourceinstance.graph.slug,
                nodegroup_alias=self.find_nodegroup_alias(),
                only={node.alias for node in self._queried_nodes},
                as_representation=getattr(self, "_as_representation", False),
                user=user,
            )
        self._refresh_aliased_data(using, fields, from_queryset)

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

    @staticmethod
    def _resource_value_to_python(tile_val):
        if tile_val is None or len(tile_val) != 1:
            return tile_val
        return tile_val[0]

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
    def prefetch(cls, graph_slug=None, *, resource_ids=None, user=None):
        """Return a graph with necessary prefetches for
        TileTree._prefetch_related_objects(), which is what builds the shape
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
            children = "children"
        else:
            children = "nodegroup_set"

        prefetches = [
            "node_set__cardxnodexwidget_set",
            "node_set__nodegroup__parentnodegroup",
            "node_set__nodegroup__node_set",
            "node_set__nodegroup__node_set__cardxnodexwidget_set",
            "node_set__nodegroup__cardmodel_set",
            *get_recursive_prefetches(
                f"node_set__nodegroup__{children}", depth=12, recursive_part=children
            ),
            *get_recursive_prefetches(
                f"node_set__nodegroup__{children}__node_set",
                depth=12,
                recursive_part=children,
            ),
            *get_recursive_prefetches(
                f"node_set__nodegroup__{children}__cardmodel_set",
                depth=12,
                recursive_part=children,
            ),
            *get_recursive_prefetches(
                f"node_set__nodegroup__{children}__node_set__cardxnodexwidget_set",
                depth=12,
                recursive_part=children,
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
                children = (
                    nodegroup.children.all()
                    if arches_version >= (8, 0)
                    else nodegroup.nodegroup_set.all()
                )
                for child_nodegroup in children:
                    child_nodegroup.grouping_node = grouping_node_map.get(
                        child_nodegroup.pk
                    )
