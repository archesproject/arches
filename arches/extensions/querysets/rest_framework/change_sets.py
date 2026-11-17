"""Server-side resource change sets: validate, detect conflicts, rebase, apply.

Operates on the JSON-normalized resource representation (the GET shape).
Semantics follow arches-modular-reports' resource-change-set.ts.
"""

import copy
import uuid
from dataclasses import dataclass, field

from django.utils.translation import gettext as _
from rest_framework.exceptions import PermissionDenied, ValidationError

from arches.app.models.models import TileModel

EDIT = "edit"
ADD = "add"
DELETE = "delete"
REORDER = "reorder"
CHANGE_TYPES = (EDIT, ADD, DELETE, REORDER)

MODIFIED = "modified"
DELETED = "deleted"
PARENT_DELETED = "parent_deleted"
SLOT_TAKEN = "slot_taken"


def _invalid(message):
    return ValidationError({"changes": [message]})


def _uuid_str(value, label):
    try:
        return str(uuid.UUID(str(value)))
    except (TypeError, ValueError, AttributeError):
        raise _invalid(_("%(label)s must be a UUID.") % {"label": label})


def _optional_uuid_str(value, label):
    return None if value is None else _uuid_str(value, label)


def parse_changes(data):
    """Validate the request payload shape and normalize UUIDs."""
    if not isinstance(data, dict) or not isinstance(data.get("changes"), list):
        raise _invalid(_("Expected an object with a 'changes' list."))

    parsed = []
    for raw in data["changes"]:
        if not isinstance(raw, dict):
            raise _invalid(_("Each change must be an object."))
        change_type = raw.get("type")
        if change_type not in CHANGE_TYPES:
            raise _invalid(
                _("Unknown change type: %(type)s") % {"type": str(change_type)}
            )
        change_id = raw.get("id")
        nodegroup_alias = raw.get("nodegroupAlias")
        if not isinstance(change_id, str) or not change_id:
            raise _invalid(_("Each change requires an 'id'."))
        if not isinstance(nodegroup_alias, str) or not nodegroup_alias:
            raise _invalid(_("Each change requires a 'nodegroupAlias'."))
        change = {
            "id": change_id,
            "type": change_type,
            "nodegroupAlias": nodegroup_alias,
        }

        if change_type in (EDIT, DELETE):
            change["tileId"] = _uuid_str(raw.get("tileId"), "tileId")
        if change_type in (ADD, REORDER):
            change["parentTileId"] = _optional_uuid_str(
                raw.get("parentTileId"), "parentTileId"
            )

        if change_type == EDIT:
            aliased_data = raw.get("aliasedData")
            original = raw.get("original")
            if not isinstance(aliased_data, dict) or not aliased_data:
                raise _invalid(_("An edit requires 'aliasedData'."))
            if not isinstance(original, dict):
                raise _invalid(_("An edit requires 'original'."))
            for node_alias, node_data in aliased_data.items():
                if not isinstance(node_data, dict) or "node_value" not in node_data:
                    raise _invalid(
                        _("Edited node %(alias)s requires a 'node_value'.")
                        % {"alias": node_alias}
                    )
                if node_alias not in original:
                    raise _invalid(
                        _("'original' is missing edited node %(alias)s.")
                        % {"alias": node_alias}
                    )
            change["aliasedData"] = aliased_data
            change["original"] = original
        elif change_type == ADD:
            tile = raw.get("tile")
            if not isinstance(tile, dict) or not isinstance(
                tile.get("aliased_data"), dict
            ):
                raise _invalid(_("An add requires a 'tile' with 'aliased_data'."))
            tile = copy.deepcopy(tile)
            tile["tileid"] = _uuid_str(tile.get("tileid"), "tile.tileid")
            change["tile"] = tile
        elif change_type == REORDER:
            tile_ids = raw.get("tileIds")
            if not isinstance(tile_ids, list):
                raise _invalid(_("A reorder requires a 'tileIds' list."))
            change["tileIds"] = [_uuid_str(tile_id, "tileIds") for tile_id in tile_ids]
        parsed.append(change)
    return parsed


def _is_tile(value):
    # Node data ({node_value, ...}) has no tileid key; blank tiles have tileid None.
    return isinstance(value, dict) and "tileid" in value


