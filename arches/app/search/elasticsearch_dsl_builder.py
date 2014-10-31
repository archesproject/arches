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

from arches.app.utils.betterJSONSerializer import JSONSerializer

class Dsl(object):
    def __init__(self, dsl={}):
        self.dsl = dsl

    def __str__(self):
        return JSONSerializer().serialize(self.dsl, indent=4) 

    @property
    def dsl(self):
        return self._dsl

    @dsl.setter
    def dsl(self, value):
        try:
            self._dsl = value.dsl
        except AttributeError:
            self._dsl = value      

class Query(Dsl):
    """
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl.html

    """

    def __init__(self, se, **kwargs):
        self.se = se
        self._filtered = False
        self.start = kwargs.pop('start', 0)
        self.limit = kwargs.pop('limit', 10)

        self.dsl = {
            'query': {
                "match_all": { }
            }
        }

    def add_filter(self, dsl={}):
        self._filtered = True
        dsl = Dsl(dsl).dsl

        self.dsl = {
            'query':{
                'filtered':{
                    'query': self.dsl['query'],
                    'filter': dsl
                }
            }
        }

    def add_query(self, dsl={}):
        dsl = Dsl(dsl).dsl

        if self._filtered:
            self.dsl['query']['filtered']['query'] = dsl
        else:
            self.dsl['query'] = dsl

    def search(self, index='', type=''):
        self.dsl['from'] = self.start
        self.dsl['size'] = self.limit
        #print self
        return self.se.search('', index=index, type=type, data=self.dsl)

    def delete(self, index='', type=''):
        self.dsl['from'] = self.start
        self.dsl['size'] = self.limit
        print self
        return self.se.delete(index=index, data=self.dsl)

class Bool(Dsl):
    """
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html
    
    """
    
    def __init__(self, **kwargs):  
        self.dsl = {
            'bool':{
                'should':[],
                'must':[],
                'must_not':[]
            }
        }
        self.should(kwargs.pop('should', None))
        self.must(kwargs.pop('must', None))
        self.must_not(kwargs.pop('must_not', None))
        self.empty = True

    def must(self, dsl):
        return self._append('must', dsl)

    def should(self, dsl):
        return self._append('should', dsl)

    def must_not(self, dsl):
        return self._append('must_not', dsl)

    def _append(self, type, dsl):
        if dsl:
            dsl = Dsl(dsl)
            self.dsl['bool'][type].append(dsl.dsl)
            self.empty = False
        return self


class Match(Dsl):
    """
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-match-query.html
    
    """

    def __init__(self, **kwargs):
        self.type = kwargs.pop('type', 'boolean')
        self.query = kwargs.pop('query', '')
        self.field = kwargs.pop('field', '_all')
        self.fuzziness = kwargs.pop('fuzziness', None)
        self.operator = kwargs.pop('operator', 'or')
        self.max_expansions = kwargs.pop('max_expansions', 10)

        self.dsl = {
            'match' : {
                self.field : {
                    'query' : self.query,
                    'type' : self.type,
                    'operator': self.operator,
                    'max_expansions' : self.max_expansions
                }
            }
        }

        if self.fuzziness and self.type != 'phrase_prefix':
            self.dsl['match'][self.field]['fuzziness'] = self.fuzziness   

class Nested(Dsl):
    """
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-nested-query.html

    Note:
        score_mode can only be used when the nested dsl is used within a queyr but not within a filter

    """

    def __init__(self, **kwargs):
        self.path = kwargs.pop('path', '')
        self.score_mode = kwargs.pop('score_mode', None)
        self.query = kwargs.pop('query', None)

        self.dsl = {
            'nested' : {
                'path' : self.path
            }
        }

        if self.score_mode:
            self.dsl['nested']['score_mode'] = self.score_mode 

        if self.query:
            self.add_query(dsl=self.query)

    def add_query(self, dsl=None):
        if dsl:
            dsl = Dsl(dsl).dsl
            self.dsl['nested']['query'] = dsl

class Terms(Dsl):
    """
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-terms-query.html

    """

    def __init__(self, **kwargs):
        self.field = kwargs.pop('field', '_all')
        self.terms = kwargs.pop('terms', [])

        self.dsl = {
            'terms' : {
                self.field : self.terms
            }
        }


class GeoShape(Dsl):
    """
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-geo-shape-query.html
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/mapping-geo-shape-type.html

    """

    def __init__(self, **kwargs):
        self.field = kwargs.pop('field', '_all')
        self.type = kwargs.pop('type', '')
        self.coordinates = kwargs.pop('coordinates', '')

        self.dsl = {
            'geo_shape': {
                self.field: {
                    'shape': {
                        'type': self.type,
                        'coordinates' : self.coordinates
                    }
                }
            }
        }


class Range(Dsl):
    """
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-range-query.html

    """

    def __init__(self, **kwargs):
        self.field = kwargs.pop('field', '_all')
        self.gte = kwargs.pop('gte', None)
        self.gt = kwargs.pop('gt', None)
        self.lte = kwargs.pop('lte', None)
        self.lt = kwargs.pop('lt', None)
        self.boost = kwargs.pop('boost', '1.0')

        self.dsl = {
            'range' : {
                self.field : {
                    'boost': self.boost
                }
            }
        }

        if self.gte is None and self.gt is None and self.lte is None and self.lt is None:
            raise Exception('You need at least one of the following: gte, gt, lte, or lt')
        if self.gte is not None and self.gt is not None:
            raise Exception('You can only use one of either: gte or gt') 
        if self.lte is not None and self.lt is not None:
            raise Exception('You can only use one of either: lte or lt') 
        
        if self.gte is not None:
            self.dsl['range'][self.field]['gte'] = self.gte
        if self.gt is not None:
            self.dsl['range'][self.field]['gt'] = self.gt
        if self.lte is not None:
            self.dsl['range'][self.field]['lte'] = self.lte
        if self.lt is not None:
            self.dsl['range'][self.field]['lt'] = self.lt

class SimpleQueryString(Dsl):
    """
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-simple-query-string-query.html

    """

    def __init__(self, **kwargs):
        self.field = kwargs.pop('field', '_all') # can be a list of fields
        self.query = kwargs.pop('query', '')
        self.operator = kwargs.pop('operator', 'or')
        self.analyzer = kwargs.pop('analyzer', 'snowball')
        self.flags = kwargs.pop('flags', 'OR|AND|PREFIX')
        #The available flags are: ALL, NONE, AND, OR, PREFIX, PHRASE, PRECEDENCE, ESCAPE, WHITESPACE, FUZZY, NEAR, and SLOP.

        # if not isinstance(self.field, list):
        #     self.field = [self.field]

        self.dsl = {
            'simple_query_string' : {
                'fields' : self.field,
                'query': self.query,
                'default_operator': self.operator,
                'flags': self.flags
            }
        }

        self.dsl = {
            "prefix" : { self.field : self.query }
        }