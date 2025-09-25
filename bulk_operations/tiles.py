import logging
import uuid
from collections import defaultdict
from operator import attrgetter

from django.core.exceptions import ValidationError
from django.db import ProgrammingError, transaction
from django.db.models import F, Q
from django.utils.translation import get_language, gettext as _

from arches import VERSION as arches_version
from arches.app.models.models import (
    CardXNodeXWidget,
    Language,
    Node,
    TileModel,
    ResourceInstance,
)
from arches.app.models.tile import Tile, TileValidationError

from arches_querysets.datatypes.datatypes import DataTypeFactory
from arches_querysets.utils.models import (
    field_attnames,
    get_nodegroups_here_and_below,
    pop_arches_model_kwargs,
)

logger = logging.getLogger(__name__)

NOT_PROVIDED = object()


class TileTreeOperation:
    def __init__(self, *, entry, request, partial=True, save_kwargs=None):
        self.to_insert = set()
        self.to_update = set()
        self.to_delete = set()
        self.errors_by_node_alias = defaultdict(list)
        self.entry = entry  # resource or tile
        self.datatype_factory = DataTypeFactory()
        self.languages = Language.objects.all()
        self.request = request
        self.partial = partial
        self.save_kwargs = save_kwargs or {}
        self.transaction_id = uuid.uuid4()
        # arches==9.0.0, replace these attributes by simply reading from
        # self.request.user.userprofile, which uses @cached_property as of Arches 8.1.
        # Store off these properties since they are expensive.
        self.editable_nodegroups: set[str] = (
            self.request.user.userprofile.editable_nodegroups
        )
        self.deletable_nodegroups: set[str] = (
            self.request.user.userprofile.deletable_nodegroups
        )

        if (self.partial and self.request.method == "PUT") or (
            not self.partial and self.request.method == "PATCH"
        ):
            raise ValueError(
                f"Expected partial={not self.partial} for {self.request.method} request."
            )

        if isinstance(entry, TileModel):
            self.resourceid = self.entry.resourceinstance_id
            self.nodegroups = get_nodegroups_here_and_below(self.entry.nodegroup)
            existing_tiles = (
                entry.__class__.objects.filter(
                    resourceinstance_id=self.resourceid,
                    nodegroup_id__in=[ng.pk for ng in self.nodegroups],
                )
                .select_related("nodegroup")
                .order_by("sortorder")
            )
            # arches_version==9.0.0
            if arches_version < (8, 0):
                # Cannot supply this too early, as nodegroup might be included
                # with the request and already instantiated to a fresh object.
                grouping_node = [
                    node
                    for node in entry.resourceinstance.graph.node_set.all()
                    if node.pk == node.nodegroup_id
                ][0]
                entry.nodegroup.grouping_node = grouping_node
        else:
            self.resourceid = self.entry.pk
            self.nodegroups = []  # not necessary to populate.
            existing_tiles = getattr(self.entry, "_tile_trees", [])

        self.grouping_nodes_by_nodegroup_id = self._get_grouping_node_lookup()
        self.existing_tiles_by_nodegroup_alias = defaultdict(list)
        for tile in existing_tiles:
            alias = tile.find_nodegroup_alias(self.grouping_nodes_by_nodegroup_id)
            self.existing_tiles_by_nodegroup_alias[alias].append(tile)
        self.new_resource_created = bool(existing_tiles)

    def _get_grouping_node_lookup(self):
        from arches_querysets.models import TileTree

        if isinstance(self.entry, TileTree):
            graph = self.entry.resourceinstance.graph
        else:
            graph = self.entry.graph
        filters = Q(pk=F("nodegroup_id"), graph__slug=graph.slug)
        # arches_version==9.0.0
        if arches_version >= (8, 0):
            filters &= Q(source_identifier=None)
            return {
                node.pk: node
                for node in Node.objects.filter(filters).select_related(
                    "nodegroup__grouping_node__nodegroup__parentnodegroup"
                )
            }
        else:
            ret = {
                node.pk: node
                for node in Node.objects.filter(filters).select_related(
                    "nodegroup__parentnodegroup"
                )
            }
            for node_id, node in ret.items():
                node.nodegroup.grouping_node = ret[node_id]
            return ret

    def validate_and_save_tiles(self):
        self.validate()
        try:
            self._save()
        except ProgrammingError as e:
            if e.args and "excess_tiles" in e.args[0]:
                nodegroup_id = e.args[0].split("nodegroupid: ")[1].split(",")[0]
                uid = uuid.UUID(nodegroup_id)
                nodegroup_alias = self.grouping_nodes_by_nodegroup_id[uid].alias
                msg = _("Tile Cardinality Error")
                raise ValidationError({nodegroup_alias: msg}) from e
            raise
        self.after_update_all()

    def validate(self, delete_absent_children=False):
        """Move values from resource or tile to prefetched tiles, and validate.
        Raises ValidationError if new data fails datatype validation.

        HTTP PUT should request delete_absent_children=True to delete child tiles
        not in the payload.
        HTTP PATCH should request delete_absent_children=False (default).
        """
        original_tile_data_by_tile_id = {}
        if isinstance(self.entry, TileModel):
            self._update_tile(
                self.grouping_nodes_by_nodegroup_id[self.entry.nodegroup_id],
                None,
                original_tile_data_by_tile_id,
                delete_siblings=False,
            )
        else:
            for grouping_node in self.grouping_nodes_by_nodegroup_id.values():
                if grouping_node.nodegroup.parentnodegroup_id:
                    continue
                self._update_tile(
                    grouping_node,
                    self.entry,
                    original_tile_data_by_tile_id,
                    delete_siblings=delete_absent_children,
                )

        if self.errors_by_node_alias:
            raise ValidationError(
                {
                    alias: ValidationError([e["message"] for e in errors])
                    for alias, errors in self.errors_by_node_alias.items()
                }
            )

    def _update_tile(
        self,
        grouping_node,
        container,
        original_tile_data_by_tile_id,
        delete_siblings=False,
    ):
        if str(grouping_node.nodegroup_id) not in self.editable_nodegroups:
            # Currently also prevents deletes.
            return

        try:
            new_tiles = self._extract_incoming_tiles(container, grouping_node)
        except KeyError:
            return
        existing_tiles = self.existing_tiles_by_nodegroup_alias[grouping_node.alias]
        if not existing_tiles:
            next_sort_order = 0
        else:
            next_sort_order = max(t.sortorder or 0 for t in existing_tiles) + 1

        to_insert = set()
        to_update = set()
        to_delete = set()
        for existing_tile, new_tile in self._pair_tiles(existing_tiles, new_tiles):
            if new_tile is NOT_PROVIDED:
                if (
                    delete_siblings
                    and str(existing_tile.nodegroup_id) in self.deletable_nodegroups
                ):
                    to_delete.add(existing_tile)
                continue
            if existing_tile is NOT_PROVIDED:
                new_tile.nodegroup_id = grouping_node.nodegroup_id
                new_tile.resourceinstance_id = self.resourceid
                new_tile.sortorder = next_sort_order
                next_sort_order += 1
                for node in grouping_node.nodegroup.node_set.all():
                    if node.datatype != "semantic":
                        new_tile.data[str(node.pk)] = new_tile.get_default_value(node)
                new_tile._incoming_tile = new_tile
                if isinstance(container, TileModel):
                    new_tile.parenttile = container
                new_tile.full_clean()
                to_insert.add(new_tile)
            else:
                original_tile_data_by_tile_id[existing_tile.pk] = {**existing_tile.data}
                existing_tile._incoming_tile = new_tile
                to_update.add(existing_tile)

        nodes = grouping_node.nodegroup.node_set.all()
        for tile in to_insert | to_update:
            # arches_version==9.0.0
            if arches_version >= (8, 0):
                children = tile.nodegroup.children.all()
            else:
                children = tile.nodegroup.nodegroup_set.all()
            for child_nodegroup in children:
                self._update_tile(
                    grouping_node=self.grouping_nodes_by_nodegroup_id[
                        child_nodegroup.pk
                    ],
                    container=tile._incoming_tile,
                    original_tile_data_by_tile_id=original_tile_data_by_tile_id,
                    delete_siblings=delete_siblings,
                )
            self._validate_and_patch_incoming_values(tile, nodes=nodes)
            tile.set_missing_keys_to_none()

        for tile in to_insert | to_update:
            # Remove no-op upserts.
            if (
                original_data := original_tile_data_by_tile_id.pop(tile.pk, None)
            ) and tile._tile_update_is_noop(original_data):
                to_update.remove(tile)

        self.to_insert |= to_insert
        self.to_update |= to_update
        self.to_delete |= to_delete

    def _extract_incoming_tiles(self, container, grouping_node):
        from arches_querysets.models import TileTree

        if container is None:
            aliased_data = self.entry.aliased_data
        elif isinstance(container, dict):
            aliased_data = container.get("aliased_data")
        else:
            aliased_data = container.aliased_data

        if container is None:
            new_tiles = [self.entry]
        elif isinstance(aliased_data, dict):
            new_tiles = aliased_data.get(grouping_node.alias, NOT_PROVIDED)
        else:
            new_tiles = getattr(aliased_data, grouping_node.alias, NOT_PROVIDED)
        if new_tiles is NOT_PROVIDED:
            raise KeyError(grouping_node.alias)

        if grouping_node.nodegroup.cardinality == "1":
            if new_tiles is None:
                new_tiles = []
            elif not isinstance(new_tiles, list):
                new_tiles = [new_tiles]
        if all(isinstance(tile, TileTree) for tile in new_tiles):
            new_tiles.sort(key=attrgetter("sortorder"))
        else:
            parent_tile = container if isinstance(container, TileTree) else None
            new_tiles = [
                TileTree.deserialize(tile_dict, parent_tile=parent_tile)
                for tile_dict in new_tiles
            ]
        return new_tiles

    def _pair_tiles(self, existing_tiles, new_tiles):
        pairs = []
        matched_new_tiles = []
        for existing_tile in existing_tiles:
            for tile in new_tiles:
                if existing_tile.pk == tile.pk:
                    pairs.append((existing_tile, tile))
                    matched_new_tiles.append(tile)
                    break
            else:
                pairs.append((existing_tile, NOT_PROVIDED))
        for new_tile in new_tiles:
            if new_tile not in matched_new_tiles:
                pairs.append((NOT_PROVIDED, new_tile))
        return pairs

    def _validate_and_patch_incoming_values(self, tile, *, nodes):
        """Validate data found on tile._incoming_tile and move it to tile.data.
        Update errors_by_node_alias in place."""
        from arches_querysets.models import AliasedData, TileTree

        for node in nodes:
            if node.datatype == "semantic":
                continue
            if isinstance(tile._incoming_tile, TileTree) and isinstance(
                tile._incoming_tile.aliased_data, AliasedData
            ):
                value_to_validate = getattr(
                    tile._incoming_tile.aliased_data, node.alias, NOT_PROVIDED
                )
            else:
                value_to_validate = tile._incoming_tile.aliased_data.get(
                    node.alias, NOT_PROVIDED
                )
            if value_to_validate is NOT_PROVIDED:
                if self.partial:
                    continue
                value_to_validate = TileTree.get_default_value(node)
                tile._incoming_tile.set_aliased_data(node, value_to_validate)
            if isinstance(value_to_validate, dict):
                value_to_validate = value_to_validate.get(
                    "node_value", value_to_validate
                )

            self._run_datatype_methods(tile, value_to_validate, node)

    def _run_datatype_methods(self, tile, value_to_validate, node):
        """
        Call datatype methods when merging value_to_validate into the tile.

        1. transform_value_for_tile() -- type coercion
        2. pre_structure_tile_data() -- insert missing dictionary keys
        3. clean() -- replace empty values
        4. validate() -- check business logic, don't mutate data
        5. pre_tile_save() -- run side effects

        TODO: move this to BaseDataType.full_clean()?
        https://github.com/archesproject/arches/issues/10851#issuecomment-2427305853
        """
        node_id_str = str(node.pk)
        datatype_instance = self.datatype_factory.get_instance(node.datatype)

        if value_to_validate is None:
            tile.data[node_id_str] = None
            return
        try:
            transformed = datatype_instance.transform_value_for_tile(
                value_to_validate,
                languages=self.languages,
                is_existing_tile=bool(tile._state.db),
                **node.config,
            )
        except ValueError:  # BooleanDataType raises.
            # validate() will handle.
            transformed = value_to_validate

        # Merge the incoming value.
        tile.data[node_id_str] = transformed

        datatype_instance.pre_structure_tile_data(
            tile, node_id_str, languages=self.languages
        )

        datatype_instance.clean(tile, node_id_str)

        if errors := datatype_instance.validate(
            transformed, node=node, request=self.request
        ):
            self.errors_by_node_alias[node.alias].extend(errors)

        try:
            datatype_instance.pre_tile_save(tile, node_id_str)
        except TypeError:  # GeoJSONDataType raises.
            self.errors_by_node_alias[node.alias].append(
                datatype_instance.create_error_message(
                    tile.data[node_id_str], None, None, None
                )
            )

    def _save(self):
        # Instantiate proxy models for now, but TODO: expose this
        # functionality on vanilla models, and in bulk.
        tile_model_fields = Tile._meta.get_fields()
        upserts = self.to_insert | self.to_update
        insert_proxies = [
            # Instantiate TileProxyModel instances without aliased data.
            Tile(**(pop_arches_model_kwargs(vars(insert), tile_model_fields)[1]))
            for insert in self.to_insert
        ]
        update_proxies = list(
            Tile.objects.filter(pk__in=[tile.pk for tile in self.to_update])
            .select_related("resourceinstance__graph")
            .prefetch_related("nodegroup__cardmodel_set")
        )
        upsert_proxies = insert_proxies + update_proxies
        delete_proxies = Tile.objects.filter(
            pk__in=[tile.pk for tile in self.to_delete]
        )

        # durable=True is a guard against any higher-level code trying to wrap in
        # another transaction. Ideally durable=True would be removed, and any
        # IntegrityErrors would not be ignored in after_update_all(), but we have
        # some Arches projects that test with "incomplete" datasets with data
        # integrity issues, so we can't do the natural thing (yet).
        with transaction.atomic(durable=True):
            if isinstance(self.entry, ResourceInstance):
                super(ResourceInstance, self.entry).save(**self.save_kwargs)
            # no else: if the entry point needs saving, it's already in
            # self.to_update or self.to_insert

            # Interact with the database in bulk as much as possible, but
            # run certain side effects from Tile.save() one-at-a-time until
            # proxy model methods can be refactored. Then run in bulk.
            for upsert_proxy, vanilla_instance in zip(
                sorted(upsert_proxies, key=attrgetter("pk")),
                sorted(upserts, key=attrgetter("pk")),
                strict=True,
            ):
                upsert_proxy._existing_data = upsert_proxy.data
                upsert_proxy._existing_provisionaledits = upsert_proxy.provisionaledits

                # Sync proxy instance fields.
                for field in field_attnames(vanilla_instance):
                    setattr(upsert_proxy, field, getattr(vanilla_instance, field))

                # Some functions expect to always drill into request.user
                # https://github.com/archesproject/arches/issues/8471
                try:
                    upsert_proxy._Tile__preSave(request=self.request)
                    upsert_proxy.check_for_missing_nodes()  # also runs clean()
                    upsert_proxy.check_for_constraint_violation()
                except TileValidationError as error:
                    if ":" in error.message:
                        self.parse_required_error(error)
                    raise ValidationError(error.message) from error
                (
                    oldprovisionalvalue,
                    newprovisionalvalue,
                    provisional_edit_log_details,
                ) = vanilla_instance._apply_provisional_edit(
                    upsert_proxy,
                    upsert_proxy._existing_data,
                    upsert_proxy._existing_provisionaledits,
                    user=self.request.user,
                )
                # Remember the values needed for the edit log updates later.
                upsert_proxy._oldprovisionalvalue = oldprovisionalvalue
                upsert_proxy._newprovisionalvalue = newprovisionalvalue
                upsert_proxy._provisional_edit_log_details = (
                    provisional_edit_log_details
                )
                upsert_proxy._existing_data = vanilla_instance.data

            for delete_proxy in delete_proxies:
                delete_proxy._Tile__preDelete(request=self.request)

            if self.to_insert:
                inserted = sorted(
                    TileModel.objects.bulk_create(self.to_insert), key=attrgetter("pk")
                )
                # Pay the cost of a second TileModel -> Tile transform until refactored.
                refreshed_insert_proxies = list(
                    Tile.objects.filter(pk__in=[t.pk for t in inserted]).order_by("pk")
                )
                for before, after in zip(
                    insert_proxies, refreshed_insert_proxies, strict=True
                ):
                    after._newprovisionalvalue = before._newprovisionalvalue
                    after._provisional_edit_log_details = (
                        before._provisional_edit_log_details
                    )
                upsert_proxies = refreshed_insert_proxies + update_proxies
            else:
                insert_proxies = Tile.objects.none()
            if self.to_update:
                TileModel.objects.bulk_update(
                    self.to_update,
                    # No updates to resource instance or nodegroup.
                    {"data", "parenttile", "provisionaledits", "sortorder"},
                )
            if self.to_delete:
                TileModel.objects.filter(pk__in=[t.pk for t in self.to_delete]).delete()

            for upsert_tile in upserts:
                grouping_node = self.grouping_nodes_by_nodegroup_id[
                    upsert_tile.nodegroup_id
                ]
                for node in grouping_node.nodegroup.node_set.all():
                    datatype = self.datatype_factory.get_instance(node.datatype)
                    datatype.post_tile_save(
                        upsert_tile, str(node.pk), request=self.request
                    )

            for upsert_proxy in upsert_proxies:
                upsert_proxy._Tile__postSave()

            # Save edits: could be done in bulk once above side effects are un-proxied.
            for insert_proxy in insert_proxies:
                insert_proxy.save_edit(
                    user=self.request.user,
                    edit_type="tile create",
                    old_value={},
                    new_value=insert_proxy.data,
                    newprovisionalvalue=insert_proxy._newprovisionalvalue,
                    provisional_edit_log_details=insert_proxy._provisional_edit_log_details,
                    transaction_id=self.transaction_id,
                    new_resource_created=self.new_resource_created,
                    note=None,
                )
            for update_proxy in update_proxies:
                update_proxy.save_edit(
                    user=self.request.user,
                    edit_type="tile edit",
                    old_value=update_proxy._existing_data,
                    new_value=update_proxy.data,
                    newprovisionalvalue=update_proxy._newprovisionalvalue,
                    oldprovisionalvalue=update_proxy._oldprovisionalvalue,
                    provisional_edit_log_details=update_proxy._provisional_edit_log_details,
                    transaction_id=self.transaction_id,
                )
            for delete_proxy in delete_proxies:
                delete_proxy.save_edit(
                    user=self.request.user,
                    edit_type="tile delete",
                    old_value=delete_proxy.data,
                    provisional_edit_log_details=None,
                    transaction_id=self.transaction_id,
                )

    def after_update_all(self):
        for datatype in self.datatype_factory.datatype_instances.values():
            try:
                datatype.after_update_all()
            except:
                # This wide catch can leave the DB in an unusable state, so not only is
                # this the *last* operation, but durable=True on the transaction.
                # https://github.com/archesproject/arches/issues/12318
                logger.error(
                    f"Error in {datatype.__class__.__name__}.after_update_all():",
                    exc_info=True,
                )
                continue

    def parse_required_error(self, error):
        """
        This is a make-do attempt to parse the TileValidationError,
        which should raise something more discrete than a localized
        "This card requires values for the following: "
        Some translations of that string do not include whitespace
        after the colon, so be sure to only strip the space, not split.
        """
        error_names = [name.strip() for name in error.message.split(":")[1].split(", ")]
        aliases = []

        from arches_querysets.models import TileTree

        if isinstance(self.entry, TileTree):
            nodes = self.entry.resourceinstance.graph.node_set.all()
        else:
            nodes = self.entry.graph.node_set.all()
        for widget_label_or_node_name in error_names:
            widget = CardXNodeXWidget.objects.filter(
                node__in=nodes,
                # Awkward due to I18n_JSON
                label__contains={get_language(): widget_label_or_node_name},
            ).first()
            if widget:
                node = widget.node
            else:
                node = Node.objects.filter(
                    pk__in=nodes,
                    name=widget_label_or_node_name,
                ).first()
            if node:
                aliases.append(node.alias)
            else:
                msg = "Unable to backsolve error name: %s"
                logger.error(msg, widget_label_or_node_name)
                raise ValidationError(error.message) from error
        raise ValidationError({alias: error.message for alias in aliases}) from error
