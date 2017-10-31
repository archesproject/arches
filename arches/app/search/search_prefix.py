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

import urllib
import uuid
import logging
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer



class SearchEngine(object):

    def __init__(self):
        #
        serializer = JSONSerializer()
        serializer.mimetype = 'application/json'
        serializer.dumps = serializer.serialize
        serializer.loads = JSONDeserializer().deserialize
        self.es = Elasticsearch(hosts=settings.ELASTICSEARCH_HOSTS, serializer=serializer, **settings.ELASTICSEARCH_CONNECTION_OPTIONS)
        self.logger = logging.getLogger(__name__)
        self.prefix = settings.ELASTICSEARCH_INDEX_PREFIX
    
    def add_prefix(self,index):
        """
        adds a prefix to the index name that is passed to the function. the
        prefix is a property of the class, and by default set to be the app
        name cast to lower().
        """
        if index is None:
            return None
        if self.prefix == '':
            return index
        if self.prefix[0] in ('_','-','+'):
            raise Exception("Invalid index prefix, must not start with '_', '-', or '+'")
        return self.prefix+"-"+index

    def delete(self, **kwargs):
        """
        Deletes a document from the index
        Pass an index, doc_type, and id to delete a specific document
        Pass a body with a query dsl to delete by query
        """

        index = kwargs.get('index', None)
        kwargs['index'] = self.add_prefix(index)
        
        body = kwargs.pop('body', None)
        if body != None:
            try:
                data = []
                refresh = kwargs.pop('refresh', False)
                for hit in helpers.scan(self.es, query=body, **kwargs):
                    hit['_op_type'] = 'delete'
                    data.append(hit)

                return helpers.bulk(self.es, data, refresh=refresh, **kwargs)
            except Exception as detail:
                self.logger.warning('%s: WARNING: failed to delete document by query: %s \nException detail: %s\n' % (datetime.now(), body, detail))
                raise detail
        else:
            try:
                return self.es.delete(ignore=[404], **kwargs)
            except Exception as detail:
                self.logger.warning('%s: WARNING: failed to delete document: %s \nException detail: %s\n' % (datetime.now(), body, detail))
                raise detail

    def delete_index(self, **kwargs):
        """
        Deletes an entire index

        """
        index = kwargs.get('index', None)
        index = self.add_prefix(index)
        
        print 'deleting index : %s' % index
        return self.es.indices.delete(index=index, ignore=[400, 404])

    def search(self, **kwargs):
        """
        Search for an item in the index.
        Pass an index, doc_type, and id to get a specific document
        Pass a body with a query dsl to perform a search

        """

        body = kwargs.get('body', None)
        id = kwargs.get('id', None)
        
        index = kwargs.get('index', None)
        index = self.add_prefix(index)
        kwargs['index'] = index

        if index is None:
            raise NotImplementedError("You must specify an 'index' in your call to search")
            
        if id:
            if isinstance(id, list):
                kwargs.setdefault('body', {'ids': kwargs.pop('id')})
                return self.es.mget(**kwargs)
            else:
                return self.es.get(**kwargs)

        ret = None
        try:
            ret = self.es.search(**kwargs)
        except Exception as detail:
            self.logger.warning('%s: WARNING: search failed for query: %s \nException detail: %s\n' % (datetime.now(), body, detail))
            pass

        return ret

    def create_mapping(self, index, doc_type, fieldname='', fieldtype='string', fieldindex=None, body=None):
        """
        Creates an Elasticsearch body for a single field given an index name and type name
        """
        
        index = self.add_prefix(index)
        fieldindex = self.add_prefix(fieldindex)
        fieldname = self.add_prefix(fieldname)

        if not body:
            if fieldtype == 'geo_shape':
                body =  {
                    doc_type : {
                        'properties' : {
                            fieldname : { 'type' : 'geo_shape', 'tree' : 'geohash', 'precision': '1m' }
                        }
                    }
                }
            else:
                fn = { 'type' : fieldtype }
                if fieldindex:
                    fn['index'] = fieldindex
                body =  {
                    doc_type : {
                        'properties' : {
                            fieldname : fn
                        }
                    }
                }

        self.es.indices.create(index=index, ignore=400)
        self.es.indices.put_mapping(index=index, doc_type=doc_type, body=body)
        print 'creating index : %s/%s' % (index, doc_type)

    def create_index(self, **kwargs):

        index = kwargs.get('index', None)
        kwargs['index'] = self.add_prefix(index)
        
        self.es.indices.create(**kwargs)
        print 'creating index : %s' % kwargs.get('index', '')

    def index_data(self, index=None, doc_type=None, body=None, idfield=None, id=None, **kwargs):
        """
        Indexes a document or list of documents into Elasticsearch

        If "id" is supplied then will use that as the id of the document

        If "idfield" is supplied then will try to find that property in the
            document itself and use the value found for the id of the document

        """
        
        index = self.add_prefix(index)

        if not isinstance(body, list):
            body = [body]

        for document in body:
            if idfield is not None:
                if isinstance(document, dict):
                    id = document[idfield]
                else:
                    id = getattr(document,idfield)

            try:
                self.es.index(index=index, doc_type=doc_type, body=document, id=id)
            except Exception as detail:
                self.logger.warning('%s: WARNING: failed to index document: %s \nException detail: %s\n' % (datetime.now(), document, detail))
                raise detail


    def bulk_index(self, data, **kwargs):
        index = kwargs.get('index', None)
        kwargs['index'] = self.add_prefix(index)
        return helpers.bulk(self.es, data, **kwargs)

    def create_bulk_item(self, op_type='index', index=None, doc_type=None, id=None, data=None):
        index = self.add_prefix(index)
        return {
            '_op_type': op_type,
            '_index': index,
            '_type': doc_type,
            '_id': id,
            '_source': data
        }

    def count(self, **kwargs):
        index = kwargs.get('index', None)
        kwargs['index'] = self.add_prefix(index)
        count = self.es.count(**kwargs)
        if count is not None:
            return count['count']
        else:
            return None

    def BulkIndexer(outer_self, batch_size=500, **kwargs):
    
        index = kwargs.get('index', None)
        kwargs['index'] = outer_self.add_prefix(index)

        class _BulkIndexer(object):
            def __init__(self, **kwargs):
                print kwargs
                index = kwargs.get('index', None)
                kwargs['index'] = outer_self.add_prefix(index)
                print kwargs
                self.queue = []
                self.batch_size = kwargs.pop('batch_size', 500)
                self.kwargs = kwargs

            def add(self, op_type='index', index=None, doc_type=None, id=None, data=None):
                index = outer_self.add_prefix(index)
                print index
                doc = {
                    '_op_type': op_type,
                    '_index': index,
                    '_type': doc_type,
                    '_id': id,
                    '_source': data
                }
                self.queue.append(doc)

                if len(self.queue) >= self.batch_size:
                    outer_self.bulk_index(self.queue, **self.kwargs)
                    del self.queue[:]  #clear out the array
            
            def close(self):
                outer_self.bulk_index(self.queue, **self.kwargs)

            def __enter__(self, **kwargs):
                index = kwargs.get('index', None)
                kwargs['index'] = outer_self.add_prefix(index)
                return self

            def __exit__(self, type, value, traceback):
                return self.close()

        return _BulkIndexer(batch_size=batch_size, **kwargs)
