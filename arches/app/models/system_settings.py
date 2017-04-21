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

from arches.app.models import models
from arches.app.models.models import TileModel


def singleton(cls):
    return cls()

@singleton
class SystemSettings(object):

    graph_id = 'ff623370-fa12-11e6-b98b-6c4008b05c4c'
    resourceinstanceid = 'a106c400-260c-11e7-a604-14109fd34195'
    settings = {}

    def __init__(self, *args, **kwargs):
        self.cache_settings()

    @classmethod
    def get(cls, setting_name):
        return cls.settings[setting_name]
        # tiles = models.TileModel.objects.filter(resourceinstance__graph_id=cls.graph_id)
        # for tile in tiles:
        #     for node in tile.nodegroup.node_set.all():
        #         if node.name == setting_name:
        #             return tile.data[str(node.nodeid)]
        # return None

    @classmethod
    def cache_settings(cls):
        for node in models.Node.objects.filter(graph_id=cls.graph_id):
            if node.datatype != 'semantic':
                cls.settings[node.name] = None
                setattr(cls, node.name, None)

        for tile in models.TileModel.objects.filter(resourceinstance__graph_id=cls.graph_id):
            for node in tile.nodegroup.node_set.all():
                if node.datatype != 'semantic':
                    try:
                        val = tile.data[str(node.nodeid)]
                        cls.settings[node.name] = val
                        setattr(cls, node.name, val)
                    except:
                        pass