def _tiles(value):
    if isinstance(value, list):
        return [tile for tile in value if _is_tile(tile)]
    if _is_tile(value):
        return [value]
    return []


def _node_value(node_data):
    if isinstance(node_data, dict):
        return node_data.get("node_value")
    return None


@dataclass
class _TileInfo:
    tile: dict
    nodegroup_alias: str
    parent_tile_id: str | None


@dataclass
class _GraphInfo:
    nodegroup_by_alias: dict = field(default_factory=dict)
    alias_by_nodegroup_id: dict = field(default_factory=dict)
    node_aliases_by_nodegroup_id: dict = field(default_factory=dict)

    @classmethod
    def from_nodes(cls, graph_nodes):
        info = cls()
        for node in graph_nodes:
            if not node.nodegroup_id or not node.alias:
                continue
            nodegroup_id = str(node.nodegroup_id)
            if str(node.pk) == nodegroup_id:
                info.nodegroup_by_alias[node.alias] = node.nodegroup
                info.alias_by_nodegroup_id[nodegroup_id] = node.alias
                if node.datatype == "semantic":
                    continue
            # Data-bearing root nodes are also nodes of their own nodegroup.
            info.node_aliases_by_nodegroup_id.setdefault(nodegroup_id, set()).add(
                node.alias
            )
        return info

    def parent_alias(self, nodegroup_alias):
        parent_id = self.nodegroup_by_alias[nodegroup_alias].parentnodegroup_id
        return self.alias_by_nodegroup_id.get(str(parent_id)) if parent_id else None

    def is_child(self, key, container_alias):
        """Whether `key` holds tiles of a nodegroup nested in `container_alias`
        (None = resource top level) rather than node data."""
        return (
            key in self.nodegroup_by_alias and self.parent_alias(key) == container_alias
        )

    def is_cardinality_n(self, nodegroup_alias):
        return self.nodegroup_by_alias[nodegroup_alias].cardinality == "n"

    def node_aliases(self, nodegroup_alias):
        nodegroup_id = str(self.nodegroup_by_alias[nodegroup_alias].pk)
        return self.node_aliases_by_nodegroup_id.get(nodegroup_id, set())


