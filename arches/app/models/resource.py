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
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

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
    def primaryname(self):
        module = importlib.import_module('arches.app.functions.resource_functions')
        PrimaryNameFunction = getattr(module, 'PrimaryNameFunction')()
        #{"7a7dfaf5-971e-11e6-aec3-14109fd34195": "Alexei", "7a7e0211-971e-11e6-a67c-14109fd34195": "a55f219a-e126-4f80-a5fd-0282efd43339"}
        # config = {}
        # config['nodegroup_id'] = '7a7dfaf5-971e-11e6-aec3-14109fd34195'
        # config['string_template'] = '{6eeeb00f-9a32-11e6-a0c9-14109fd34195} Type({6eeeb9ca-9a32-11e6-ad09-14109fd34195})'

        #try:
        functionConfig = models.FunctionXGraph.objects.filter(graph=self.graph, function__functiontype='primaryname')
        if len(functionConfig) == 1:
            return PrimaryNameFunction.get(self, functionConfig[0].config)
        else:
            return 'undefined'
        # except:
        #     return 'undefined'
        #{"6eeeb00f-9a32-11e6-a0c9-14109fd34195": "Alexei", "6eeeb9ca-9a32-11e6-ad09-14109fd34195": ""}
        #{"nodegroup_id": "6eeeb00f-9a32-11e6-a0c9-14109fd34195", "string_template": "{6eeeb00f-9a32-11e6-a0c9-14109fd34195} Type({6eeeb9ca-9a32-11e6-ad09-14109fd34195})"}

    def index(self):
        """
        Indexes all the nessesary documents related to resources to support the map, search, and reports

        """

        se = SearchEngineFactory().create()

        search_documents = self.prepare_documents_for_search_index()
        for document in search_documents:
            se.index_data('resource', self.graph_id, document, id=self.pk)

        # for term in self.prepare_terms_for_search_index():
        #     term_id = '%s_%s' % (str(self.tileid), str(term['nodeid']))
        #     se.delete_terms(term_id)
        #     se.index_term(term['term'], term_id, term['context'], term['options'])

    def prepare_documents_for_search_index(self):
        """
        Generates a list of specialized resource based documents to support resource search

        """

        document = JSONSerializer().serializeToPython(self)
        document['tiles'] = models.TileModel.objects.filter(resourceinstance=self)
        document['strings'] = []
        document['dates'] = []
        document['domains'] = []
        document['geometries'] = []
        document['numbers'] = []

        for tile in document['tiles']:
            for nodeid, nodevalue in tile.data.iteritems():
                node = models.Node.objects.get(pk=nodeid)
                if nodevalue != '' and nodevalue != [] and nodevalue != {} and nodevalue is not None:
                    if node.datatype == 'string':
                        document['strings'].append(nodevalue)
                    elif node.datatype == 'concept' or node.datatype == 'concept-list':
                        if node.datatype == 'concept':
                            nodevalue = [nodevalue]
                        for concept_valueid in nodevalue:
                            value = models.Value.objects.get(pk=concept_valueid)
                            document['domains'].append({'label': value.value, 'conceptid': value.concept_id, 'valueid': concept_valueid})
                    elif node.datatype == 'date':
                        document['dates'].append(nodevalue)
                    elif node.datatype == 'geojson-feature-collection':
                        document['geometries'].append(nodevalue)
                    elif node.datatype == 'number':
                        document['numbers'].append(nodevalue)

        return [JSONSerializer().serializeToPython(document)]

    def serialize(self):
        """
        serialize to a different form then used by the internal class structure

        used to append additional values (like parent ontology properties) that
        internal objects (like models.Nodes) don't support

        """

        ret = JSONSerializer().handle_model(self)
        ret['tiles'] = self.tiles

        return JSONSerializer().serializeToPython(ret)
