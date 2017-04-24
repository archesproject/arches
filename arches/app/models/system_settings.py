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
        
        from system_settings import SystemSettings
        ....
        SystemSettings.SEARCH_ITEMS_PER_PAGE 

        # will list all settings
        print SystemSettings

    """

    graph_id = 'ff623370-fa12-11e6-b98b-6c4008b05c4c'
    resourceinstanceid = 'a106c400-260c-11e7-a604-14109fd34195'
    settings = {} # includes all settings including methods and private attributes defined in settings.py

    def __init__(self, *args, **kwargs):
        self.cache_settings()
        print self

    def __str__(self):
        ret = []
        for item in sorted(self.settings.iteritems(), key=lambda item: item[0], reverse=False):
            ret.append("%s = %s" % (item[0], item[1]))
        return '\n'.join(ret)

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
            # if not setting.startswith('__') and not callable(getattr(core_settings,setting)):
            #     setattr(cls, setting, getattr(core_settings, setting))

        # get all the possible settings defined by the Arches System Settings Graph
        for node in models.Node.objects.filter(graph_id=cls.graph_id):
            # if node.datatype != 'semantic':
            #     cls.settings[node.name] = None
            #     setattr(cls, node.name, None)
            def setup_node(node, parent_node=None):
                if node.is_collector:
                    if node.nodegroup.cardinality == '1':
                        obj = {}
                        for decendant_node in cls.get_direct_decendent_nodes(node):
                            # setup_node(decendant_node)
                            # if decendant_node.name not in cls.settings:
                            #     cls.settings[decendant_node.name] = None
                            #     setattr(cls, decendant_node.name, None)
                            obj[decendant_node.name] = setup_node(decendant_node, node)

                        cls.settings[node.name] = obj
                        #setattr(cls, node.name, obj)

                    if node.nodegroup.cardinality == 'n':
                        cls.settings[node.name] = []
                        #setattr(cls, node.name, [])
                    return cls.settings[node.name]

                if parent_node is not None:
                    cls.settings[node.name] = None
                    #setattr(cls, node.name, None)

            setup_node(node)

        # set any values saved in the instance of the Arches System Settings Graph 
        for tile in models.TileModel.objects.filter(resourceinstance__graph_id=cls.graph_id):
            if tile.nodegroup.cardinality == '1':
                for node in tile.nodegroup.node_set.all():
                    if node.datatype != 'semantic':
                        try:
                            val = tile.data[str(node.nodeid)]
                            cls.settings[node.name] = val
                            #setattr(cls, node.name, val)
                        except:
                            pass

            if tile.nodegroup.cardinality == 'n':
                obj = {}
                collector_nodename = ''
                for node in tile.nodegroup.node_set.all():
                    print "%s: %s" % (node.name,node.is_collector)
                    if node.is_collector:
                        collector_nodename = node.name
                    if node.datatype != 'semantic':
                        obj[node.name] = tile.data[str(node.nodeid)]
                    # try:
                    #     #val = tile.data[str(node.nodeid)]
                    #     obj[node.name] = tile.data[str(node.nodeid)]
                    #     # cls.settings[node.name] = val
                    #     # setattr(cls, node.name, val)
                    # except:
                    #     pass

                print collector_nodename
                print obj

                cls.settings[collector_nodename].append(obj)
                #setattr(cls, collector_nodename, ret)

        for key, setting in cls.settings.iteritems():
            if not key.startswith('__') and not callable(cls.settings[key]):
                setattr(cls, key, setting)

        print cls


    @classmethod
    def get_direct_decendent_nodes(cls, node):
        nodes = []
        for edge in models.Edge.objects.filter(domainnode=node):
            nodes.append(edge.rangenode)
        return nodes

    # @classmethod
    # def serialize(cls):
    #     nodes = models.Node.objects.filter(graph_id=cls.graph_id)
    #     edges = models.Edge.objects.filter(graph_id=cls.graph_id)
    #     for node in 