class ResourceChangeSet:
    def __init__(self, changes, representation, *, graph_nodes, resource_id, user):
        self.changes = changes
        self.representation = representation
        self.graph = _GraphInfo.from_nodes(graph_nodes)
        self.resource_id = str(resource_id)
        self.user = user
        self.tiles_by_id = {}
        self._index(representation.get("aliased_data") or {}, None, None)

    def _index(self, aliased_data, container_alias, parent_tile_id):
        for alias, value in aliased_data.items():
            if not self.graph.is_child(alias, container_alias):
                continue
            for tile in _tiles(value):
                if tile_id := tile.get("tileid"):
                    self.tiles_by_id[str(tile_id)] = _TileInfo(
                        tile, alias, parent_tile_id
                    )
                    self._index(tile.get("aliased_data") or {}, alias, str(tile_id))

    # Validation & permissions

    def validate(self):
        """Reject changes that reference other graphs/resources or forbidden nodegroups."""
        editable = self.user.userprofile.editable_nodegroups
        deletable = self.user.userprofile.deletable_nodegroups
        added_tiles = {}  # tileid -> nodegroup alias, including nested tiles
        touched_for_edit = set()
        touched_for_delete = set()

        for change in self.changes:
            alias = change["nodegroupAlias"]
            self._check_nodegroup_alias(alias)
            if change["type"] == DELETE:
                touched_for_delete.add(alias)
            else:
                touched_for_edit.add(alias)

            if change["type"] == EDIT:
                unknown = set(change["aliasedData"]) - self.graph.node_aliases(alias)
                if unknown:
                    raise _invalid(
                        _("%(node)s is not a node of %(nodegroup)s.")
                        % {"node": sorted(unknown)[0], "nodegroup": alias}
                    )
            if change["type"] in (EDIT, DELETE):
                self._check_tile_nodegroup(change["tileId"], alias, added_tiles)
            if change["type"] in (ADD, REORDER):
                self._check_parent(change["parentTileId"], alias, added_tiles)
            if change["type"] == ADD:
                tile = change["tile"]
                if (info := self.tiles_by_id.get(tile["tileid"])) and (
                    info.nodegroup_alias != alias
                ):
                    raise _invalid(
                        _("Tile does not belong to %(nodegroup)s.")
                        % {"nodegroup": alias}
                    )
                self._prepare_added_tile(
                    tile, alias, change["parentTileId"], added_tiles, touched_for_edit
                )
            if change["type"] == REORDER:
                for tile_id in change["tileIds"]:
                    info = self.tiles_by_id.get(tile_id)
                    if info and (
                        info.nodegroup_alias != alias
                        or info.parent_tile_id != change["parentTileId"]
                    ):
                        raise _invalid(_("Reordered tiles must be siblings."))

        self._check_unknown_tile_ids(added_tiles)

        for alias in touched_for_edit | touched_for_delete:
            nodegroup_id = str(self.graph.nodegroup_by_alias[alias].pk)
            allowed = nodegroup_id in editable
            if alias in touched_for_delete:
                allowed = allowed and nodegroup_id in deletable
            if not allowed:
                raise PermissionDenied(
                    _("You do not have permission to change %(nodegroup)s.")
                    % {"nodegroup": alias}
                )

    def _check_nodegroup_alias(self, alias):
        if alias not in self.graph.nodegroup_by_alias:
            raise _invalid(
                _("%(nodegroup)s is not a nodegroup of this graph.")
                % {"nodegroup": alias}
            )

    def _check_tile_nodegroup(self, tile_id, alias, added_tiles):
        if info := self.tiles_by_id.get(tile_id):
            actual = info.nodegroup_alias
        else:
            actual = added_tiles.get(tile_id, alias)
        if actual != alias:
            raise _invalid(
                _("Tile does not belong to %(nodegroup)s.") % {"nodegroup": alias}
            )

    def _check_parent(self, parent_tile_id, alias, added_tiles):
        expected_parent_alias = self.graph.parent_alias(alias)
        if parent_tile_id is None:
            if expected_parent_alias is not None:
                raise _invalid(
                    _("%(nodegroup)s requires a parent tile.") % {"nodegroup": alias}
                )
            return
        if expected_parent_alias is None:
            raise _invalid(
                _("%(nodegroup)s cannot have a parent tile.") % {"nodegroup": alias}
            )
        if info := self.tiles_by_id.get(parent_tile_id):
            parent_alias = info.nodegroup_alias
        else:
            parent_alias = added_tiles.get(parent_tile_id, expected_parent_alias)
        if parent_alias != expected_parent_alias:
            raise _invalid(
                _("Parent tile does not belong to %(nodegroup)s.")
                % {"nodegroup": expected_parent_alias}
            )

    def _prepare_added_tile(self, tile, alias, parent_tile_id, added_tiles, touched):
        """Validate an added tile's tree and pin its identifying fields."""
        tile["tileid"] = _uuid_str(tile.get("tileid") or uuid.uuid4(), "tileid")
        tile["resourceinstance"] = self.resource_id
        tile["nodegroup"] = str(self.graph.nodegroup_by_alias[alias].pk)
        # Unsaved parents can't be referenced yet; nesting conveys the relationship.
        tile["parenttile"] = (
            parent_tile_id if parent_tile_id in self.tiles_by_id else None
        )
        added_tiles[tile["tileid"]] = alias
        touched.add(alias)

        aliased_data = tile.get("aliased_data")
        if not isinstance(aliased_data, dict):
            raise _invalid(_("Tiles require 'aliased_data'."))
        node_aliases = self.graph.node_aliases(alias)
        for key, value in aliased_data.items():
            if key in node_aliases:
                continue
            if self.graph.is_child(key, alias):
                children = value if isinstance(value, list) else [value]
                for child in children:
                    if child is None:
                        continue
                    if not isinstance(child, dict):
                        raise _invalid(_("Tiles must be objects."))
                    if str(child.get("tileid")) in self.tiles_by_id:
                        raise _invalid(_("Added tiles cannot contain existing tiles."))
                    self._prepare_added_tile(
                        child, key, tile["tileid"], added_tiles, touched
                    )
                continue
            raise _invalid(
                _("%(key)s is not part of %(nodegroup)s.")
                % {"key": key, "nodegroup": alias}
            )

    def _check_unknown_tile_ids(self, added_tiles):
        referenced = set(added_tiles)
        for change in self.changes:
            referenced.update(
                tile_id
                for tile_id in (
                    change.get("tileId"),
                    change.get("parentTileId"),
                    *change.get("tileIds", []),
                )
                if tile_id
            )
        unknown = referenced - set(self.tiles_by_id)
        if not unknown:
            return
        for tile_id, resource_id in TileModel.objects.filter(
            pk__in=unknown
        ).values_list("pk", "resourceinstance_id"):
            if str(resource_id) != self.resource_id:
                raise _invalid(
                    _("Tile %(tile)s belongs to another resource.") % {"tile": tile_id}
                )
            # Exists on this resource but isn't readable by this user.
            raise PermissionDenied(
                _("You do not have permission to change tile %(tile)s.")
                % {"tile": tile_id}
            )

    # Conflicts

    def find_conflicts(self):
        conflicts = []
        added_so_far = set()
        deleted_so_far = set()
        for change in self.changes:
            if conflict := self._conflict_for(change, added_so_far, deleted_so_far):
                conflicts.append(conflict)
            if change["type"] == ADD:
                added_so_far.add(change["tile"]["tileid"])
            elif change["type"] == DELETE:
                deleted_so_far.add(change["tileId"])
        return conflicts

    def _conflict_for(self, change, added_so_far, deleted_so_far):
        base = {"changeId": change["id"], "nodegroupAlias": change["nodegroupAlias"]}
        if change["type"] in (ADD, REORDER):
            parent_tile_id = change["parentTileId"]
            if (
                parent_tile_id is not None
                and parent_tile_id not in self.tiles_by_id
                and parent_tile_id not in added_so_far
            ):
                return {
                    **base,
                    "reason": PARENT_DELETED,
                    "parentTileId": parent_tile_id,
                }
            if change["type"] == ADD and self._fills_taken_slot(change, deleted_so_far):
                return {
                    **base,
                    "reason": SLOT_TAKEN,
                    "tileId": change["tile"]["tileid"],
                }
            return None
        if change["type"] == DELETE:
            return None

        tile_id = change["tileId"]
        info = self.tiles_by_id.get(tile_id)
        if info is None:
            if tile_id in added_so_far:
                return None
            return {**base, "reason": DELETED, "tileId": tile_id}
        nodes = {}
        for node_alias, node_data in change["aliasedData"].items():
            current_data = info.tile.get("aliased_data", {}).get(node_alias)
            current = _node_value(current_data)
            original = change["original"][node_alias]
            if current != original and current != node_data["node_value"]:
                nodes[node_alias] = {
                    "current": current,
                    "currentDisplay": (
                        current_data.get("display_value")
                        if isinstance(current_data, dict)
                        else None
                    ),
                    "original": original,
                }
        if nodes:
            return {**base, "reason": MODIFIED, "tileId": tile_id, "nodes": nodes}
        return None

    def _fills_taken_slot(self, change, deleted_so_far):
        alias = change["nodegroupAlias"]
        if self.graph.is_cardinality_n(alias):
            return False
        parent_tile_id = change["parentTileId"]
        if parent_tile_id is None:
            container = self.representation.get("aliased_data") or {}
        elif info := self.tiles_by_id.get(parent_tile_id):
            container = info.tile.get("aliased_data") or {}
        else:
            return False
        occupant = container.get(alias)
        if not isinstance(occupant, dict) or not occupant.get("tileid"):
            return False
        occupant_id = str(occupant["tileid"])
        # Replacing a tile deleted earlier in this change set is fine.
        return occupant_id != change["tile"]["tileid"] and (
            occupant_id not in deleted_so_far
        )

    # Rebase & apply

    def rebase(self):
        rebased = []
        for change in self.changes:
            if change["type"] == ADD and change["tile"]["tileid"] in self.tiles_by_id:
                tile = change["tile"]
                node_aliases = self.graph.node_aliases(change["nodegroupAlias"])
                change = {
                    "id": change["id"],
                    "type": EDIT,
                    "nodegroupAlias": change["nodegroupAlias"],
                    "tileId": tile["tileid"],
                    "aliasedData": {
                        key: value
                        for key, value in tile["aliased_data"].items()
                        if key in node_aliases and isinstance(value, dict)
                    },
                }
            if change["type"] == EDIT:
                change = self._with_changed_nodes_only(change)
            if change is not None:
                rebased.append(change)
        return [
            change
            for change in rebased
            if change["type"] != REORDER
            or not self._keeps_current_order(change, rebased)
        ]

    def _with_changed_nodes_only(self, change):
        info = self.tiles_by_id.get(change["tileId"])
        if info is None:
            return change
        server_data = info.tile.get("aliased_data") or {}
        changed = {
            node_alias: node_data
            for node_alias, node_data in change["aliasedData"].items()
            if not isinstance(server_data.get(node_alias), dict)
            or node_data.get("node_value") != _node_value(server_data[node_alias])
        }
        if not changed:
            return None
        return {**change, "aliasedData": changed}

    def _keeps_current_order(self, reorder, changes):
        others = [change for change in changes if change is not reorder]
        working = self._apply_to_aliased_data(
            copy.deepcopy(self.representation.get("aliased_data") or {}),
            None,
            None,
            others,
            remove_deleted=False,
        )
        if reorder["parentTileId"] is None:
            siblings = _tiles(working.get(reorder["nodegroupAlias"]))
        else:
            parent = self._find_tile(working, None, reorder["parentTileId"])
            siblings = _tiles(
                (parent or {}).get("aliased_data", {}).get(reorder["nodegroupAlias"])
            )
        return [str(tile.get("tileid")) for tile in siblings] == reorder["tileIds"]

    def apply(self):
        """Return the representation with the rebased changes applied."""
        updated = copy.deepcopy(self.representation)
        updated["aliased_data"] = self._apply_to_aliased_data(
            updated.get("aliased_data") or {},
            None,
            None,
            self.rebase(),
            remove_deleted=True,
        )
        return updated

    def _apply_to_aliased_data(
        self, aliased_data, container_alias, parent_tile_id, changes, *, remove_deleted
    ):
        added = {}
        orders = {}
        for change in changes:
            if change["type"] == ADD and change["parentTileId"] == parent_tile_id:
                added.setdefault(change["nodegroupAlias"], []).append(
                    copy.deepcopy(change["tile"])
                )
            if change["type"] == REORDER and change["parentTileId"] == parent_tile_id:
                orders[change["nodegroupAlias"]] = change["tileIds"]
        deleted = {change["tileId"] for change in changes if change["type"] == DELETE}

        for alias in [*aliased_data, *(a for a in added if a not in aliased_data)]:
            if not self.graph.is_child(alias, container_alias):
                continue
            tiles = _tiles(aliased_data.get(alias))
            if remove_deleted:
                tiles = [t for t in tiles if str(t.get("tileid")) not in deleted]
            tiles = [
                self._apply_to_tile(tile, alias, changes, remove_deleted=remove_deleted)
                for tile in [*tiles, *added.get(alias, [])]
            ]
            tiles = _reorder(tiles, orders.get(alias))
            if self.graph.is_cardinality_n(alias):
                aliased_data[alias] = tiles
            else:
                aliased_data[alias] = tiles[0] if tiles else None
        return aliased_data

    def _apply_to_tile(self, tile, alias, changes, *, remove_deleted):
        tile_id = str(tile.get("tileid"))
        aliased_data = tile.setdefault("aliased_data", {})
        for change in changes:
            if change["type"] == EDIT and change["tileId"] == tile_id:
                aliased_data.update(copy.deepcopy(change["aliasedData"]))
                break
        self._apply_to_aliased_data(
            aliased_data, alias, tile_id, changes, remove_deleted=remove_deleted
        )
        return tile

    def _find_tile(self, aliased_data, container_alias, tile_id):
        for alias, value in aliased_data.items():
            if not self.graph.is_child(alias, container_alias):
                continue
            for tile in _tiles(value):
                if str(tile.get("tileid")) == tile_id:
                    return tile
                if found := self._find_tile(
                    tile.get("aliased_data") or {}, alias, tile_id
                ):
                    return found
        return None


def _reorder(tiles, ordered_tile_ids):
    if ordered_tile_ids is None:
        return tiles
    positions = {tile_id: position for position, tile_id in enumerate(ordered_tile_ids)}
    for tile in tiles:
        position = positions.get(str(tile.get("tileid")))
        if position is not None:
            tile["sortorder"] = position
    return sorted(tiles, key=lambda tile: tile.get("sortorder") or 0)
