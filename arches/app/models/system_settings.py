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

from django.conf import LazySettings
from arches.app.models import models


class SystemSettings(LazySettings):
    """
    This class can be used just like you would use settings.py 

    To use, import like you would the django settings module:
        
        from system_settings import settings
        ....
        settings.SEARCH_ITEMS_PER_PAGE 

        # will list all settings
        print settings

    """

    graph_id = 'ff623370-fa12-11e6-b98b-6c4008b05c4c'
    resourceinstanceid = 'a106c400-260c-11e7-a604-14109fd34195'

    def __init__(self, *args, **kwargs):
        super(SystemSettings, self).__init__(*args, **kwargs)
        try: 
            self.update_settings()
        except:
            pass
        #print self

    def __str__(self):
        ret = []
        for setting in dir(self):
            if setting.isupper():
                setting_value = getattr(self, setting)
                ret.append("%s = %s" % (setting, setting_value))
        return '\n'.join(ret)

    def update_settings(self):
        """
        Updates the settings the Arches System Settings graph

        """

        # get all the possible settings defined by the Arches System Settings Graph
        for node in models.Node.objects.filter(graph_id=self.graph_id):
            
            def setup_node(node, parent_node=None):
                if node.is_collector:
                    if node.nodegroup.cardinality == '1':
                        obj = {}
                        for decendant_node in self.get_direct_decendent_nodes(node):
                            obj[decendant_node.name] = setup_node(decendant_node, node)

                        setattr(self, node.name, obj)

                    if node.nodegroup.cardinality == 'n':
                        setattr(self, node.name, [])
                    return getattr(self, node.name)

                if parent_node is not None:
                    setattr(self, node.name, None)

            setup_node(node)

        # set any values saved in the instance of the Arches System Settings Graph 
        for tile in models.TileModel.objects.filter(resourceinstance__graph_id=self.graph_id):
            if tile.nodegroup.cardinality == '1':
                for node in tile.nodegroup.node_set.all():
                    if node.datatype != 'semantic':
                        try:
                            val = tile.data[str(node.nodeid)]
                            setattr(self, node.name, val)
                        except:
                            pass

            if tile.nodegroup.cardinality == 'n':
                obj = {}
                collector_nodename = ''
                for node in tile.nodegroup.node_set.all():
                    # print "%s: %s" % (node.name,node.is_collector)
                    if node.is_collector:
                        collector_nodename = node.name
                    if node.datatype != 'semantic':
                        obj[node.name] = tile.data[str(node.nodeid)]

                # print collector_nodename
                # print obj

                val = getattr(self, collector_nodename)
                val.append(obj)
                setattr(self, collector_nodename, val)

        print self

    @classmethod
    def get_direct_decendent_nodes(cls, node):
        nodes = []
        for edge in models.Edge.objects.filter(domainnode=node):
            nodes.append(edge.rangenode)
        return nodes


settings = SystemSettings()