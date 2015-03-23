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
        #return self.resource.get_nodes(entitytypeid, keys=['label', 'value', 'entityid', 'entitytypeid'])
        ret = []
        entities = self.resource.find_entities_by_type_id(entitytypeid)
        for entity in entities:
            ret.append({'nodes': entity.flatten()})

        return ret

    def update_nodes(self, entitytypeid, data, dataKey=None):
        if dataKey == None:
            dataKey = entitytypeid

        self.resource.prune(entitytypes=[entitytypeid])

        if self.schema == None:
            self.schema = Entity.get_mapping_schema(self.resource.entitytypeid)
        for value in data[entitytypeid]:
            baseentity = None
            for newentity in value['nodes']:
                try:
                    entity = Entity()
                    entity.create_from_mapping(self.resource.entitytypeid, self.schema[newentity['entitytypeid']]['steps'], newentity['entitytypeid'], newentity['value'], newentity['entityid'])

                    if baseentity == None:
                        baseentity = entity
                    else:
                        baseentity.merge(entity)
                except:
                    pass
            
            self.resource.merge_at(baseentity, self.resource.entitytypeid)

        self.resource.trim()
