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

from django.conf import settings as core_settings
from arches.app.models import models
from arches.app.models.models import TileModel


def singleton(cls):
    return cls()

@singleton
class SystemSettings(object):
    """
    This class can be used just like you would use settings.py 

    This class is a singleton and doesn't need to be instantiated

    To use, import like you would the django settings module:
        
        from system_settings import SystemSettings as settings
        ....
        settings.SEARCH_ITEMS_PER_PAGE 

    """

    graph_id = 'ff623370-fa12-11e6-b98b-6c4008b05c4c'
    resourceinstanceid = 'a106c400-260c-11e7-a604-14109fd34195'
    settings = {} # includes all settings including methods and private attributes defined in settings.py

    def __init__(self, *args, **kwargs):
        print 'init System Settings'
        self.cache_settings()

    @classmethod
    def get(cls, setting_name):
        """
        Used to retrieve any setting, even callable methods defined in settings.py

        """

        return cls.settings[setting_name]

    @classmethod
    def cache_settings(cls):
        """
        Updates the current cache of settings defined in settings.py and in the Arches System Settings graph

        """

        # load all the settings from settings.py
        for setting in dir(core_settings):
            cls.settings[setting] = getattr(core_settings, setting)
            if not setting.startswith('__') and not callable(getattr(core_settings,setting)):
                setattr(cls, setting, getattr(core_settings, setting))

        # get all the possible settings defined by the Arches System Settings Graph
        for node in models.Node.objects.filter(graph_id=cls.graph_id):
            if node.datatype != 'semantic':
                cls.settings[node.name] = None
                setattr(cls, node.name, None)

        # set any values saved in the instance of the Arches System Settings Graph 
        for tile in models.TileModel.objects.filter(resourceinstance__graph_id=cls.graph_id):
            for node in tile.nodegroup.node_set.all():
                if node.datatype != 'semantic':
                    try:
                        val = tile.data[str(node.nodeid)]
                        cls.settings[node.name] = val
                        setattr(cls, node.name, val)
                    except:
                        pass
