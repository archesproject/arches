'''
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
'''

import uuid, importlib
import datetime
import json
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext as _
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.resource import EditLog
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Bool, Terms
from arches.app.datatypes.datatypes import DataTypeFactory


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

        if args:
            if isinstance(args[0], dict):
                for key, value in args[0].iteritems():
                    if not (key == 'tiles'):
                        setattr(self, key, value)

                if self.tileid is None or self.tileid == '':
                    self.tileid = uuid.uuid4()

                if 'tiles' in args[0]:
                    for tile_obj in args[0]['tiles']:
                        tile = Tile(tile_obj)
                        tile.parenttile = self
                        self.tiles.append(tile)

    def save_edit(self, user={}, note='', edit_type='', old_value=None, new_value=None, newprovisionalvalue=None, oldprovisionalvalue=None, provisional_edit_log_details=None):
        timestamp = datetime.datetime.now()
        edit = EditLog()
        edit.resourceclassid = self.resourceinstance.graph_id
        edit.resourceinstanceid = self.resourceinstance.resourceinstanceid
        edit.nodegroupid = self.nodegroup_id
        edit.tileinstanceid = self.tileid
        if provisional_edit_log_details != None:
            edit.provisional_user_username = getattr(provisional_edit_log_details['provisional_editor'], 'username', '')
            edit.provisional_userid = getattr(provisional_edit_log_details['provisional_editor'], 'id', '')
            edit.provisional_edittype = provisional_edit_log_details['action']
            user = provisional_edit_log_details['user']
        edit.userid = getattr(user, 'id', '')
        edit.user_email = getattr(user, 'email', '')
        edit.user_firstname = getattr(user, 'first_name', '')
        edit.user_lastname = getattr(user, 'last_name', '')
        edit.user_username = getattr(user, 'username', '')
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
        if self.tiles != None and len(self.tiles) > 0:
            nodes = models.Node.objects.filter(nodegroup=self.nodegroup)
            if len(nodes) == 1 and nodes[0].datatype == 'semantic':
                result = False
        return result

    def apply_provisional_edit(self, user, data, action='create', status='review', existing_model=None):
        """
        Creates or updates the json stored in a tile's provisionaledits db_column

        """
        if self.tile_collects_data() is True and data != {}:

            provisionaledit =  {
                "value": data,
                "status": status,
                "action": action,
                "reviewer": None,
                "timestamp": unicode(timezone.now()),
                "reviewtimestamp": None
            }

            if existing_model is not None and existing_model.provisionaledits is not None:
                provisionaledits = existing_model.provisionaledits
                provisionaledits[str(user.id)] = provisionaledit
            else:
                provisionaledits = {
                    str(user.id): provisionaledit
                    }
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

    def check_for_missing_nodes(self, request):
        missing_nodes = []
        for nodeid, value in self.data.iteritems():
            datatype_factory = DataTypeFactory()
            node = models.Node.objects.get(nodeid=nodeid)
            datatype = datatype_factory.get_instance(node.datatype)
            datatype.clean(self, nodeid)
            if request is not None:
                datatype.handle_request(self, request, node)
                if self.data[nodeid] == None and node.isrequired == True:
                    if len(node.cardxnodexwidget_set.all()) > 0:
                        missing_nodes.append(node.cardxnodexwidget_set.all()[0].label)
                    else:
                        missing_nodes.append(node.name)
        if missing_nodes != []:
            message = _('This card requires values for the following:')
            raise ValidationError(message, (', ').join(missing_nodes))

    def validate(self, errors=None):
        for nodeid, value in self.data.iteritems():
            datatype_factory = DataTypeFactory()
            node = models.Node.objects.get(nodeid=nodeid)
            datatype = datatype_factory.get_instance(node.datatype)
            error = datatype.validate(value)
            if errors != None:
                errors += error
        return errors

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        index = kwargs.pop('index', True)
        log = kwargs.pop('log', True)
        provisional_edit_log_details = kwargs.pop('provisional_edit_log_details', None)
        self.__preSave(request)
        missing_nodes = []
        creating_new_tile = True
        user_is_reviewer = False
        newprovisionalvalue = None
        oldprovisionalvalue = None
        self.check_for_missing_nodes(request)

        try:
            user = request.user
            user_is_reviewer = request.user.groups.filter(name='Resource Reviewer').exists()
        except AttributeError: #no user - probably importing data
            user = None

        creating_new_tile = models.TileModel.objects.filter(pk=self.tileid).exists() == False
        edit_type = 'tile create' if (creating_new_tile == True) else 'tile edit'

        if creating_new_tile == False:
            existing_model = models.TileModel.objects.get(pk=self.tileid)

        if user is not None:
            if user_is_reviewer == False and creating_new_tile == False:
                self.apply_provisional_edit(user, self.data, action='update', existing_model=existing_model)
                newprovisionalvalue = self.data
                oldprovisional = self.get_provisional_edit(existing_model, user)
                if oldprovisional is not None:
                    oldprovisionalvalue = oldprovisional['value']

                self.data = existing_model.data
                if provisional_edit_log_details == None:
                    provisional_edit_log_details={"user": user, "action": "add edit",  "provisional_editor": user}

            if creating_new_tile == True:
                if self.is_provisional() == False and user_is_reviewer == False:
                    self.apply_provisional_edit(user, data=self.data, action='create')
                    newprovisionalvalue = self.data
                    self.data = {}
                    if provisional_edit_log_details == None:
                        provisional_edit_log_details={"user": user, "action": "create tile",  "provisional_editor": user}

        super(Tile, self).save(*args, **kwargs)
        #We have to save the edit log record after calling save so that the
        #resource's displayname changes are avaliable
        if log == True:
            user = {} if user == None else user
            if creating_new_tile == True:
                self.save_edit(user=user, edit_type=edit_type, old_value={}, new_value=self.data, newprovisionalvalue=newprovisionalvalue, provisional_edit_log_details=provisional_edit_log_details)
            else:
                self.save_edit(
                    user=user,
                    edit_type=edit_type,
                    old_value=existing_model.data,
                    new_value=self.data,
                    newprovisionalvalue=newprovisionalvalue,
                    oldprovisionalvalue=oldprovisionalvalue,
                    provisional_edit_log_details=provisional_edit_log_details
                )

        if index:
            self.index()

        for tile in self.tiles:
            tile.resourceinstance = self.resourceinstance
            tile.parenttile = self
            tile.save(*args, request=request, index=index, **kwargs)


    def delete(self, *args, **kwargs):
        se = SearchEngineFactory().create()
        request = kwargs.pop('request', None)
        provisional_edit_log_details = kwargs.pop('provisional_edit_log_details', None)
        for tile in self.tiles:
            tile.delete(*args, request=request, **kwargs)
        try:
            user = request.user
            user_is_reviewer = request.user.groups.filter(name='Resource Reviewer').exists()
        except AttributeError: #no user
            user = None

        if user_is_reviewer is True or self.user_owns_provisional(user):
            query = Query(se)
            bool_query = Bool()
            bool_query.filter(Terms(field='tileid', terms=[self.tileid]))
            query.add_query(bool_query)
            results = query.search(index='strings', doc_type='term')['hits']['hits']

            for result in results:
                se.delete(index='strings', doc_type='term', id=result['_id'])

            self.__preDelete(request)
            self.save_edit(
                user=request.user,
                edit_type='tile delete',
                old_value=self.data,
                provisional_edit_log_details=provisional_edit_log_details)
            super(Tile, self).delete(*args, **kwargs)
            resource = Resource.objects.get(resourceinstanceid=self.resourceinstance.resourceinstanceid)
            resource.index()

        else:
            self.apply_provisional_edit(user, data={}, action='delete')
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
        datatype_factory = DataTypeFactory()
        for node in nodegroup.node_set.all():
            datatype = datatype_factory.get_instance(node.datatype)
            datatype.after_update_all()
        for tile in self.tiles:
            tile.after_update_all()

    def is_blank(self):
        if self.data != {}:
            if len([item for item in self.data.values() if item != None]) > 0:
                return False

        child_tiles_are_blank = True
        for tile in self.tiles:
            if tile.is_blank() == False:
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

    def __preSave(self, request=None):
        for function in self.__getFunctionClassInstances():
            try:
                function.save(self, request)
            except NotImplementedError:
                pass

    def __preDelete(self, request):
        for function in self.__getFunctionClassInstances():
            try:
                function.delete(self, request)
            except NotImplementedError:
                pass

    def __getFunctionClassInstances(self):
        ret = []
        resource = models.ResourceInstance.objects.get(pk=self.resourceinstance_id)
        functionXgraphs = models.FunctionXGraph.objects.filter(graph_id=resource.graph_id, config__triggering_nodegroups__contains=[str(self.nodegroup_id)])
        for functionXgraph in functionXgraphs:
            func = functionXgraph.function.get_class_module()(functionXgraph.config, self.nodegroup_id)
            ret.append(func)
        return ret

    def filter_by_perm(self, user, perm):
        if user:
            if user.has_perm(perm, self.nodegroup):
                self.tiles = filter(lambda tile: tile.filter_by_perm(user, perm), self.tiles)
            else:
                return None
        return self

    def serialize(self, fields=None, exclude=None):
        """
        serialize to a different form then used by the internal class structure

        """

        ret = JSONSerializer().handle_model(self)
        ret['tiles'] = self.tiles

        return ret
