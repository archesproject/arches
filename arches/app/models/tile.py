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

from arches.app.utils.uuid_helpers import uuid_get_or_create
from arches.app.models import models
from django.forms.models import model_to_dict
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
import validations as validation_methods
from arches.app.views.concept import get_preflabel_from_valueid

class Tile(object):
    def __init__(self, *args, **kwargs):
        self.tileid = kwargs.get('tileid', '')
        self.parenttile_id = kwargs.get('parenttile_id', '')
        self.resourceinstance_id = kwargs.get('resourceinstance_id', '')
        self.nodegroup_id = kwargs.get('nodegroup_id', '')
        self.data = kwargs.get('data', {})
        self.sortorder = kwargs.get('sortorder', {})
        self.tiles = kwargs.get('tiles', {})

        if len(args) != 0:
            if isinstance(args[0], basestring):
                self.load(JSONDeserializer().deserialize(args[0]))
            elif isinstance(args[0], models.Tile):
                self.map(args[0])
            elif args[0] != None and isinstance(args[0], object):
                self.load(args[0])

    def load(self, obj):
        """
        Populate an Tile instance from a generic python object

        """

        self.tileid = obj.get('tileid', '')
        self.parenttile_id = obj.get('parenttile_id', '')
        self.resourceinstance_id = obj.get('resourceinstance_id', '')
        self.nodegroup_id = obj.get('nodegroup_id', '')
        self.data = obj.get('data', {})
        self.sortorder = obj.get('sortorder', {})
        if not isinstance(self.data, dict):
            self.data = {}
        self.tiles = {}
        for nodegroup_id, tiles in obj.get('tiles', {}).iteritems():
            self.tiles[nodegroup_id] = []
            for tile in tiles:
                self.tiles[nodegroup_id].append(Tile(tile))
        return self

    @classmethod
    def get(cls, **kwargs):
        #tile = models.Tile.objects.get(**kwargs)
        ret = Tile(models.Tile.objects.get(**kwargs))
        return ret

    def get_nodes(self):
        return models.Node.objects.filter(nodegroup_id=self.nodegroup_id)

    def validate(self):
        functions = {'is_valid': True}
        for node in self.get_nodes():
            results = []
            node_is_valid = True
            value = None
            if str(node.nodeid) in self.data:
                value = self.data[str(node.nodeid)]
            for function in node.functions.all():
                validation_method = getattr(validation_methods, function.function)
                result = validation_method(value, node.nodeid, self.tileid)
                if not result['valid']:
                    functions['is_valid'] = False
                    node_is_valid = False
                results.append(result)
            functions[str(node.nodeid)] = {'results': results, 'is_valid': node_is_valid}
        return functions

    def get_node_display_values(self):
        for nodeid, nodevalue in self.data.iteritems():
            if models.Node.objects.get(pk=nodeid).datatype == 'concept':
                self.data[nodeid] = get_preflabel_from_valueid(nodevalue, 'en-US')['value']

        return self.data

    def save(self):
        self.tileid, created = uuid_get_or_create(self.tileid)
        tile, created = models.Tile.objects.update_or_create(
            tileid = self.tileid,
            defaults = {
                'nodegroup_id': self.nodegroup_id,
                'data': self.data,
                'resourceinstance_id': self.resourceinstance_id,
                'parenttile_id': self.parenttile_id
            }
        )

        for key, tiles in self.tiles.iteritems():
            for childtile in tiles:
                childtile.parenttile_id = tile.tileid
                childtile.save()

    # @classmethod
    # def aggregate(cls, queryset, aggregate=False):
    #     ret = {} if aggregate else []

    #     if aggregate:
    #         for tile in queryset:
    #             if t.nodegroup not in ret:
    #                 ret[str(tile.nodegroup_id)] = []
    #             ret[str(tile.nodegroup_id)].append(cls._map(tile))
    #     else:
    #         for tile in queryset:
    #             ret.append(cls._map(tile))

    #     return ret

    def map(self, ormTile):
        self.tileid = ormTile.tileid
        self.parenttile_id = ormTile.parenttile_id
        self.resourceinstance_id = ormTile.resourceinstance_id
        self.nodegroup_id = ormTile.nodegroup_id
        self.data = ormTile.data
        return self
