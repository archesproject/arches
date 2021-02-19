"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import uuid
import importlib
import datetime
import json
import pytz
import logging
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.resource import EditLog
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.permission_backend import user_is_resource_reviewer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Bool, Terms
from arches.app.search.mappings import TERMS_INDEX
from arches.app.datatypes.datatypes import DataTypeFactory

logger = logging.getLogger(__name__)


class Tile(models.TileModel):
    """
    Used for mapping complete tile object to and from the database

    """

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        """
        Init a Tile from a dictionary representation of from a model method call

        init this object by using Django query syntax, eg:
        .. code-block:: python

            Tile.objects.get(pk=some_tile_id)
            # or
            Tile.objects.filter(name=some_value_to_filter_by)

        OR, init this object with a dictionary, eg:
        .. code-block:: python

            Tile({
                name:'some name',
                tileid: '12341234-1234-1234-1324-1234123433433',
                ...
            })

        Arguments:
        args -- a dictionary of properties repsenting a Tile object
        kwargs -- unused

        """

        super(Tile, self).__init__(*args, **kwargs)
        # from models.TileModel
        # self.tileid
        # self.resourceinstance
        # self.parenttile
        # self.data
        # self.nodegroup
        # self.sortorder
        # end from models.TileModel
        self.tiles = []
        self.datatype_factory = DataTypeFactory()

        if args:
            if isinstance(args[0], dict):
                for key, value in args[0].items():
                    if not (key == "tiles"):
                        setattr(self, key, value)

                if self.tileid is None or self.tileid == "":
                    self.tileid = uuid.uuid4()

                if "tiles" in args[0]:
                    for tile_obj in args[0]["tiles"]:
                        tile = Tile(tile_obj)
                        tile.parenttile = self
                        self.tiles.append(tile)

    def save_edit(
        self,
        user={},
        note="",
        edit_type="",
        old_value=None,
        new_value=None,
        newprovisionalvalue=None,
        oldprovisionalvalue=None,
        provisional_edit_log_details=None,
    ):
        timestamp = datetime.datetime.now()
        edit = EditLog()
        edit.resourceclassid = self.resourceinstance.graph_id
        edit.resourceinstanceid = self.resourceinstance.resourceinstanceid
        edit.nodegroupid = self.nodegroup_id
        edit.tileinstanceid = self.tileid
        if provisional_edit_log_details is not None:
            edit.provisional_user_username = getattr(provisional_edit_log_details["provisional_editor"], "username", "")
            edit.provisional_userid = getattr(provisional_edit_log_details["provisional_editor"], "id", "")
            edit.provisional_edittype = provisional_edit_log_details["action"]
            user = provisional_edit_log_details["user"]
        edit.userid = getattr(user, "id", "")
        edit.user_email = getattr(user, "email", "")
        edit.user_firstname = getattr(user, "first_name", "")
        edit.user_lastname = getattr(user, "last_name", "")
        edit.user_username = getattr(user, "username", "")
        edit.resourcedisplayname = Resource.objects.get(resourceinstanceid=self.resourceinstance.resourceinstanceid).displayname
        edit.oldvalue = old_value
        edit.newvalue = new_value
        edit.timestamp = timestamp
        edit.edittype = edit_type
        edit.newprovisionalvalue = newprovisionalvalue
        edit.oldprovisionalvalue = oldprovisionalvalue
        edit.save()

    def tile_collects_data(self):
        result = True
        if self.tiles is not None and len(self.tiles) > 0:
            nodes = models.Node.objects.filter(nodegroup=self.nodegroup)
            if len(nodes) == 1 and nodes[0].datatype == "semantic":
                result = False
        return result

    def apply_provisional_edit(self, user, data, action="create", status="review", existing_model=None):
        """
        Creates or updates the json stored in a tile's provisionaledits db_column

        """
        if self.tile_collects_data() is True and data != {}:

            utc_date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
            timestamp_utc = str(datetime.datetime.now(pytz.utc).strftime(utc_date_format))

            provisionaledit = {
                "value": data,
                "status": status,
                "action": action,
                "reviewer": None,
                "timestamp": timestamp_utc,
                "reviewtimestamp": None,
            }

            # if this tile has been previously saved and already has provisional edits on it then
            if existing_model is not None and existing_model.provisionaledits is not None:
                provisionaledits = existing_model.provisionaledits
                provisionaledits[str(user.id)] = provisionaledit
            else:
                # this is a new tile so there is no provisional edits object on the tile
                provisionaledits = {str(user.id): provisionaledit}
            self.provisionaledits = provisionaledits

    def is_provisional(self):
        """
        Returns True if a tile has been created as provisional and has not yet
        been approved by a user in the resource reviewer group

        """

        result = False
        if self.provisionaledits is not None and len(self.data) == 0:
            result = True

        return result

    def user_owns_provisional(self, user):
        """
        Returns True if a user was the creator of a provisional tile that has not
        yet been approved. This is used to confirm whether a provisional user
        is allowed to edit and delete their provisional data.

        """
        if self.provisionaledits is None:
            return False
        else:
            return str(user.id) in self.provisionaledits

    def get_provisional_edit(self, tile, user):
        edit = None
        if tile.provisionaledits is not None:
            edits = tile.provisionaledits
            if str(user.id) in edits:
                edit = edits[str(user.id)]
        return edit

    def check_tile_cardinality_violation(self):
        if settings.BYPASS_CARDINALITY_TILE_VALIDATION:
            return
        if self.nodegroup.cardinality == "1":
            kwargs = {"nodegroup": self.nodegroup, "resourceinstance_id": self.resourceinstance_id}
            try:
                uuid.UUID(str(self.parenttile_id))
                kwargs["parenttile_id"] = self.parenttile_id
            except ValueError:
                pass

            existing_tiles = list(models.TileModel.objects.filter(**kwargs).values_list("tileid", flat=True))

            # this should only ever return at most one tile
            if len(existing_tiles) > 0 and uuid.UUID(str(self.tileid)) not in existing_tiles:
                card = models.CardModel.objects.get(nodegroup=self.nodegroup)
                message = _("Unable to save a tile to a card with cardinality 1 where a tile has previously been saved.")
                details = _(
                    "Details: card: {0}, graph: {1}, resource: {2}, tile: {3}, nodegroup: {4}".format(
                        card.name, self.resourceinstance.graph.name, self.resourceinstance_id, self.tileid, self.nodegroup_id
                    )
                )
                message += " " + details
                raise TileCardinalityError(message)

    def check_for_constraint_violation(self):
        if settings.BYPASS_UNIQUE_CONSTRAINT_TILE_VALIDATION:
            return
        card = models.CardModel.objects.get(nodegroup=self.nodegroup)
        constraints = models.ConstraintModel.objects.filter(card=card)
        if constraints.count() > 0:
            for constraint in constraints:
                if constraint.uniquetoallinstances is True:
                    tiles = models.TileModel.objects.filter(nodegroup=self.nodegroup)
                else:
                    tiles = models.TileModel.objects.filter(
                        Q(resourceinstance_id=self.resourceinstance.resourceinstanceid) & Q(nodegroup=self.nodegroup)
                    )
                nodes = [node for node in constraint.nodes.all()]
                for tile in tiles:
                    if str(self.tileid) != str(tile.tileid):
                        match = False
                        duplicate_values = []
                        for node in nodes:
                            datatype = self.datatype_factory.get_instance(node.datatype)
                            nodeid = str(node.nodeid)
                            tile_data = ""
                            if tile.provisionaledits is None:
                                # If this is not a provisional tile, the data should
                                # exist, so we check it normally
                                tile_data = tile.data[nodeid]
                            else:
                                # If it is a provisional tile, we need to check the
                                # provisional edits for clashing values
                                for edit_id in tile.provisionaledits.keys():
                                    edit_data = tile.provisionaledits[str(edit_id)]
                                    if nodeid in edit_data["value"]:
                                        tile_data = edit_data["value"][nodeid]
                                        break
                            if datatype.values_match(tile_data, self.data[nodeid]):
                                match = True
                                duplicate_values.append(datatype.get_display_value(tile, node))
                            else:
                                match = False
                                break
                        if match is True:
                            message = _(
                                "This card violates a unique constraint. \
                                The following value is already saved: "
                            )
                            raise TileValidationError(message + (", ").join(duplicate_values))

    def check_for_missing_nodes(self, request):
        if settings.BYPASS_REQUIRED_VALUE_TILE_VALIDATION:
            return
        missing_nodes = []
        for nodeid, value in self.data.items():
            try:
                node = models.Node.objects.get(nodeid=nodeid)
                datatype = self.datatype_factory.get_instance(node.datatype)
                datatype.clean(self, nodeid)
                if request is not None:
                    if self.data[nodeid] is None and node.isrequired is True:
                        if len(node.cardxnodexwidget_set.all()) > 0:
                            missing_nodes.append(node.cardxnodexwidget_set.all()[0].label)
                        else:
                            missing_nodes.append(node.name)
            except Exception as e:
                warning = _(
                    "Error checking for missing node. Nodeid: {nodeid} with value: {value}, not in nodes. \
                    You may have a node in your business data that no longer exists in any graphs."
                ).format(**locals())
                logger.warning(warning)
        if missing_nodes != []:
            message = _("This card requires values for the following: ")
            message += (", ").join(missing_nodes)
            raise TileValidationError(message)

    def validate(self, errors=None):
        for nodeid, value in self.data.items():
            node = models.Node.objects.get(nodeid=nodeid)
            datatype = self.datatype_factory.get_instance(node.datatype)
            error = datatype.validate(value, node=node)
            for error_instance in error:
                if error_instance["type"] == "ERROR":
                    raise TileValidationError(_("{0}".format(error_instance["message"])))
            if errors is not None:
                errors += error
        return errors

    def get_tile_data(self, user_id=None):
        data = self.data

        if user_id is not None:
            user_id = str(user_id)
            user = User.objects.get(pk=user_id)
            user_is_reviewer = user_is_resource_reviewer(user)
            if user_is_reviewer is False and self.provisionaledits is not None and user_id in self.provisionaledits:
                data = self.provisionaledits[user_id]["value"]

        return data

    def datatype_post_save_actions(self, request=None):
        userid = None
        if request is not None:
            userid = str(request.user.id)
            if hasattr(request.user, "userprofile") is not True:
                models.UserProfile.objects.create(user=request.user)
        tile_data = self.get_tile_data(userid)
        for nodeid, value in list(tile_data.items()):
            node = models.Node.objects.get(nodeid=nodeid)
            datatype = self.datatype_factory.get_instance(node.datatype)
            if request is not None:
                datatype.handle_request(self, request, node)

    def save(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        index = kwargs.pop("index", True)
        user = kwargs.pop("user", None)
        log = kwargs.pop("log", True)
        provisional_edit_log_details = kwargs.pop("provisional_edit_log_details", None)
        missing_nodes = []
        creating_new_tile = True
        user_is_reviewer = False
        newprovisionalvalue = None
        oldprovisionalvalue = None

        try:
            if user is None and request is not None:
                user = request.user
            user_is_reviewer = user_is_resource_reviewer(user)
        except AttributeError:  # no user - probably importing data
            user = None

        with transaction.atomic():
            for nodeid, value in self.data.items():
                node = models.Node.objects.get(nodeid=nodeid)
                datatype = self.datatype_factory.get_instance(node.datatype)
                datatype.pre_tile_save(self, nodeid)
            self.__preSave(request)
            self.check_for_missing_nodes(request)
            self.check_for_constraint_violation()
            self.check_tile_cardinality_violation()

            creating_new_tile = models.TileModel.objects.filter(pk=self.tileid).exists() is False
            edit_type = "tile create" if (creating_new_tile is True) else "tile edit"

            if creating_new_tile is False:
                existing_model = models.TileModel.objects.get(pk=self.tileid)

            # this section moves the data over from self.data to self.provisionaledits if certain users permissions are in force
            # then self.data is restored from the previously saved tile data
            if user is not None and user_is_reviewer is False:
                if creating_new_tile is True:
                    self.apply_provisional_edit(user, data=self.data, action="create")
                    newprovisionalvalue = self.data
                    self.data = {}

                else:
                    # the user has previously edited this tile
                    self.apply_provisional_edit(user, self.data, action="update", existing_model=existing_model)
                    newprovisionalvalue = self.data
                    self.data = existing_model.data

                    oldprovisional = self.get_provisional_edit(existing_model, user)
                    if oldprovisional is not None:
                        oldprovisionalvalue = oldprovisional["value"]

                if provisional_edit_log_details is None:
                    provisional_edit_log_details = {
                        "user": user,
                        "provisional_editor": user,
                        "action": "create tile" if creating_new_tile else "add edit",
                    }

            if user is not None:
                self.validate([])

            super(Tile, self).save(*args, **kwargs)
            # We have to save the edit log record after calling save so that the
            # resource's displayname changes are avaliable
            user = {} if user is None else user
            self.datatype_post_save_actions(request)
            self.__postSave(request)
            if creating_new_tile is True:
                self.save_edit(
                    user=user,
                    edit_type=edit_type,
                    old_value={},
                    new_value=self.data,
                    newprovisionalvalue=newprovisionalvalue,
                    provisional_edit_log_details=provisional_edit_log_details,
                )
            else:
                self.save_edit(
                    user=user,
                    edit_type=edit_type,
                    old_value=existing_model.data,
                    new_value=self.data,
                    newprovisionalvalue=newprovisionalvalue,
                    oldprovisionalvalue=oldprovisionalvalue,
                    provisional_edit_log_details=provisional_edit_log_details,
                )

            if index:
                self.index()

            for tile in self.tiles:
                tile.resourceinstance = self.resourceinstance
                tile.parenttile = self
                tile.save(*args, request=request, index=index, **kwargs)

    def delete(self, *args, **kwargs):
        se = SearchEngineFactory().create()
        request = kwargs.pop("request", None)
        index = kwargs.pop("index", True)
        provisional_edit_log_details = kwargs.pop("provisional_edit_log_details", None)
        for tile in self.tiles:
            tile.delete(*args, request=request, **kwargs)
        try:
            user = request.user
            user_is_reviewer = user_is_resource_reviewer(user)
        except AttributeError:  # no user
            user = None
            user_is_reviewer = True

        if user_is_reviewer is True or self.user_owns_provisional(user):
            if index:
                query = Query(se)
                bool_query = Bool()
                bool_query.filter(Terms(field="tileid", terms=[self.tileid]))
                query.add_query(bool_query)
                results = query.delete(index=TERMS_INDEX)

            self.__preDelete(request)
            self.save_edit(
                user=user, edit_type="tile delete", old_value=self.data, provisional_edit_log_details=provisional_edit_log_details
            )
            try:
                super(Tile, self).delete(*args, **kwargs)
                for nodeid in self.data.keys():
                    node = models.Node.objects.get(nodeid=nodeid)
                    datatype = self.datatype_factory.get_instance(node.datatype)
                    datatype.post_tile_delete(self, nodeid, index=index)
                if index:
                    self.index()
            except IntegrityError as e:
                logger.error(e)

        else:
            self.apply_provisional_edit(user, data={}, action="delete")
            super(Tile, self).save(*args, **kwargs)

    def index(self):
        """
        Indexes all the nessesary documents related to resources to support the map, search, and reports

        """

        Resource.objects.get(pk=self.resourceinstance_id).index()

    # # flatten out the nested tiles into a single array
    def get_flattened_tiles(self):
        tiles = []

        def flatten_tiles(obj):
            for tile in obj.tiles:
                tiles.append(flatten_tiles(tile))
            return obj

        tiles.append(flatten_tiles(self))
        return tiles

    def after_update_all(self):
        nodegroup = models.NodeGroup.objects.get(pk=self.nodegroup_id)
        for node in nodegroup.node_set.all():
            datatype = self.datatype_factory.get_instance(node.datatype)
            datatype.after_update_all()
        for tile in self.tiles:
            tile.after_update_all()

    def is_blank(self):
        if self.data != {}:
            if len([item for item in list(self.data.values()) if item is not None]) > 0:
                return False

        child_tiles_are_blank = True
        for tile in self.tiles:
            if tile.is_blank() is False:
                child_tiles_are_blank = False
                break

        return child_tiles_are_blank

    @staticmethod
    def get_blank_tile(nodeid, resourceid=None):
        parent_nodegroup = None

        node = models.Node.objects.get(pk=nodeid)
        if node.nodegroup.parentnodegroup_id is not None:
            parent_nodegroup = node.nodegroup.parentnodegroup
            parent_tile = Tile()
            parent_tile.data = {}
            parent_tile.tileid = None
            parent_tile.nodegroup_id = node.nodegroup.parentnodegroup_id
            parent_tile.resourceinstance_id = resourceid
            parent_tile.tiles = []
            for nodegroup in models.NodeGroup.objects.filter(parentnodegroup_id=node.nodegroup.parentnodegroup_id):
                parent_tile.tiles.append(Tile.get_blank_tile_from_nodegroup_id(nodegroup.pk, resourceid=resourceid, parenttile=parent_tile))
            return parent_tile
        else:
            return Tile.get_blank_tile_from_nodegroup_id(node.nodegroup_id, resourceid=resourceid)

    @staticmethod
    def get_blank_tile_from_nodegroup_id(nodegroup_id, resourceid=None, parenttile=None):
        tile = Tile()
        tile.nodegroup_id = nodegroup_id
        tile.resourceinstance_id = resourceid
        tile.parenttile = parenttile
        tile.data = {}

        for node in models.Node.objects.filter(nodegroup=nodegroup_id):
            tile.data[str(node.nodeid)] = None

        return tile

    @staticmethod
    def update_node_value(nodeid, value, tileid=None, nodegroupid=None, resourceinstanceid=None):
        """
        Updates the value of a node in a tile. Creates the tile and parent tiles if they do not yet
        exist.

        """

        if tileid and models.TileModel.objects.filter(pk=tileid).exists():
            tile = Tile.objects.get(pk=tileid)
            tile.data[nodeid] = value
            tile.save()
        elif models.TileModel.objects.filter(Q(resourceinstance_id=resourceinstanceid), Q(nodegroup_id=nodegroupid)).count() == 1:
            tile = Tile.objects.filter(Q(resourceinstance_id=resourceinstanceid), Q(nodegroup_id=nodegroupid))[0]
            tile.data[nodeid] = value
            tile.save()
        else:
            if not resourceinstanceid:
                graph = models.Node.objects.get(pk=nodeid).graph
                resource_instance = models.ResourceInstance(graph=graph)
                resource_instance.save()
                resourceinstanceid = str(resource_instance.resourceinstanceid)
            tile = Tile.get_blank_tile(nodeid, resourceinstanceid)
            if nodeid in tile.data:
                tile.data[nodeid] = value
                tile.save()
            else:
                tile.save()
                if nodegroupid and resourceinstanceid:
                    tile = Tile.update_node_value(nodeid, value, nodegroupid=nodegroupid, resourceinstanceid=resourceinstanceid)
        return tile

    def __preSave(self, request=None):
        try:
            for function in self._getFunctionClassInstances():
                try:
                    function.save(self, request)
                except NotImplementedError:
                    pass
        except TypeError:
            logger.info(_("No associated functions or other TypeError raised by a function"))

    def __preDelete(self, request):
        try:
            for function in self._getFunctionClassInstances():
                try:
                    function.delete(self, request)
                except NotImplementedError:
                    pass
        except TypeError:
            logger.info(_("No associated functions or other TypeError raised by a function"))

    def __postSave(self, request=None):
        try:
            for function in self._getFunctionClassInstances():
                try:
                    function.post_save(self, request)
                except NotImplementedError:
                    pass
        except TypeError as e:
            logger.warning(_("No associated functions or other TypeError raised by a function"))
            logger.warning(e)

    def _getFunctionClassInstances(self):
        ret = []
        resource = models.ResourceInstance.objects.get(pk=self.resourceinstance_id)
        functionXgraphs = models.FunctionXGraph.objects.filter(
            Q(graph_id=resource.graph_id),
            Q(config__contains={"triggering_nodegroups": [str(self.nodegroup_id)]}) | Q(config__triggering_nodegroups__exact=[]),
            ~Q(function__classname="PrimaryDescriptorsFunction"),
        )
        for functionXgraph in functionXgraphs:
            func = functionXgraph.function.get_class_module()(functionXgraph.config, self.nodegroup_id)
            ret.append(func)
        return ret

    def filter_by_perm(self, user, perm):
        if user:
            if self.nodegroup_id is not None and user.has_perm(perm, self.nodegroup):
                self.tiles = [tile for tile in self.tiles if tile.filter_by_perm(user, perm)]
            else:
                return None
        return self

    def serialize(self, fields=None, exclude=None):
        """
        serialize to a different form then used by the internal class structure

        """

        ret = JSONSerializer().handle_model(self)
        ret["tiles"] = self.tiles

        return ret


class TileValidationError(Exception):
    def __init__(self, message, code=None):
        self.title = _("Tile Validation Error")
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)


class TileCardinalityError(TileValidationError):
    def __init__(self, message, code=None):
        super(TileCardinalityError, self).__init__(message, code)
        self.title = _("Tile Cardinaltiy Error")
