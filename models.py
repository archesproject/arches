import logging
import sys
from collections import defaultdict
from functools import partial
from itertools import chain, zip_longest
from operator import attrgetter

from django.core.exceptions import ValidationError
from django.db import ProgrammingError, models, transaction
from django.http import HttpRequest
from django.utils.translation import gettext as _

from arches import __version__ as arches_version
from arches.app.models.models import (
    GraphModel,
    Node,
    ResourceInstance,
    TileModel,
)
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile, TileValidationError
from arches.app.models.utils import field_names
from arches.app.utils.permission_backend import user_is_resource_reviewer

from arches_querysets.lookups import *
from arches_querysets.querysets import (
    ResourceInstanceQuerySet,
    SemanticTileManager,
    SemanticTileQuerySet,
)
from arches_querysets.utils import datatype_transforms
from arches_querysets.utils.models import (
    field_attnames,
    get_nodegroups_here_and_below,
    pop_arches_model_kwargs,
)


logger = logging.getLogger(__name__)


class SemanticResource(ResourceInstance):
    objects = ResourceInstanceQuerySet.as_manager()

    class Meta:
        proxy = True
        db_table = "resource_instances"
        permissions = (("no_access_to_resourceinstance", "No Access"),)

    def __init__(self, *args, **kwargs):
        arches_model_kwargs, other_kwargs = pop_arches_model_kwargs(
            kwargs, self._meta.get_fields()
        )
        super().__init__(*args, **other_kwargs)
        for kwarg, value in arches_model_kwargs.items():
            setattr(self, kwarg, value)

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
        if not hasattr(self, "_fetched_root_nodes"):
            return super().save(**kwargs)
        with transaction.atomic():
            # update_fields=set() will abort the save, but at least calling
            # into save() will run a sanity check on unsaved relations.
            super().save(update_fields=set())
            self._save_tiles_for_pythonic_model(user=user, index=index, **kwargs)
            # TODO: document that this is not compatible with signals.
            self.save_edit(user=user)

    def clean(self):
        """Raises a compound ValidationError with any failing tile values."""
        self._update_tiles_from_pythonic_model_values()

    def _save_tiles_for_pythonic_model(self, user=None, index=False, **kwargs):
        """Raises a compound ValidationError with any failing tile values.

        It's not exactly idiomatic for a Django project to clean()
        values during a save(), but we can't easily express this logic
        in a "pure" DRF field validator, because:
            - the node values are phantom fields.
            - we have other entry points besides DRF.
        """
        from arches.app.datatypes.datatypes import DataTypeFactory

        dummy_request = HttpRequest()
        dummy_request.user = user
        datatype_factory = DataTypeFactory()
        to_insert, to_update, to_delete = (
            self._update_tiles_from_pythonic_model_values()
        )

        # Instantiate proxy models for now, but TODO: expose this
        # functionality on vanilla models, and in bulk.
        upserts = to_insert | to_update
        insert_proxies = [
            # TODO: make readable.
            Tile(
                **(pop_arches_model_kwargs(vars(insert), self._meta.get_fields())[1]),
            )
            for insert in to_insert
        ]
        update_proxies = Tile.objects.filter(pk__in=[tile.pk for tile in to_update])
        upsert_proxies = chain(insert_proxies, update_proxies)
        delete_proxies = Tile.objects.filter(pk__in=[tile.pk for tile in to_delete])

        with transaction.atomic():
            # Interact with the database in bulk as much as possible, but
            # run certain side effects from Tile.save() one-at-a-time until
            # proxy model methods can be refactored. Then run in bulk.
            for upsert_proxy, vanilla_instance in zip(
                upsert_proxies, upserts, strict=True
            ):
                if upsert_proxy.pk != vanilla_instance.pk:
                    upsert_proxy.pk = vanilla_instance.pk
                    logger.warning(
                        "DEBUG next week. Recent dev/8.0.x changes? Might be a gift."
                    )
                upsert_proxy._existing_data = upsert_proxy.data
                upsert_proxy._existing_provisionaledits = upsert_proxy.provisionaledits

                # Sync proxy instance fields.
                for field in field_attnames(vanilla_instance):
                    setattr(upsert_proxy, field, getattr(vanilla_instance, field))

                # Run tile lifecycle updates on proxy instance.
                upsert_proxy._Tile__preSave()
                upsert_proxy.check_for_missing_nodes()
                upsert_proxy.check_for_constraint_violation()
                (
                    oldprovisionalvalue,
                    newprovisionalvalue,
                    provisional_edit_log_details,
                ) = vanilla_instance._apply_provisional_edit(
                    upsert_proxy,
                    upsert_proxy._existing_data,
                    upsert_proxy._existing_provisionaledits,
                    user=user,
                )
                # Remember the values needed for the edit log updates later.
                upsert_proxy._oldprovisionalvalue = oldprovisionalvalue
                upsert_proxy._newprovisionalvalue = newprovisionalvalue
                upsert_proxy._provisional_edit_log_details = (
                    provisional_edit_log_details
                )
                upsert_proxy._existing_data = vanilla_instance.data

            for delete_proxy in delete_proxies:
                delete_proxy._Tile__preDelete(request=dummy_request)

            if to_insert:
                inserted = TileModel.objects.bulk_create(to_insert)
                # Pay the cost of a second TileModel -> Tile transform until refactored.
                refreshed_insert_proxies = Tile.objects.filter(
                    pk__in=[t.pk for t in inserted]
                )
                for before, after in zip(
                    insert_proxies, refreshed_insert_proxies, strict=True
                ):
                    assert before.pk == after.pk
                    after._newprovisionalvalue = before._newprovisionalvalue
                    after._provisional_edit_log_details = (
                        before._provisional_edit_log_details
                    )
                upsert_proxies = refreshed_insert_proxies | update_proxies
            else:
                insert_proxies = TileModel.objects.none()
            if to_update:
                TileModel.objects.bulk_update(
                    to_update, {"data", "parenttile", "provisionaledits"}
                )
            if to_delete:
                TileModel.objects.filter(pk__in=[t.pk for t in to_delete]).delete()

            super().save(**kwargs)

            for upsert_tile in upserts:
                for root_node in self._fetched_root_nodes:
                    if upsert_tile.nodegroup_id == root_node.nodegroup_id:
                        for node in root_node.nodegroup.node_set.all():
                            datatype = datatype_factory.get_instance(node.datatype)
                            datatype.post_tile_save(
                                upsert_tile, str(node.pk), request=dummy_request
                            )
                        break

            for upsert_proxy in upsert_proxies:
                upsert_proxy._Tile__postSave()

            # Save edits: could be done in bulk once above side effects are un-proxied.
            for insert_proxy in insert_proxies:
                insert_proxy.save_edit(
                    user=user,
                    edit_type="tile create",
                    old_value={},
                    new_value=insert_proxy.data,
                    newprovisionalvalue=insert_proxy._newprovisionalvalue,
                    provisional_edit_log_details=insert_proxy._provisional_edit_log_details,
                    transaction_id=None,
                    # TODO: get this information upstream somewhere.
                    new_resource_created=False,
                    note=None,
                )
            for update_proxy in update_proxies:
                update_proxy.save_edit(
                    user=user,
                    edit_type="tile edit",
                    old_value=update_proxy._existing_data,
                    new_value=update_proxy.data,
                    newprovisionalvalue=update_proxy._newprovisionalvalue,
                    oldprovisionalvalue=update_proxy._oldprovisionalvalue,
                    provisional_edit_log_details=update_proxy._provisional_edit_log_details,
                    transaction_id=None,
                )

        self.refresh_from_db(
            using=kwargs.get("using", None),
            fields=kwargs.get("update_fields", None),
        )

        # Instantiate proxy model for now, but refactor & expose this on vanilla model
        proxy_resource = Resource.objects.get(pk=self.pk)
        proxy_resource.save_descriptors()
        if index:
            proxy_resource.index()

    def _update_tiles_from_pythonic_model_values(self):
        """Move values from model instance to prefetched tiles, and validate.
        Raises ValidationError if new data fails datatype validation.
        """
        # TODO: put all this state in a helper dataclass to ease passing it around.
        errors_by_node_alias = defaultdict(list)
        to_insert = set()
        to_update = set()
        to_delete = set()

        original_tile_data_by_tile_id = {}
        for root_node in self._fetched_root_nodes:
            self._update_tile_for_grouping_node(
                root_node,
                self,
                original_tile_data_by_tile_id,
                to_insert,
                to_update,
                to_delete,
                errors_by_node_alias,
            )

        if errors_by_node_alias:
            del self._annotated_tiles
            raise ValidationError(
                {
                    alias: ValidationError([e["message"] for e in errors])
                    for alias, errors in errors_by_node_alias.items()
                }
            )

        return to_insert, to_update, to_delete

    def _update_tile_for_grouping_node(
        self,
        grouping_node,
        container,
        original_tile_data_by_tile_id,
        to_insert,
        to_update,
        to_delete,
        errors_by_node_alias,
    ):
        NOT_PROVIDED = object()

        if isinstance(container, dict):
            new_tiles = container.get(grouping_node.alias, NOT_PROVIDED)
        else:
            new_tiles = getattr(container, grouping_node.alias, NOT_PROVIDED)
        if new_tiles is NOT_PROVIDED:
            return
        if grouping_node.nodegroup.cardinality == "1":
            if new_tiles is None:
                new_tiles = []
            else:
                new_tiles = [new_tiles]
        if all(isinstance(tile, TileModel) for tile in new_tiles):
            new_tiles.sort(key=attrgetter("sortorder"))
        else:
            # DRF doesn't provide nested writable fields by default.
            # TODO: probably move this to the serializers.
            parent_tile = container if isinstance(container, TileModel) else None
            new_tiles = [
                SemanticTile(**{**tile, "parenttile": parent_tile})
                for tile in new_tiles
            ]
        db_tiles = [
            t
            for t in self._annotated_tiles
            if t.find_nodegroup_alias() == grouping_node.alias
        ]
        if not db_tiles:
            next_sort_order = 0
        else:
            next_sort_order = max(t.sortorder or 0 for t in db_tiles) + 1
        for db_tile, new_tile in zip_longest(
            db_tiles, new_tiles, fillvalue=NOT_PROVIDED
        ):
            if new_tile is NOT_PROVIDED:
                to_delete.add(db_tile)
                continue
            if db_tile is NOT_PROVIDED:
                new_tile.nodegroup_id = grouping_node.nodegroup_id
                new_tile.resourceinstance_id = self.pk
                new_tile.sortorder = next_sort_order
                next_sort_order += 1
                for node in grouping_node.nodegroup.node_set.all():
                    new_tile.data[str(node.pk)] = None

                parent_tile = new_tile.parenttile
                exclude = None
                if parent_tile:
                    if (
                        parent_tile.nodegroup_id
                        != grouping_node.nodegroup.parentnodegroup_id
                    ):
                        raise ValueError(
                            _("Wrong nodegroup for parent tile: {}".format(parent_tile))
                        )
                    if parent_tile._state.adding:
                        exclude = {"parenttile"}

                new_tile._incoming_tile = new_tile
                new_tile.full_clean(exclude=exclude)
                to_insert.add(new_tile)
            else:
                original_tile_data_by_tile_id[db_tile.pk] = {**db_tile.data}
                db_tile._incoming_tile = new_tile
                to_update.add(db_tile)

        nodes = grouping_node.nodegroup.node_set.all()
        for tile in to_insert | to_update:
            if tile.nodegroup_id != grouping_node.pk:
                # TODO: this is a symptom this should be refactored.
                continue
            children = tile.nodegroup.nodegroup_set.all()
            if arches_version < "8":
                grouping_node = (
                    Node.objects.filter(pk=tile.nodegroup.pk)
                    .prefetch_related("node_set")
                    .get()
                )
                for child_nodegroup in children:
                    child_nodegroup.grouping_node = grouping_node
            for child_nodegroup in children:
                self._update_tile_for_grouping_node(
                    grouping_node=child_nodegroup.grouping_node,
                    container=tile._incoming_tile,
                    original_tile_data_by_tile_id=original_tile_data_by_tile_id,
                    to_insert=to_insert,
                    to_update=to_update,
                    to_delete=to_delete,
                    errors_by_node_alias=errors_by_node_alias,
                )
            self._validate_and_patch_from_tile_values(
                tile, nodes=nodes, errors_by_node_alias=errors_by_node_alias
            )

        for tile in to_insert | to_update:
            if tile.nodegroup.pk != grouping_node.pk:
                # TODO: this is a symptom this should be refactored.
                continue
            # Remove blank tiles if they have no children.
            if (
                not any(tile.data.values())
                and not tile.children.exists()
                # Check unsaved children.
                and not any(
                    getattr(tile._incoming_tile, child_tile_alias, None)
                    for child_tile_alias in grouping_node.nodegroup.children.values_list(
                        # TODO: 7.6 compat
                        "grouping_node__alias",
                        flat=True,
                    )
                )
            ):
                if tile._state.adding:
                    to_insert.remove(tile)
                else:
                    to_update.remove(tile)
                    to_delete.add(tile)

        for tile in to_insert | to_update:
            if tile.nodegroup.pk != grouping_node.pk:
                # TODO: this is a symptom this should be refactored.
                continue
            # Remove no-op upserts.
            if (
                original_data := original_tile_data_by_tile_id.pop(tile.pk, None)
            ) and tile._tile_update_is_noop(original_data):
                to_update.remove(tile)

    @staticmethod
    def _validate_and_patch_from_tile_values(tile, *, nodes, errors_by_node_alias):
        """Validate data found on ._incoming_tile and move it to .data.
        Update errors_by_node_alias in place."""
        from arches.app.datatypes.datatypes import DataTypeFactory

        NOT_PROVIDED = object()
        datatype_factory = DataTypeFactory()
        for node in nodes:
            node_id_str = str(node.pk)
            # TODO: remove this switch and deserialize this in DRF.
            if isinstance(tile._incoming_tile, TileModel):
                value_to_validate = getattr(
                    tile._incoming_tile, node.alias, NOT_PROVIDED
                )
            else:
                value_to_validate = tile._incoming_tile.get(node.alias, NOT_PROVIDED)
            if value_to_validate is NOT_PROVIDED:
                continue

            # This ugly section provides hooks to patch in better datatype methods.
            # It won't live forever.
            datatype_instance = datatype_factory.get_instance(node.datatype)
            # TODO: pre_structure_tile_data()?
            # TODO: move this to Tile.full_clean()?
            # https://github.com/archesproject/arches/issues/10851#issuecomment-2427305853
            if transform_fn := getattr(
                datatype_transforms, f"{node.datatype}_transform_value_for_tile", None
            ):
                transform_fn = partial(transform_fn, datatype_instance)
            else:
                transform_fn = datatype_instance.transform_value_for_tile
            if clean_fn := getattr(datatype_transforms, f"{node.datatype}_clean", None):
                clean_fn = partial(clean_fn, datatype_instance)
            else:
                clean_fn = datatype_instance.clean
            if validate_fn := getattr(
                datatype_transforms, f"{node.datatype}_validate", None
            ):
                validate_fn = partial(validate_fn, datatype_instance)
            else:
                validate_fn = datatype_instance.validate
            if pre_tile_save_fn := getattr(
                datatype_transforms, f"{node.datatype}_pre_tile_save", None
            ):
                pre_tile_save_fn = partial(pre_tile_save_fn, datatype_instance)
            else:
                pre_tile_save_fn = datatype_instance.pre_tile_save

            if value_to_validate is None:
                tile.data[node_id_str] = None
                continue
            try:
                transformed = transform_fn(value_to_validate, **node.config)
            except ValueError:  # BooleanDataType raises.
                # validate() will handle.
                transformed = value_to_validate

            # Patch the transformed data into the tile.data.
            tile.data[node_id_str] = transformed

            clean_fn(tile, node_id_str)

            if errors := validate_fn(transformed, node=node):
                errors_by_node_alias[node.alias].extend(errors)

            try:
                pre_tile_save_fn(tile, node_id_str)
            except TypeError:  # GeoJSONDataType raises.
                errors_by_node_alias[node.alias].append(
                    datatype_instance.create_error_message(
                        tile.data[node_id_str], None, None, None
                    )
                )

    def refresh_from_db(self, using=None, fields=None, from_queryset=None):
        if from_queryset is None and (
            root_nodes := getattr(self, "_fetched_root_nodes", set())
        ):
            aliases = [n.alias for n in root_nodes]
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
        for kwarg, value in arches_model_kwargs.items():
            setattr(self, kwarg, value)

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
        defer=None,
        only=None,
        as_representation=False,
        allow_empty=False,
    ):
        """
        See `arches.app.models.querysets.TileQuerySet.with_node_values`.
        """

        root_node = cls._root_node(graph_slug, root_node_alias)
        branch_nodes = []
        for nodegroup in get_nodegroups_here_and_below(root_node.nodegroup):
            branch_nodes.extend(list(nodegroup.node_set.all()))

        return (
            cls.objects.filter(nodegroup_id=root_node.pk)
            .with_node_values(
                branch_nodes,
                root_node=root_node,
                defer=defer,
                only=[root_node.alias],  # determine whether to expose
                as_representation=as_representation,
                allow_empty=allow_empty,
            )
            .annotate(_nodegroup_alias=models.Value(root_node_alias))
        )

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
        if not hasattr(self, "_fetched_nodes"):
            return super().save(**kwargs)
        nodegroup_alias = self.find_nodegroup_alias()
        try:
            with transaction.atomic():
                # update_fields=set() will abort the save, but at least calling
                # into save() will run a sanity check on unsaved relations.
                super().save(update_fields=set())
                if self.sortorder is None or self.is_fully_provisional():
                    self.set_next_sort_order()
                self._save_from_pythonic_model_values(user=user, index=index, **kwargs)
                # TODO: document that this is not compatible with signals.
        except ProgrammingError as e:
            if e.args and "excess_tiles" in e.args[0]:
                msg = _("Tile Cardinality Error")
                raise ValidationError({nodegroup_alias: msg}) from e
            raise

    def _save_from_pythonic_model_values(self, *, user=None, index=False, **kwargs):
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

        self._incoming_tile = {}
        model_fields = field_names(self)
        for tile_attr, tile_value in vars(self).items():
            if tile_attr.startswith("_") or tile_attr in model_fields:
                continue
            self._incoming_tile[tile_attr] = tile_value

        errors_by_alias = defaultdict(list)
        if not self.nodegroup:
            raise ValueError
        # TODO: Move. This shouldn't emit resource edit log entries.
        SemanticResource._validate_and_patch_from_tile_values(
            self,
            nodes=self.nodegroup.node_set.all(),
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
        for grouping_node in resource._fetched_root_nodes:
            for node in grouping_node.nodegroup.node_set.all():
                setattr(self, node.alias, self.data.get(str(node.pk)))
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
            # and generate_tile_annotations().

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

    class Meta:
        proxy = True
        db_table = "graphs"
