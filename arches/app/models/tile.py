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
from types import SimpleNamespace
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext as _
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

        self.serialized_graph = None
        self.load_serialized_graph()

    def load_serialized_graph(self):
        try:
            resource = self.resourceinstance
        except models.ResourceInstance.DoesNotExist:
            return

        published_graph = resource.graph.get_published_graph()

        if published_graph:
            self.serialized_graph = published_graph.serialized_graph

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
        transaction_id=None,
        new_resource_created=False,
    ):
        if new_resource_created:
            timestamp = datetime.datetime.now()
            resource_edit = EditLog()
            resource_edit.resourceclassid = self.resourceinstance.graph_id
            resource_edit.resourceinstanceid = self.resourceinstance.resourceinstanceid
            resource_edit.edittype = "create"
            resource_edit.timestamp = timestamp
            resource_edit.userid = getattr(user, "id", "")
            resource_edit.user_email = getattr(user, "email", "")
            resource_edit.user_firstname = getattr(user, "first_name", "")
            resource_edit.user_lastname = getattr(user, "last_name", "")
            resource_edit.user_username = getattr(user, "username", "")
            if transaction_id is not None:
                resource_edit.transactionid = transaction_id
            resource_edit.save()

        timestamp = datetime.datetime.now()
        edit = EditLog()
        edit.resourceclassid = self.resourceinstance.graph_id
        edit.resourceinstanceid = self.resourceinstance.resourceinstanceid
        edit.nodegroupid = self.nodegroup_id
        edit.tileinstanceid = self.tileid
        if provisional_edit_log_details is not None:
            edit.provisional_user_username = getattr(
                provisional_edit_log_details["provisional_editor"], "username", ""
            )
            edit.provisional_userid = getattr(
                provisional_edit_log_details["provisional_editor"], "id", ""
            )
            edit.provisional_edittype = provisional_edit_log_details["action"]
            user = provisional_edit_log_details["user"]
        edit.userid = getattr(user, "id", "")
        edit.user_email = getattr(user, "email", "")
        edit.user_firstname = getattr(user, "first_name", "")
        edit.user_lastname = getattr(user, "last_name", "")
        edit.user_username = getattr(user, "username", "")
        edit.resourcedisplayname = Resource.objects.get(
            resourceinstanceid=self.resourceinstance.resourceinstanceid
        ).displayname()
        edit.oldvalue = old_value
        edit.newvalue = new_value
        edit.timestamp = timestamp
        edit.edittype = edit_type
        edit.newprovisionalvalue = newprovisionalvalue
        edit.oldprovisionalvalue = oldprovisionalvalue
        edit.note = note
        if transaction_id is not None:
            edit.transactionid = transaction_id
        edit.save()

    def tile_collects_data(self):
        result = True
        if self.tiles is not None and len(self.tiles) > 0:
            nodes = models.Node.objects.filter(nodegroup=self.nodegroup)
            if len(nodes) == 1 and nodes[0].datatype == "semantic":
                result = False
        return result

    def apply_provisional_edit(
        self, user, data, action="create", status="review", existing_model=None
    ):
        """
        Creates or updates the json stored in a tile's provisionaledits db_column

        """
        if self.tile_collects_data() is True and data != {}:

            utc_date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
            timestamp_utc = str(
                datetime.datetime.now(pytz.utc).strftime(utc_date_format)
            )

            provisionaledit = {
                "value": data,
                "status": status,
                "action": action,
                "reviewer": None,
                "timestamp": timestamp_utc,
                "reviewtimestamp": None,
            }

            # if this tile has been previously saved and already has provisional edits on it then
            if (
                existing_model is not None
                and existing_model.provisionaledits is not None
            ):
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
        if self.provisionaledits is not None and not any(self.data.values()):
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

    def check_for_constraint_violation(self):
        if settings.BYPASS_UNIQUE_CONSTRAINT_TILE_VALIDATION:
            return
        card = models.CardModel.objects.get(nodegroup=self.nodegroup)
        constraints = models.ConstraintModel.objects.filter(card=card)
        if constraints.exists():
            for constraint in constraints:
                if constraint.uniquetoallinstances is True:
                    tiles = models.TileModel.objects.filter(
                        nodegroup_id=self.nodegroup_id
                    )
                else:
                    tiles = models.TileModel.objects.filter(
                        Q(resourceinstance_id=self.resourceinstance.resourceinstanceid)
                        & Q(nodegroup_id=self.nodegroup_id)
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
                                duplicate_values.append(
                                    datatype.get_display_value(tile, node)
                                )
                            else:
                                match = False
                                break
                        if match is True:
                            message = _(
                                "This card violates a unique constraint. \
                                The following value is already saved: "
                            )
                            raise TileValidationError(
                                message + (", ").join(duplicate_values)
                            )

    def check_for_missing_nodes(self):
        if settings.BYPASS_REQUIRED_VALUE_TILE_VALIDATION:
            return
        missing_nodes = []
        for nodeid, value in self.data.items():
            try:
                try:
                    node = SimpleNamespace(
                        **next(
                            (
                                x
                                for x in self.serialized_graph["nodes"]
                                if x["nodeid"] == nodeid
                            ),
                            None,
                        )
                    )
                except:
                    node = models.Node.objects.get(nodeid=nodeid)
                datatype = self.datatype_factory.get_instance(node.datatype)
                datatype.clean(self, nodeid)
                if self.data[nodeid] is None and node.isrequired is True:
                    if not isinstance(node, models.Node):
                        node = models.Node.objects.get(nodeid=nodeid)

                    first_card_x_node_x_widget = node.cardxnodexwidget_set.first()
                    if first_card_x_node_x_widget:
                        missing_nodes.append(str(first_card_x_node_x_widget.label))
                    else:
                        missing_nodes.append(node.name)
            except Exception:
                warning = _(
                    "Error checking for missing node. Nodeid: {nodeid} with value: {value}, not in nodes. \
                    You may have a node in your business data that no longer exists in any graphs."
                ).format(**locals())
                logger.warning(warning)
        if missing_nodes != []:
            message = _("This card requires values for the following: ")
            message += (", ").join(missing_nodes)
            raise TileValidationError(message)

    def validate(self, errors=None, raise_early=True, strict=False, request=None):
        """
        Keyword Arguments:
        errors -- supply and list to have errors appened on to
        raise_early -- True(default) to raise an error on the first value in the tile that throws an error
            otherwise throw an error only after all nodes in a tile have been validated
        strict -- False(default), True to use a more complete check on the datatype
            (eg: check for the existance of a referenced resoure on the resource-instance datatype)
        """

        tile_errors = []
        for nodeid, value in self.data.items():
            try:
                node = SimpleNamespace(
                    **next(
                        (
                            x
                            for x in self.serialized_graph["nodes"]
                            if x["nodeid"] == nodeid
                        ),
                        None,
                    )
                )
                node.pk = uuid.UUID(node.nodeid)
            except TypeError:  # will catch if serialized_graph is None
                node = models.Node.objects.get(nodeid=nodeid)
            datatype = self.datatype_factory.get_instance(node.datatype)
            error = datatype.validate(value, node=node, strict=strict, request=request)
            tile_errors += error
            for error_instance in error:
                if error_instance["type"] == "ERROR":
                    if raise_early:
                        raise TileValidationError(
                            _("{0}".format(error_instance["message"]))
                        )
            if errors is not None:
                errors += error
        if not raise_early:
            raise TileValidationError(tile_errors)
        return errors

    def get_tile_data(self, user_id=None):
        data = self.data

        if user_id is not None:
            user_id = str(user_id)
            user = User.objects.get(pk=user_id)
            user_is_reviewer = user_is_resource_reviewer(user)
            if (
                user_is_reviewer is False
                and self.provisionaledits is not None
                and user_id in self.provisionaledits
            ):
                data = self.provisionaledits[user_id]["value"]

        return data

    def datatype_post_save_actions(self, request=None):
        try:
            userid = str(request.user.id)
        except:
            userid = None

        tile_data = self.get_tile_data(userid)
        for nodeid in tile_data.keys():
            try:
                node = SimpleNamespace(
                    **next(
                        (
                            x
                            for x in self.serialized_graph["nodes"]
                            if x["nodeid"] == nodeid
                        ),
                        None,
                    )
                )
            except:
                node = models.Node.objects.get(nodeid=nodeid)
            datatype = self.datatype_factory.get_instance(node.datatype)
            datatype.post_tile_save(self, nodeid, request)

    def save(self, **kwargs):
        request = kwargs.pop("request", None)
        index = kwargs.pop("index", True)
        user = kwargs.pop("user", None)
        new_resource_created = kwargs.pop("new_resource_created", False)
        resource_creation = kwargs.pop("resource_creation", False)
        note = "resource creation" if resource_creation else None
        context = kwargs.pop("context", None)
        transaction_id = kwargs.pop("transaction_id", None)
        provisional_edit_log_details = kwargs.pop("provisional_edit_log_details", None)
        creating_new_tile = True
        user_is_reviewer = False
        newprovisionalvalue = None
        oldprovisionalvalue = None

        if not self.serialized_graph:
            self.load_serialized_graph()
        try:
            if user is None and request is not None:
                user = request.user
            user_is_reviewer = user_is_resource_reviewer(user)
        except AttributeError:  # no user - probably importing data
            user = None

        with transaction.atomic():
            for nodeid in self.data.keys():
                node = next(
                    item
                    for item in self.serialized_graph["nodes"]
                    if item["nodeid"] == nodeid
                )
                datatype = self.datatype_factory.get_instance(node["datatype"])
                datatype.pre_tile_save(self, nodeid)
            self.__preSave(request, context=context)
            self.check_for_missing_nodes()
            self.check_for_constraint_violation()

            existing_model = models.TileModel.objects.filter(pk=self.tileid).first()
            creating_new_tile = existing_model is None
            edit_type = "tile edit"
            if creating_new_tile:
                edit_type = "tile create"
                self.populate_missing_nodes()

            # this section moves the data over from self.data to self.provisionaledits if certain users permissions are in force
            # then self.data is restored from the previously saved tile data
            if user is not None and user_is_reviewer is False:
                if creating_new_tile is True:
                    self.apply_provisional_edit(user, data=self.data, action="create")
                    newprovisionalvalue = self.data
                    self.data = {}

                else:
                    # the user has previously edited this tile
                    self.apply_provisional_edit(
                        user, self.data, action="update", existing_model=existing_model
                    )
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
                self.validate([], request=request)

            super(Tile, self).save(**kwargs)
            # We have to save the edit log record after calling save so that the
            # resource's displayname changes are avaliable
            user = {} if user is None else user
            self.datatype_post_save_actions(request)
            self.__postSave(request, context=context)
            if creating_new_tile is True:
                self.save_edit(
                    user=user,
                    edit_type=edit_type,
                    old_value={},
                    new_value=self.data,
                    newprovisionalvalue=newprovisionalvalue,
                    provisional_edit_log_details=provisional_edit_log_details,
                    transaction_id=transaction_id,
                    new_resource_created=new_resource_created,
                    note=note,
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
                    transaction_id=transaction_id,
                )

            for tile in self.tiles:
                tile.resourceinstance = self.resourceinstance
                tile.parenttile = self
                tile.save(
                    request=request,
                    resource_creation=resource_creation,
                    index=False,
                    **kwargs,
                )

            resource = Resource.objects.get(pk=self.resourceinstance_id)
            resource.save_descriptors(context={"tile": self})

            if index:
                self.index(resource=resource)

    def populate_missing_nodes(self):
        first_node = next(iter(self.data.items()), None)
        if first_node is not None:
            result = Tile.get_blank_tile_from_nodegroup_id(
                nodegroup_id=self.nodegroup_id
            )
            result.data.update(self.data)
            self.data = result.data

    def delete(self, *args, **kwargs):
        se = SearchEngineFactory().create()
        request = kwargs.pop("request", None)
        index = kwargs.pop("index", True)
        transaction_id = kwargs.pop("transaction_id", None)
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
                user=user,
                edit_type="tile delete",
                old_value=self.data,
                provisional_edit_log_details=provisional_edit_log_details,
                transaction_id=transaction_id,
            )
            try:
                super(Tile, self).delete(*args, **kwargs)
                for nodeid in self.data.keys():
                    try:
                        node = SimpleNamespace(
                            **next(
                                (
                                    x
                                    for x in self.serialized_graph["nodes"]
                                    if x["nodeid"] == nodeid
                                ),
                                None,
                            )
                        )
                    except TypeError:  # will catch if serialized_graph is None
                        node = models.Node.objects.get(nodeid=nodeid)

                    datatype = self.datatype_factory.get_instance(node.datatype)
                    datatype.post_tile_delete(self, nodeid, index=index)

                resource = Resource.objects.get(pk=self.resourceinstance_id)
                resource.save_descriptors()

                if index:
                    self.index(resource=resource)
            except IntegrityError as e:
                logger.error(e)

        else:
            self.apply_provisional_edit(user, data={}, action="delete")
            super(Tile, self).save(*args, **kwargs)

    def index(self, resource=None):
        """
        Indexes all the nessesary documents related to resources to support the map, search, and reports

        """

        if not resource:
            Resource.objects.get(pk=self.resourceinstance_id).index()
        else:
            resource.index()

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
        try:
            nodes = [
                SimpleNamespace(node)
                for node in self.serialized_graph["nodes"]
                if node["nodegroup_id"] == str(self.nodegroup_id)
            ]
        except TypeError:  # handle if serialized_graph is None
            nodes = self.nodegroup.node_set.all()

        for node in nodes:
            datatype = self.datatype_factory.get_instance(node.datatype)
            datatype.after_update_all(tile=self)
        for tile in self.tiles:
            tile.after_update_all()

    def is_blank(self):
        if self.data != {}:
            if any(self.data.values()):
                return False

        child_tiles_are_blank = True
        for tile in self.tiles:
            if tile.is_blank() is False:
                child_tiles_are_blank = False
                break

        return child_tiles_are_blank

    @staticmethod
    def get_blank_tile(nodeid, resourceid=None):
        node = models.Node.objects.filter(pk=nodeid).select_related("nodegroup")[0]
        parentnodegroup_id = node.nodegroup.parentnodegroup_id
        if parentnodegroup_id is not None:
            parent_tile = Tile.get_blank_tile_from_nodegroup_id(
                nodegroup_id=parentnodegroup_id, resourceid=resourceid, parenttile=None
            )
            parent_tile.tileid = None
            parent_tile.tiles = []
            for nodegroup in models.NodeGroup.objects.filter(
                parentnodegroup_id=parentnodegroup_id
            ):
                parent_tile.tiles.append(
                    Tile.get_blank_tile_from_nodegroup_id(
                        nodegroup.pk, resourceid=resourceid, parenttile=parent_tile
                    )
                )
            return parent_tile
        else:
            return Tile.get_blank_tile_from_nodegroup_id(
                node.nodegroup_id, resourceid=resourceid
            )

    @staticmethod
    def get_blank_tile_from_nodegroup_id(
        nodegroup_id, resourceid=None, parenttile=None
    ):
        tile = Tile()
        tile.nodegroup_id = nodegroup_id
        tile.resourceinstance_id = resourceid
        tile.parenttile = parenttile
        tile.data = {}
        nodes = models.Node.objects.filter(nodegroup=nodegroup_id).exclude(
            datatype="semantic"
        )

        for node in nodes:
            tile.data[str(node.nodeid)] = None

        return tile

    @staticmethod
    def update_node_value(
        nodeid,
        value,
        tileid=None,
        nodegroupid=None,
        request=None,
        resourceinstanceid=None,
        transaction_id=None,
    ):
        """
        Updates the value of a node in a tile. Creates the tile and parent tiles if they do not yet
        exist.

        """
        if tileid and models.TileModel.objects.filter(pk=tileid).exists():
            tile = Tile.objects.get(pk=tileid)
            tile.data[nodeid] = value
            tile.save(request=request, transaction_id=transaction_id)
        elif (
            models.TileModel.objects.filter(
                Q(resourceinstance_id=resourceinstanceid), Q(nodegroup_id=nodegroupid)
            ).count()
            == 1
        ):
            tile = Tile.objects.filter(
                Q(resourceinstance_id=resourceinstanceid), Q(nodegroup_id=nodegroupid)
            )[0]
            tile.data[nodeid] = value
            tile.save(request=request, transaction_id=transaction_id)
        else:
            new_resource_created = False
            if not resourceinstanceid:
                graph = models.Node.objects.get(pk=nodeid).graph
                resource_instance = models.ResourceInstance(graph=graph)
                resource_instance.save()
                resourceinstanceid = str(resource_instance.resourceinstanceid)
                new_resource_created = True
            tile = Tile.get_blank_tile(nodeid, resourceinstanceid)
            if nodeid in tile.data:
                tile.data[nodeid] = value
                tile.save(
                    request=request,
                    new_resource_created=new_resource_created,
                    transaction_id=transaction_id,
                )
            else:
                tile.save(
                    request=request,
                    new_resource_created=new_resource_created,
                    transaction_id=transaction_id,
                )
                if not nodegroupid:
                    nodegroupid = models.Node.objects.get(pk=nodeid).nodegroup_id
                if nodegroupid and resourceinstanceid:
                    tile = Tile.update_node_value(
                        nodeid,
                        value,
                        nodegroupid=nodegroupid,
                        request=request,
                        resourceinstanceid=resourceinstanceid,
                        transaction_id=transaction_id,
                    )

        tile.after_update_all()
        return tile

    def __preSave(self, request=None, context=None):
        """
        Keyword Arguments:
        request -- request object passed from the view to the model.
        context -- string e.g. "copy" indicating conditions under which a resource is saved and how functions should behave.
        """

        for function in self._getFunctionClassInstances():
            try:
                function.save(self, request, context=context)
            except NotImplementedError:
                pass

    def __preDelete(self, request=None):
        for function in self._getFunctionClassInstances():
            try:
                function.delete(self, request)
            except NotImplementedError:
                pass

    def __postSave(self, request=None, context=None):
        """
        Keyword Arguments:
        request -- request object passed from the view to the model.
        context -- string e.g. "copy" indicating conditions under which a resource is saved and how functions should behave.
        """

        for function in self._getFunctionClassInstances():
            try:
                function.post_save(self, request, context=context)
            except NotImplementedError:
                pass

    def _getFunctionClassInstances(self):
        ret = []
        functionXgraphs = models.FunctionXGraph.objects.filter(
            Q(graph_id=self.resourceinstance.graph_id),
            Q(config__contains={"triggering_nodegroups": [str(self.nodegroup_id)]})
            | Q(config__triggering_nodegroups__exact=[]),
            ~Q(function__functiontype="primarydescriptors"),
        ).select_related("function")
        for functionXgraph in functionXgraphs:
            func = functionXgraph.function.get_class_module()(
                functionXgraph.config, self.nodegroup_id
            )
            ret.append(func)
        return ret

    def filter_by_perm(self, user, perm):
        if user:
            if self.nodegroup_id is not None and user.has_perm(perm, self.nodegroup):
                self.tiles = [
                    tile for tile in self.tiles if tile.filter_by_perm(user, perm)
                ]
            else:
                return None
        return self

    def serialize(self, fields=None, exclude=None, **kwargs):
        """
        serialize to a different form then used by the internal class structure

        """

        ret = JSONSerializer().handle_model(self)
        ret["tiles"] = self.tiles

        return ret


class TileValidationError(ValidationError):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.title = _("Tile Validation Error")
        self.code = code

    def __str__(self):
        if hasattr(self, "messages"):
            return repr(self.messages)
        return repr(self.message)


class TileCardinalityError(TileValidationError):
    def __init__(self, message, code=None):
        super().__init__(message, code)
        self.title = _("Tile Cardinality Error")
