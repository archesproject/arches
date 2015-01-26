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
from django.conf import settings
from datetime import datetime
from elasticsearch import Elasticsearch, helpers


class SearchEngine(object):

    def __init__(self):
        self.es = Elasticsearch(hosts=settings.ELASTICSEARCH_HOSTS, **settings.ELASTICSEARCH_CONNECTION_OPTIONS)
        self.logger = logging.getLogger(__name__)

    def delete(self, **kwargs):
        """
        Deletes a document from the index
        Pass an index, doc_type, and id to delete a specific document
        Pass a body with a query dsl to delete by query

        """

        body = kwargs.get('body', None)
        if body != None:
            try:
                return self.es.delete_by_query(ignore=[404], **kwargs)
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

        index = kwargs.get('index', '').strip()
        print 'deleting index : %s' % index
        return self.es.indices.delete(index=index, ignore=[400, 404])

    def search(self, **kwargs):
        """
        Search for an item in the index.
        Pass an index, doc_type, and id to get a specific document
        Pass a body with a query dsl to perform a search

        """

        body = kwargs.get('body', None)
        index = kwargs.get('index', None)
        id = kwargs.get('id', None)

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
                result = self.es.get(index='term', doc_type='value', id=_id, ignore=404)

                #print 'result: %s' % result
                if result['found'] == True:
                    ids = result['_source']['ids']
                    if id not in ids:
                        ids.append(id)
                else:
                    ids = [id]

                self.index_data('term', 'value', {'term': term, 'context': context, 'options': options, 'count': len(ids), 'ids': ids}, id=_id)

            except Exception as detail:
                self.logger.warning('%s: WARNING: search failed to index term: %s \nException detail: %s\n' % (datetime.now(), term, detail))
                raise detail   
                  
    def delete_terms(self, entities):
        """
        If the term is referenced more then once simply decrement the 
        count and remove the entity id of the deleted term from the from the existing index.

        If the term is only referenced once then delete the index  

        """

        if not isinstance(entities, list):
            entities = [entities]

        for entity in entities:
            result = self.es.search(index='term', doc_type='value', body={
                "query": {
                    "filtered": {
                        "filter":{
                            "terms": {
                                "ids": [entity.entityid]
                            }
                        }, 
                        "query": {
                            "match_all": {}
                        }
                    }
                }, 
                "from": 0, 
                "size": 10
            }, ignore=404)

            if 'hits' in result:
                for document in result['hits']['hits']:
                    document['_source']['ids'].remove(entity.entityid)
                    count = len(document['_source']['ids'])
                    if count > 0:
                        document['_source']['count'] = count
                        self.index_data('term', 'value', document['_source'], id=document['_id'])
                    else:
                        self.delete(index='term', doc_type='value', id=document['_id'])

    def create_mapping(self, index, doc_type, fieldname='', fieldtype='string', fieldindex='analyzed', body=None):
        """
        Creates an Elasticsearch body for a single field given an index name and type name

        """

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
                body =  { 
                    doc_type : {
                        'properties' : {
                            fieldname : { 'type' : fieldtype, 'index' : fieldindex }
                        }
                    }
                }

        self.create_index(index=index, ignore=400)
        self.es.indices.put_mapping(index=index, doc_type=doc_type, body=body)

    def create_index(self, **kwargs):
        self.es.indices.create(**kwargs)

    def index_data(self, index=None, doc_type=None, body=None, idfield=None, id=None, **kwargs):
        """
        Indexes a document or list of documents into Elasticsearch

        If "id" is supplied then will use that as the id of the document

        If "idfield" is supplied then will try to find that property in the 
            document itself and use the value found for the id of the document

        """

        if not isinstance(body, list):
            body = [body]

        for document in body:
            if idfield is not None:
                if isinstance(document, dict):
                    id = document[idfield]
                else:
                    id = getattr(document,idfield)

            try:
                self.es.index(index=index, doc_type=doc_type, body=document, id=id, **kwargs)
            except Exception as detail:
                self.logger.warning('%s: WARNING: failed to index document: %s \nException detail: %s\n' % (datetime.now(), document, detail))
                raise detail


    def bulk_index(self, data):
        return helpers.bulk(self.es, data, chunk_size=500, raise_on_error=True)

    def create_bulk_item(self, index, type, id, data):
        if not(self.isempty_or_none(index) or self.isempty_or_none(type) or self.isempty_or_none(id)):
            return[
                { "index" : { "_index" : index, "_type" : type, "_id" : id } },
                data
            ]
        else:
            return false