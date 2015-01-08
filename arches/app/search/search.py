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

import rawes
import urllib
import uuid
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.conf import settings

class SearchEngine(object):

    def __init__(self, connectionName = 'default', **connection_options):
        self.options = settings.SEARCH_CONNECTION.get(connectionName, {})
        self.port = settings.ELASTICSEARCH_HTTP_PORT
        self.conn = rawes.Elastic(url = '%s:%s' % (self.options['host'], self.port), path='', timeout=self.options['timeout'], connection_type=self.options['connection_type'], connection=None)

    def delete(self, **kwargs):
        index = kwargs.get('index', '').strip()
        type = kwargs.get('type', '').strip()
        id = kwargs.get('id', '').strip()
        data = kwargs.pop('data', None)
        force = kwargs.get('force', False)

        if data != None:
            path = index
            if type is not '':
                path = '%s/%s' % (path, type)

            path = '%s/%s' % (path, '_query')
                
            return self.conn.delete(path, data=data)
        else:

            if (index == '' or type == '' or id == '') and force == False:
                raise NotImplementedError("You must specify an 'index', 'type', and 'id' in your call to delete")

            path = index
            if type is not '':
                path = '%s/%s' % (path, type)
                if id is not '':
                    path = '%s/%s' % (path, id) 
            print 'deleting index by path: %s' % path

            return self.conn.delete(path)

    def search(self, **kwargs):
        data = kwargs.pop('data', None)
        search_type = kwargs.pop('search_type', '_search')
        index = kwargs.pop('index', None)
        type = kwargs.pop('type', None)
        id = kwargs.pop('id', None)

        if index is None:
            raise NotImplementedError("You must specify an 'index' in your call to search")

        if id:
            path = '%s/%s/%s' % (index, type, id)
            return self.conn.get(path)
        
        if type:
            path = '%s/%s' % (index, type)
        else:
            path = index

        path = '%s/%s' % (path, search_type)

        # print path
        # print JSONSerializer().serialize(data, indent=4)

        ret = self.conn.post(path, data=data)
        if 'error' in ret:
            raise Exception(ret)

        return ret

    def index_term(self, term, id, context='', options={}):
        """
        If the term is already indexed, then simply increment the count and add the entity id of the term to the existing index.
        If the term isn't indexed then add the index.

        """

        if term.strip(' \t\n\r') != '':
            already_indexed = False
            count = 1
            ids = [id]
            
            try:
                #_id = unicode(term, errors='ignore').decode('utf-8').encode('ascii')
                _id = uuid.uuid3(uuid.NAMESPACE_DNS, '%s%s' % (hash(term), hash(context)))
                result = self.conn.get('term/value/%s' % (_id)) #{"_index":"term","_type":"value","_id":"CASTLE MILL","_version":2,"exists":true, "_source" : {"term": "CASTLE MILL"}}

                #print 'result: %s' % result
                if result['found'] == True:
                    ids = result['_source']['ids']
                    if id not in ids:
                        ids.append(id)
                else:
                    ids = [id]

                self.index_data('term', 'value', {'term': term, 'context': context, 'options': options, 'count': len(ids), 'ids': ids}, idfield=None, id=_id)

            except Exception as detail:
                print "\n\nException detail: %s " % (detail)
                print 'WARNING: failed to index term: %s' % (term)
                pass            

    def delete_terms(self, entities):
        """
        If the term is referenced more then once simply decrement the 
        count and remove the entity id of the deleted term from the from the existing index.

        If the term is only referenced once then delete the index  

        """

        if not isinstance(entities, list):
            entities = [entities]

        for entity in entities:
            try:
                result = self.conn.get('term/value/%s' % (entity.value)) #{"_index":"term","_type":"value","_id":"CASTLE MILL","_version":2,"exists":true, "_source" : {"term": "CASTLE MILL"}}
                count = result['_source']['count']

                if entity.entityid in result['_source']['ids']:
                    count = len(result['_source']['ids'].remove(entity.entityid))
                    if count > 0:
                        result['_source']['count'] = count
                        self.index_data('term', 'value', result['_source'], idfield=None, id=result['_id'])
                    else:
                        self.delete(index='term', type='value', id=result['_id'])
            except:
                pass

    def create_mapping(self, index, type, fieldname='', fieldtype='string', fieldindex='analyzed', mapping=None):
        """
        Creates an Elasticsearch mapping for a single field given an index name and type name

        """
        if not mapping:
            mapping =  { 
                type : {
                    'properties' : {
                        fieldname : { 'type' : fieldtype, 'index' : fieldindex }
                    }
                }
            }

        if fieldtype == 'geo_shape':
            mapping =  { 
                type : {
                    'properties' : {
                        fieldname : { 'type' : 'geo_shape', 'tree' : 'geohash', 'precision': '1m' }
                    }
                }
            }

        self.index_data(index=index)  
        self.index_data(index=index, type=type, data=mapping, id='_mapping')  

    def index_data(self, index=None, type=None, data=None, idfield=None, id=None):
        """
        Indexes a document or list of documents into Elasticsearch

        If "id" is supplied then will use that as the id of the document

        If "idfield" is supplied then will try to find that property in the 
            document itself and use the value found for the id of the document

        """

        if not isinstance(data, list):
            data = [data]

        for document in data:
            url = ""
            if id is not None:
                url = '%s/%s/%s' % (index, type, id)
            elif idfield is not None:
                if isinstance(document, dict):
                    url = '%s/%s/%s' % (index, type, document[idfield])
                else:
                    url = '%s/%s/%s' % (index, type, getattr(document,idfield))
            elif type is not None:
                url = '%s/%s' % (index, type)
            else:
                url = '%s' % (index)

            #print url
            # print JSONSerializer().serialize(document, indent=4)

            self.conn.post(urllib.quote(url.encode('utf8')),
                data = document, 
                params={
                    'refresh': 'true'
                }
            )

    def bulk_index(self, index, type, data):
        print 'here i am'
        if not(self.isempty_or_none(index) or self.isempty_or_none(type)):
            print 'here i am too'
            # Remember to include the trailing \n character for bulk inserts
            newdata = '\n'.join(map(json.dumps, data))+'\n'
            #newdata = '\n'.join(map(json.dumps, data))+'\n'
            print newdata
            print urllib.quote('%s/%s' % (index, type))
            return self.conn.post(urllib.quote('%s/%s' % (index, type)), 
                data=newdata, 
                params = {
                    'refresh' : 'true'
                }
            )
        else:
            return false

    def create_bulk_item(self, index, type, id, data):
        if not(self.isempty_or_none(index) or self.isempty_or_none(type) or self.isempty_or_none(id)):
            return[
                { "index" : { "_index" : index, "_type" : type, "_id" : id } },
                data
            ]
        else:
            return false