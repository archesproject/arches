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
from django.conf import settings
from arches.app.models import models
from arches.app.models.resource import Resource
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
        self.tiles = {}

        if args:
            if isinstance(args[0], dict):
                for key, value in args[0].iteritems():
                    if not (key == 'tiles'):
                        setattr(self, key, value)

                if self.tileid is None or self.tileid == '':
                    self.tileid = uuid.uuid4()

                if 'tiles' in args[0]:
                    for key, tiles in args[0]['tiles'].iteritems():
                        self.tiles[key] = []
                        for tile_obj in tiles:
                            tile = Tile(tile_obj)
                            tile.parenttile = self
                            self.tiles[key].append(tile)

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        index = kwargs.pop('index', True)
        self.__preSave(request)
        if self.data != {}:
            for nodeid, value in self.data.iteritems():
                datatype_factory = DataTypeFactory()
                datatype = datatype_factory.get_instance(models.Node.objects.get(nodeid=nodeid).datatype)
                datatype.convert_value(self, nodeid)
        super(Tile, self).save(*args, **kwargs)
        if index:
            self.index()
        for tiles in self.tiles.itervalues():
            for tile in tiles:
                tile.resourceinstance = self.resourceinstance
                tile.parenttile = self
                tile.save(*args, request=request, index=index, **kwargs)


    def delete(self, *args, **kwargs):
        se = SearchEngineFactory().create()
        request = kwargs.pop('request', None)
        for tiles in self.tiles.itervalues():
            for tile in tiles:
                tile.delete(*args, request=request, **kwargs)

        query = Query(se)
        bool_query = Bool()
        bool_query.filter(Terms(field='tileid', terms=[self.tileid]))
        query.add_query(bool_query)
        results = query.search(index='strings', doc_type='term')['hits']['hits']
        for result in results:
            se.delete(index='strings', doc_type='term', id=result['_id'])

        self.__preDelete(request)
        super(Tile, self).delete(*args, **kwargs)
        resource = Resource.objects.get(resourceinstanceid=self.resourceinstance.resourceinstanceid)
        resource.index()


    def index(self):
        """
        Indexes all the nessesary documents related to resources to support the map, search, and reports

        """

        Resource.objects.get(pk=self.resourceinstance_id).index()

    def after_update_all(self):
        nodegroup = models.NodeGroup.objects.get(pk=self.nodegroup_id)
        datatype_factory = DataTypeFactory()
        for node in nodegroup.node_set.all():
            datatype = datatype_factory.get_instance(node.datatype)
            datatype.after_update_all()
        for key, tile_list in self.tiles.iteritems():
            for child_tile in tile_list:
                child_tile.after_update_all()

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
            parent_tile.tiles = {}
            for nodegroup in models.NodeGroup.objects.filter(parentnodegroup_id=node.nodegroup.parentnodegroup_id):
                parent_tile.tiles[nodegroup.pk] = [Tile.get_blank_tile_from_nodegroup_id(nodegroup.pk, resourceid=resourceid, parenttile=parent_tile)]
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
        functions = models.FunctionXGraph.objects.filter(graph_id=resource.graph_id, config__triggering_nodegroups__contains=[str(self.nodegroup_id)])
        for function in functions:
            mod_path = function.function.modulename.replace('.py', '')
            module = importlib.import_module('arches.app.functions.%s' % mod_path)
            func = getattr(module, function.function.classname)(function.config, self.nodegroup_id)
            ret.append(func)
        return ret

    def serialize(self):
        """
        serialize to a different form then used by the internal class structure

        """

        ret = JSONSerializer().handle_model(self)
        ret['tiles'] = self.tiles

        return ret
