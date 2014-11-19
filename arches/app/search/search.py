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

    def search(self, q='', **kwargs):
        search_type = kwargs.pop('search_type', None)
        index = kwargs.pop('index', None)
        type = kwargs.pop('type', '_all')
        id = kwargs.pop('id', None)

        if index is None:
            raise NotImplementedError("You must specify an 'index' in your call to search")

        if id:
            path = '%s/%s/%s' % (index, type, id)
            return self.conn.get(path)
        else:
            path = '%s/%s' % (index, type)
            if search_type == None:
                #path = path + '/_search?q="%s"' % q
                path = '%s/%s' % (path, '_search')

        data = kwargs.pop('data', None)
        if data == None:
            data = self.build_search_kwargs(q, **kwargs)
        # print path
        # print JSONSerializer().serialize(data, indent=4)
        return self.conn.post(path, 
            data = data
        )

    def index_terms(self, entities):
        """
        If the term is already indexed, then simply increment the count and add the entity id of the term to the existing index.
        If the term isn't indexed then add the index.

        """

        if not isinstance(entities, list):
            entities = [entities]

        for entity in entities:
            self.index_term(entity.value, entity.entityid, entity.entitytypeid)

    def index_term(self, term, id, options={}):
        """
        If the term is already indexed, then simply increment the count and add the entity id of the term to the existing index.
        If the term isn't indexed then add the index.

        """

        if term.strip(' \t\n\r') != '':
            already_indexed = False
            count = 1
            ids = [id]

            # strip out any non-printable characters then hash the string into a uuid
            try:
                _id = unicode(term, errors='ignore').decode('utf-8').encode('ascii')
            except Exception as detail:
                print "\n\nException detail: %s " % (detail)
                print 'WARNING: failed to index term: %s' % (_id)
                pass

            if _id:
                _id = uuid.uuid3(uuid.NAMESPACE_DNS, _id)
                result = self.conn.get('term/value/%s' % (_id)) #{"_index":"term","_type":"value","_id":"CASTLE MILL","_version":2,"exists":true, "_source" : {"term": "CASTLE MILL"}}

                #print 'result: %s' % result
                if result['found'] == True:
                    ids = result['_source']['ids']
                    if id not in ids:
                        ids.append(id)
                else:
                    ids = [id]

                self.index_data('term', 'value', {'term': term, 'options': options, 'count': len(ids), 'ids': ids}, idfield=None, id=_id)

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

    def build_search_kwargs(self, query_string, sort_by=None, start_offset=0, end_offset=50,
                            search_field='', return_fields='', highlight=False, facets=None,
                            date_facets=None, query_facets=None,
                            narrow_queries=None, spelling_query=None,
                            within=None, dwithin=None, distance_point=None, models=None, 
                            result_class=None, use_phrase=False, use_fuzzy=False, use_wildcard=False, 
                            use_fuzzy_like_this=False, use_range=False):
        
        #index = haystack.connections[self.connection_alias].get_unified_index()
        #search_field = "_all"#index.document_field

        # if query_string == '*:*':
        #     kwargs = {
        #         'query': {
        #             'filtered': {
        #                 'query': {
        #                     "match_all": {}
        #                 },
        #             },
        #         },
        #     }
        # else:
        #     kwargs = {
        #         'query': {
        #             'filtered': {
        #                 'query': {
        #                     'query_string': {
        #                         'default_field': search_field,
        #                         'default_operator': self.default_operator,
        #                         'query': query_string,
        #                         'analyze_wildcard': True,
        #                         'auto_generate_phrase_queries': True,
        #                     },
        #                 },
        #             },
        #         },
        #     }

        # if return_fields:
        #     if isinstance(return_fields, (list, set)):
        #         return_fields = " ".join(return_fields)

        #     kwargs['fields'] = return_fields

        # if sort_by is not None:
        #     order_list = []
        #     for field, direction in sort_by:
        #         if field == 'distance' and distance_point:
        #             # Do the geo-enabled sort.
        #             lng, lat = distance_point['point'].get_coords()
        #             sort_kwargs = {
        #                 "_geo_distance": {
        #                     distance_point['field']: [lng, lat],
        #                     "order": direction,
        #                     "unit": "km"
        #                 }
        #             }
        #         else:
        #             if field == 'distance':
        #                 warnings.warn("In order to sort by distance, you must call the '.distance(...)' method.")

        #             # Regular sorting.
        #             sort_kwargs = {field: {'order': direction}}

        #         order_list.append(sort_kwargs)

        #     kwargs['sort'] = order_list

        # # From/size offsets don't seem to work right in Elasticsearch's DSL. :/
        # # if start_offset is not None:
        # #     kwargs['from'] = start_offset

        # # if end_offset is not None:
        # #     kwargs['size'] = end_offset - start_offset

        # if highlight is True:
        #     kwargs['highlight'] = {
        #         "pre_tags" : ["<span class='searchHighlight'>"],
        #         "post_tags" : ["</span>"],     
        #         'fields': {
        #             search_field: {'store': 'yes'},
        #         }
        #     }

        # # if self.include_spelling is True:
        # #     warnings.warn("Elasticsearch does not handle spelling suggestions.", Warning, stacklevel=2)

        # if narrow_queries is None:
        #     narrow_queries = set()

        # if facets is not None:
        #     kwargs.setdefault('facets', {})

        #     for facet_fieldname in facets:
        #         kwargs['facets'][facet_fieldname] = {
        #             'terms': {
        #                 'field': facet_fieldname,
        #             },
        #         }

        # if date_facets is not None:
        #     kwargs.setdefault('facets', {})

        #     for facet_fieldname, value in date_facets.items():
        #         # Need to detect on gap_by & only add amount if it's more than one.
        #         interval = value.get('gap_by').lower()

        #         # Need to detect on amount (can't be applied on months or years).
        #         if value.get('gap_amount', 1) != 1 and not interval in ('month', 'year'):
        #             # Just the first character is valid for use.
        #             interval = "%s%s" % (value['gap_amount'], interval[:1])

        #         kwargs['facets'][facet_fieldname] = {
        #             'date_histogram': {
        #                 'field': facet_fieldname,
        #                 'interval': interval,
        #             },
        #             'facet_filter': {
        #                 "range": {
        #                     facet_fieldname: {
        #                         'from': self.conn.from_python(value.get('start_date')),
        #                         'to': self.conn.from_python(value.get('end_date')),
        #                     }
        #                 }
        #             }
        #         }

        # if query_facets is not None:
        #     kwargs.setdefault('facets', {})

        #     for facet_fieldname, value in query_facets:
        #         kwargs['facets'][facet_fieldname] = {
        #             'query': {
        #                 'query_string': {
        #                     'query': value,
        #                 }
        #             },
        #         }

        # if limit_to_registered_models is None:
        #     limit_to_registered_models = getattr(settings, 'HAYSTACK_LIMIT_TO_REGISTERED_MODELS', True)

        # if models and len(models):
        #     model_choices = sorted(['%s.%s' % (model._meta.app_label, model._meta.module_name) for model in models])
        # elif limit_to_registered_models:
        #     # Using narrow queries, limit the results to only models handled
        #     # with the current routers.
        #     model_choices = self.build_models_list()
        # else:
        #     model_choices = []

        # if len(model_choices) > 0:
        #     if narrow_queries is None:
        #         narrow_queries = set()

        #     narrow_queries.add('%s:(%s)' % (DJANGO_CT, ' OR '.join(model_choices)))

        # if narrow_queries:
        #     kwargs['query'].setdefault('filtered', {})
        #     kwargs['query']['filtered'].setdefault('filter', {})
        #     kwargs['query']['filtered']['filter'] = {
        #         'fquery': {
        #             'query': {
        #                 'query_string': {
        #                     'query': u' AND '.join(list(narrow_queries)),
        #                 },
        #             },
        #             '_cache': True,
        #         }
        #     }

        # if within is not None:
        #     from haystack.utils.geo import generate_bounding_box

        #     ((min_lat, min_lng), (max_lat, max_lng)) = generate_bounding_box(within['point_1'], within['point_2'])
        #     within_filter = {
        #         "geo_bounding_box": {
        #             within['field']: {
        #                 "top_left": {
        #                     "lat": max_lat,
        #                     "lon": max_lng
        #                 },
        #                 "bottom_right": {
        #                     "lat": min_lat,
        #                     "lon": min_lng
        #                 }
        #             }
        #         },
        #     }
        #     kwargs['query'].setdefault('filtered', {})
        #     kwargs['query']['filtered'].setdefault('filter', {})
        #     if kwargs['query']['filtered']['filter']:
        #         compound_filter = {
        #             "and": [
        #                 kwargs['query']['filtered']['filter'],
        #                 within_filter,
        #             ]
        #         }
        #         kwargs['query']['filtered']['filter'] = compound_filter
        #     else:
        #         kwargs['query']['filtered']['filter'] = within_filter

        # if dwithin is not None:
        #     lng, lat = dwithin['point'].get_coords()
        #     dwithin_filter = {
        #         "geo_distance": {
        #             "distance": dwithin['distance'].km,
        #             dwithin['field']: {
        #                 "lat": lat,
        #                 "lon": lng
        #             }
        #         }
        #     }
        #     kwargs['query'].setdefault('filtered', {})
        #     kwargs['query']['filtered'].setdefault('filter', {})
        #     if kwargs['query']['filtered']['filter']:
        #         compound_filter = {
        #             "and": [
        #                 kwargs['query']['filtered']['filter'],
        #                 dwithin_filter
        #             ]
        #         }
        #         kwargs['query']['filtered']['filter'] = compound_filter
        #     else:
        #         kwargs['query']['filtered']['filter'] = dwithin_filter


        # # Remove the "filtered" key if we're not filtering. Otherwise,
        # # Elasticsearch will blow up.
        # if not kwargs['query']['filtered'].get('filter'):
        #     kwargs['query'] = kwargs['query']['filtered']['query']

        kwargs = {
            'query': {
                "bool":{
                    "should":[],
                    "must":[],
                    "must_not":[]
                }
            },
            "sort":[],
            "facets":{}
        }

        #From/size offsets don't seem to work right in Elasticsearch's DSL. :/
        self.add_limit(kwargs, start_offset, end_offset)

        if query_string == '':
            kwargs['query']['bool']['should'].append({
                "match_all": {}
            })
            return kwargs

        if use_phrase is True:
            if not isinstance(query_string, list):
                query_string = [query_string] 
            for query_string_item in query_string:
                kwargs['query']['bool']['must'].append(self.build_dsl('phrase', search_field, query_string_item))


        if use_fuzzy is True:
            kwargs['query']['bool']['should'].append(self.build_dsl('fuzzy', search_field, query_string, operator='and'))


        if use_range is True:
            kwargs['query']['bool']['must'].append(self.build_dsl('range', search_field, query_string))   


        if use_wildcard is True:
            kwargs['query']['bool']['should'].append(self.build_dsl('wildcard', search_field, query_string))


        if highlight is True:
            kwargs['highlight'] = {
                "pre_tags" : ["<span class='searchHighlight'>"],
                "post_tags" : ["</span>"],     
                'fields': {
                    search_field: {'store': 'yes'},
                }
            }

        return kwargs

    def build_dsl(self, querytype, search_field, query_string, operator='or'):
        if querytype is 'phrase':
            return {
                "match_phrase": {
                    search_field: {
                        "query": query_string
                    }
                }
            }

        if querytype is 'fuzzy':
            return {
                "match": {
                    search_field: {
                        "query": query_string,
                        "operator": operator,
                        "fuzziness": 0.4
                    }
                }
            }

        if querytype is 'wildcard':
            return {
                "wildcard": {
                    search_field: '%s%s' % (query_string, "*")
                }
            }

        if querytype is 'terms':
            return {
                "terms": {
                    search_field: query_string,
                    "execution": operator
                }
            }   

        if querytype is 'range':
            rangefilter = {}
            if 'from' in query_string:
                rangefilter['gte'] = query_string['from']
            if 'to' in query_string:
                rangefilter['lte'] = query_string['to']
            return {
                "range": {
                    search_field: rangefilter
                }
            }

        if querytype is 'geo_shape':
            return {
                "geo_shape": {
                    search_field: {
                        "shape": query_string
                    }
                }
            }

    def range(self, search_field, gte=None, lte=None, gt=None, lt=None):
        if gte is None and gt is None and lte is None and lt is None:
            raise Exception("You need at least one of the following: gte, gt, lte, or lt")
        if gte is not None and gt is not None:
            raise Exception("You can only use one of either: gte or gt") 
        if lte is not None and lt is not None:
            raise Exception("You can only use one of either: lte or lt") 
        
        ret = {search_field: {}}
        if gte is not None:
            ret[search_field]['gte'] = gte
        if gt is not None:
            ret[search_field]['gt'] = gt
        if lte is not None:
            ret[search_field]['lte'] = lte
        if lt is not None:
            ret[search_field]['lt'] = lt
        
        return {'range': ret }

    def bool(self, must=None, should=None, must_not=None):
        if must is None and should is None and must_not is None:
            raise Exception("You need at least one of the following: must, should, or must_not") 
        
        ret = {}
        if must is not None:
            ret['must'] = must
        if should is not None:
            ret['should'] = should
        if must_not is not None:
            ret['must_not'] = must_not
        
        return {'bool': ret }

    def add_limit(self, dsl={}, start_offset=0, end_offset=50):
        dsl['from'] = start_offset
        dsl['size'] = end_offset - start_offset
        return dsl

