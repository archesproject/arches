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

from arches.app.models.entity import Entity

class ResourceForm(object):
    def __init__(self, resource):
        # here is where we can create the basic format for the form data
        info = self.get_info()
        self.id = info['id']
        self.name = info['name']
        self.icon = info['icon']
        self.resource = resource
        
        self.data = {
            "domains": {},
            "defaults": {}
        }

    @property
    def schema(self):
        try:
            return self._schema
        except AttributeError:
            self._schema = Entity.get_mapping_schema(self.resource.entitytypeid)
            return self._schema
    
    @staticmethod
    def get_info():
        return {
            'id': '',
            'icon': '',
            'name': '',
            'class': ResourceForm
        }

    def update(self, data):
        # update resource w/ post data
        return 

    def load(self):
        # retrieves the data from the server
        return 

    def get_nodes(self, entitytypeid):
        return self.resource.get_nodes(entitytypeid, keys=['label', 'value', 'entityid'])

    def update_nodes(self, entitytypeid, data):
        for entity in self.resource.find_entities_by_type_id(entitytypeid):
            self.resource.child_entities.remove(entity)

        if self.schema == None:
            self.schema = Entity.get_mapping_schema(self.resource.entitytypeid)
        for value in data[entitytypeid.replace('.', '_')]:
            baseentity = None
            for newentity in self.decode_data_item(value):
                entity = Entity()
                entity.create_from_mapping(self.resource.entitytypeid, self.schema[newentity['entitytypeid']]['steps'], newentity['entitytypeid'], newentity['value'], newentity['entityid'])

                if baseentity == None:
                    baseentity = entity
                else:
                    baseentity.merge(entity)
            
            self.resource.merge_at(baseentity, self.resource.entitytypeid)

    def update_node(self, entitytypeid, data):
        if self.schema == None:
            self.schema = Entity.get_mapping_schema(self.resource.entitytypeid)
        nodes = self.resource.find_entities_by_type_id(entitytypeid)
        node_data = self.decode_data_item(data[entitytypeid.replace('.', '_')])[0]

        if len(nodes) == 0:
            entity = Entity()
            entity.create_from_mapping(self.resource.entitytypeid, self.schema[entitytypeid]['steps'], entitytypeid, node_data['value'], node_data['entityid'])
            self.resource.merge_at(entity, self.resource.entitytypeid)
        else:
            nodes[0].value = node_data['value']

    def decode_data_item(self, entity):
        def dec(item):
            # item = "NAME_E41__entitytypeid"
            val = item.split('__')
            if len(val) != 2:
                return False
            entitytypeid = val[0]
            propertyname = val[1]
            
            v = entitytypeid.split('_')
            entitytypeid = '%s.%s' % ('_'.join(v[:-1]), v[-1])
            return (entitytypeid, propertyname)

        ret = {}
        for key, value in entity.iteritems():
            r = dec(key)
            if r:
                if r[0] not in ret:
                    ret[r[0]] = {}
                ret[r[0]][r[1]] = value

        ret2 = []
        for key, value in ret.iteritems():
            value['entitytypeid'] = key
            ret2.append(value)
        return ret2
