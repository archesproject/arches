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

import importlib
from arches.app.models import models

class Resource(models.ResourceInstance):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        # from models.ResourceInstance
        # self.resourceinstanceid
        # self.graph
        # self.resourceinstancesecurity
        # end from models.ResourceInstance
        self.tiles = []

    @property
    def primary_name(self):
        module = importlib.import_module('arches.app.functions.resource_functions')
        get_primary_name = getattr(module, 'get_primary_name_from_nodes')
        #{"7a7dfaf5-971e-11e6-aec3-14109fd34195": "Alexei", "7a7e0211-971e-11e6-a67c-14109fd34195": "a55f219a-e126-4f80-a5fd-0282efd43339"}
        # config = {}
        # config['nodegroup_id'] = '7a7dfaf5-971e-11e6-aec3-14109fd34195'
        # config['string_template'] = '{6eeeb00f-9a32-11e6-a0c9-14109fd34195} Type({6eeeb9ca-9a32-11e6-ad09-14109fd34195})'

        #try:
        functionConfig = models.FunctionXGraph.objects.filter(graph=self.graph, function__functiontype='primaryname')
        if len(functionConfig) == 1:
            return get_primary_name(self, functionConfig[0].config)
        else:
            return 'undefined'
        # except:
        #     return 'undefined'
        #{"6eeeb00f-9a32-11e6-a0c9-14109fd34195": "Alexei", "6eeeb9ca-9a32-11e6-ad09-14109fd34195": ""}
        #{"nodegroup_id": "6eeeb00f-9a32-11e6-a0c9-14109fd34195", "string_template": "{6eeeb00f-9a32-11e6-a0c9-14109fd34195} Type({6eeeb9ca-9a32-11e6-ad09-14109fd34195})"}