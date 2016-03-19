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

import uuid
from arches.app.models import models
from django.forms.models import model_to_dict
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

class Tile(object):
    def __init__(self, *args, **kwargs):
        self.tileid = kwargs.get('tileid', '')
        self.parenttile_id = kwargs.get('parenttile_id', '')
        self.resourceinstance_id = kwargs.get('resourceinstance_id', '')
        self.nodegroup_id = kwargs.get('nodegroup_id', '')
        self.data = kwargs.get('data', {})
        self.tiles = kwargs.get('tiles', {})

        if len(args) != 0:
            if isinstance(args[0], basestring):
                self.load(JSONDeserializer().deserialize(args[0]))  
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
        if not isinstance(self.data, dict):
            self.data = {}
        self.tiles = {}
        for nodegroup_id, tiles in obj.get('tiles', {}).iteritems():
            self.tiles[nodegroup_id] = []
            for tile in tiles:
                self.tiles[nodegroup_id].append(Tile(tile))
        return self

    def save(self):
        self.tileid, created = uuid.get_or_create(self.tileid)
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


    @classmethod    
    def aggregate(cls, queryset, aggregate=False):
        ret = {} if aggregate else []

        if aggregate:
            for tile in queryset:
                if t.nodegroup not in ret:
                    ret[str(tile.nodegroup_id)] = []
                ret[str(tile.nodegroup_id)].append(cls._map(tile))
        else:
            for tile in queryset:
                ret.append(cls._map(tile))

        return ret

    @classmethod 
    def _map(cls, ormTile):
        t = Tile()
        t.tileid = ormTile.tileid
        t.parenttile_id = ormTile.parenttile_id
        t.resourceinstance_id = ormTile.resourceinstance_id
        t.nodegroup_id = ormTile.nodegroup_id
        t.data = ormTile.data
        return t



# # Move to util function
# def get(id):
#     try:
#         uuid.UUID(id)
#         return uuid.UUID(id), False
#     except(ValueError, TypeError):
#         return uuid.uuid4(), True


# uuid.get_or_create = get