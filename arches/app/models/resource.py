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
import importlib
from django.db.models import Q
from django.conf import settings
from arches.app.models import models
from arches.app.models.models import TileModel
from arches.app.models.concept import get_preflabel_from_valueid
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Bool, Terms
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.datatypes.datatypes import DataTypeFactory
from django.db import transaction


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

    def get_descriptor(self, descriptor):
        module = importlib.import_module('arches.app.functions.primary_descriptors')
        PrimaryDescriptorsFunction = getattr(module, 'PrimaryDescriptorsFunction')()
        functionConfig = models.FunctionXGraph.objects.filter(graph_id=self.graph_id, function__functiontype='primarydescriptors')
        if len(functionConfig) == 1:
            return PrimaryDescriptorsFunction.get_primary_descriptor_from_nodes(self, functionConfig[0].config[descriptor])
        else:
            return 'undefined'

    @property
    def displaydescription(self):
        return self.get_descriptor('description')

    @property
    def map_popup(self):
        return self.get_descriptor('map_popup')

    @property
    def displayname(self):
        return self.get_descriptor('name')

    def save(self, *args, **kwargs):
        """
        Saves and indexes a single resource

        """

        super(Resource, self).save(*args, **kwargs)
        for tile in self.tiles:
            tile.resourceinstance_id = self.resourceinstanceid
            saved_tile = tile.save(index=False)
        self.index()

    @staticmethod
    def bulk_save(resources):
        """
        Saves and indexes a list of resources

        Arguments:
        resources -- a list of resource models

        """

        se = SearchEngineFactory().create()
        datatype_factory = DataTypeFactory()
        node_datatypes = {str(nodeid): datatype for nodeid, datatype in models.Node.objects.values_list('nodeid', 'datatype')}
        tiles = []
        documents = []
        term_list = []

        # flatten out the nested tiles into a single array
        for resource in resources:
            for parent_tile in resource.tiles:
                for child_tile in parent_tile.tiles.itervalues():
                    if len(child_tile) > 0:
                        resource.tiles.extend(child_tile)
                parent_tile.tiles = {}

            tiles.extend(resource.tiles)

        # need to save the models first before getting the documents for index
        Resource.objects.bulk_create(resources)
        TileModel.objects.bulk_create(tiles)

        for resource in resources:
            document, terms = resource.get_documents_to_index(fetchTiles=False, datatype_factory=datatype_factory, node_datatypes=node_datatypes)
            documents.append(se.create_bulk_item(index='resource', doc_type=document['graph_id'], id=document['resourceinstanceid'], data=document))
            for term in terms:
                term_list.append(se.create_bulk_item(index='strings', doc_type='term', id=uuid.uuid4(), data=term))

        # bulk index the resources, tiles and terms
        se.bulk_index(documents)
        se.bulk_index(term_list)

    def index(self):
        """
        Indexes all the nessesary items values of a resource to support search

        """

        se = SearchEngineFactory().create()
        datatype_factory = DataTypeFactory()
        node_datatypes = {str(nodeid): datatype for nodeid, datatype in models.Node.objects.values_list('nodeid', 'datatype')}

        document, terms = self.get_documents_to_index(datatype_factory=datatype_factory, node_datatypes=node_datatypes)
        se.index_data('resource', self.graph_id, JSONSerializer().serializeToPython(document), id=self.pk)

        for term in terms:
            se.index_data('strings', 'term', term, id=unicode(term['nodeid'])+unicode(term['tileid']))

    def get_documents_to_index(self, fetchTiles=True, datatype_factory=None, node_datatypes=None):
        """
        Gets all the documents nessesary to index a single resource
        returns a tuple of a document and list of terms

        Keyword Arguments:
        fetchTiles -- instead of fetching the tiles from the database get them off the model itself
        datatype_factory -- refernce to the DataTypeFactory instance
        node_datatypes -- a dictionary of datatypes keyed to node ids

        """

        document = JSONSerializer().serializeToPython(self)
        document['tiles'] = models.TileModel.objects.filter(resourceinstance=self) if fetchTiles else self.tiles
        document['strings'] = []
        document['dates'] = []
        document['domains'] = []
        document['geometries'] = []
        document['points'] = []
        document['numbers'] = []

        terms = []

        for tile in document['tiles']:
            for nodeid, nodevalue in tile.data.iteritems():
                datatype = node_datatypes[nodeid]
                if nodevalue != '' and nodevalue != [] and nodevalue != {} and nodevalue is not None:
                    datatype_instance = datatype_factory.get_instance(datatype)
                    datatype_instance.append_to_document(document, nodevalue)
                    term = datatype_instance.get_search_term(nodevalue)
                    if term is not None:
                        terms.append({'value': term, 'nodeid': nodeid, 'nodegroupid': tile.nodegroup_id, 'tileid': tile.tileid, 'resourceinstanceid':tile.resourceinstance_id})

        return document, terms

    def delete(self):
        """
        Deletes a single resource and any related indexed data

        """

        se = SearchEngineFactory().create()
        related_resources = self.get_related_resources(lang="en-US", start=0, limit=15)
        for rr in related_resources['resource_relationships']:
            models.ResourceXResource.objects.get(pk=rr['resourcexid']).delete()
        query = Query(se)
        bool_query = Bool()
        bool_query.filter(Terms(field='resourceinstanceid', terms=[self.resourceinstanceid]))
        query.add_query(bool_query)
        results = query.search(index='strings', doc_type='term')['hits']['hits']
        for result in results:
            se.delete(index='strings', doc_type='term', id=result['_id'])
        se.delete(index='resource', doc_type=str(self.graph_id), id=self.resourceinstanceid)
        super(Resource, self).delete()

    def get_related_resources(self, lang='en-US', limit=1000, start=0):
        """
        Returns an object that lists the related resources, the relationship types, and a reference to the current resource

        """

        ret = {
            'resource_instance': self,
            'resource_relationships': [],
            'related_resources': []
        }
        se = SearchEngineFactory().create()
        query = Query(se, limit=limit, start=start)
        bool_filter = Bool()
        bool_filter.should(Terms(field='resourceinstanceidfrom', terms=self.resourceinstanceid))
        bool_filter.should(Terms(field='resourceinstanceidto', terms=self.resourceinstanceid))
        query.add_query(bool_filter)
        resource_relations = query.search(index='resource_relations', doc_type='all')
        ret['total'] = resource_relations['hits']['total']
        instanceids = set()
        for relation in resource_relations['hits']['hits']:
            relation['_source']['preflabel'] = get_preflabel_from_valueid(relation['_source']['relationshiptype'], lang)
            ret['resource_relationships'].append(relation['_source'])
            instanceids.add(relation['_source']['resourceinstanceidto'])
            instanceids.add(relation['_source']['resourceinstanceidfrom'])
        if len(instanceids) > 0:
            instanceids.remove(str(self.resourceinstanceid))

        related_resources = se.search(index='resource', doc_type='_all', id=list(instanceids))
        if related_resources:
            for resource in related_resources['docs']:
                ret['related_resources'].append(resource['_source'])

        return ret

    def serialize(self):
        """
        Serialize to a different form then used by the internal class structure

        used to append additional values (like parent ontology properties) that
        internal objects (like models.Nodes) don't support

        """

        ret = JSONSerializer().handle_model(self)
        ret['tiles'] = self.tiles

        return JSONSerializer().serializeToPython(ret)
