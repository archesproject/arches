"""
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
"""

from arches.app.utils.betterJSONSerializer import JSONSerializer
from django.utils.translation import ugettext as _


class Dsl(object):
    def __init__(self, dsl=None):
        if dsl is None:
            self.dsl = {}
        else:
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
    http://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html

    """

    def __init__(self, se, **kwargs):
        self.se = se
        self.start = kwargs.pop("start", 0)
        self.limit = kwargs.pop("limit", 10)
        self.scroll = None

        self.dsl = {"query": {"match_all": {}}, "_source": {"includes": [], "excludes": []}}

        for key, value in kwargs.items():
            self.dsl[key] = value

    def add_query(self, dsl=None):
        if dsl is not None:
            dsl = Dsl(dsl).dsl

        if "bool" in dsl and "bool" in self.dsl["query"]:
            self.dsl["query"] = Bool(self.dsl["query"]).merge(dsl).dsl
        else:
            self.dsl["query"] = dsl

    def add_aggregation(self, agg=None):
        if agg is not None:
            if "aggs" not in self.dsl:
                self.dsl["aggs"] = {}

            self.dsl["aggs"][agg.name] = agg.agg[agg.name]

    def include(self, include):
        self.dsl["_source"]["includes"].append(include)

    def exclude(self, exclude):
        self.dsl["_source"]["excludes"].append(exclude)

    def min_score(self, min_score):
        self.dsl["min_score"] = min_score

    def search(self, index="", **kwargs):
        self.start = kwargs.pop("start", self.start)
        self.limit = kwargs.pop("limit", self.limit)
        self.scroll = kwargs.pop("scroll", None)
        self.prepare()
        if self.scroll is None:
            return self.se.search(index=index, body=self.dsl, id=kwargs.get("id", None))
        else:
            return self.se.search(index=index, body=self.dsl, scroll=self.scroll)

    def count(self, index="", **kwargs):
        return self.se.count(index=index, body=self.dsl)

    def delete(self, index="", **kwargs):
        return self.se.delete(index=index, body=self.dsl, **kwargs)

    def prepare(self, scroll=False):
        if self.scroll is None:
            self.dsl["from"] = self.start
        self.dsl["size"] = self.limit


class Bool(Dsl):
    """
    http://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html

    """

    def __init__(self, dsl=None, **kwargs):
        self.dsl = {"bool": {"should": [], "must": [], "must_not": [], "filter": []}}
        if isinstance(dsl, dict):
            self.dsl["bool"] = dsl["bool"]
        elif isinstance(dsl, Bool):
            self = dsl

        self.should(kwargs.pop("should", None))
        self.must(kwargs.pop("must", None))
        self.must_not(kwargs.pop("must_not", None))
        self.filter(kwargs.pop("filter", None))
        self.empty = True

    def must(self, dsl):
        return self._append("must", dsl)

    def should(self, dsl):
        if dsl and "minimum_should_match" not in self.dsl["bool"]:
            self.dsl["bool"]["minimum_should_match"] = 1
        return self._append("should", dsl)

    def must_not(self, dsl):
        return self._append("must_not", dsl)

    def filter(self, dsl):
        return self._append("filter", dsl)

    def _append(self, type, dsl):
        if dsl:
            dsl = Dsl(dsl)
            self.dsl["bool"][type].append(dsl.dsl)
            self.empty = False
        return self

    def merge(self, object):
        if isinstance(object, dict):
            object = Bool(object)

        self.dsl["bool"]["must"] = self.dsl["bool"]["must"] + object.dsl["bool"]["must"]
        self.dsl["bool"]["should"] = self.dsl["bool"]["should"] + object.dsl["bool"]["should"]
        self.dsl["bool"]["must_not"] = self.dsl["bool"]["must_not"] + object.dsl["bool"]["must_not"]
        self.dsl["bool"]["filter"] = self.dsl["bool"]["filter"] + object.dsl["bool"]["filter"]

        return self


class Match(Dsl):
    """
    http://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html

    """

    def __init__(self, **kwargs):
        self.type = kwargs.pop("type", "match")
        self.field = kwargs.pop("field", "_all")
        # self.query = kwargs.pop('query', '')
        # self.fuzziness = kwargs.pop('fuzziness', None)
        # self.fuzzy_transpositions = kwargs.pop('fuzzy_transpositions', True)
        # self.fuzzy_rewrite = kwargs.pop('fuzzy_rewrite', 'constant_score')
        # self.prefix_length = kwargs.pop('prefix_length', None)
        # self.operator = kwargs.pop('operator', 'or')
        # self.max_expansions = kwargs.pop('max_expansions', 10)
        # self.zero_terms_query = kwargs.pop('zero_terms_query', None)
        # self.cutoff_frequency = kwargs.pop('cutoff_frequency', 1)
        # self.auto_generate_synonyms_phrase_query = kwargs.pop('auto_generate_synonyms_phrase_query', True)

        if self.type != "match":
            self.type = "match_%s" % self.type

        parameters = {}
        for key, value in kwargs.items():
            parameters[key] = value

        self.dsl = {self.type: {self.field: parameters}}


class Nested(Dsl):
    """
    http://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-nested-query.html

    Note:
        score_mode can only be used when the nested dsl is used within a query but not within a filter

    """

    def __init__(self, **kwargs):
        self.path = kwargs.pop("path", "")
        self.score_mode = kwargs.pop("score_mode", None)
        self.query = kwargs.pop("query", None)

        self.dsl = {"nested": {"path": self.path}}

        if self.score_mode:
            self.dsl["nested"]["score_mode"] = self.score_mode

        if self.query:
            self.add_query(dsl=self.query)

    def add_query(self, dsl=None):
        if dsl:
            dsl = Dsl(dsl).dsl
            self.dsl["nested"]["query"] = dsl


class Term(Dsl):
    """
    https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-term-query.html

    """

    def __init__(self, **kwargs):
        self.field = kwargs.pop("field", "_all")
        self.term = kwargs.pop("term", "")

        self.dsl = {"term": {self.field: self.term}}


class Terms(Dsl):
    """
    http://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-terms-query.html

    """

    def __init__(self, **kwargs):
        self.field = kwargs.pop("field", "_all")
        self.terms = kwargs.pop("terms", [])

        if not isinstance(self.terms, list):
            self.terms = [self.terms]

        self.dsl = {"terms": {self.field: self.terms}}


class GeoShape(Dsl):
    """
    http://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-geo-shape-query.html
    http://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-geo-shape-type.html

    """

    def __init__(self, **kwargs):
        self.field = kwargs.pop("field", "_all")
        self.type = kwargs.pop("type", "")
        self.coordinates = kwargs.pop("coordinates", "")

        self.dsl = {"geo_shape": {self.field: {"shape": {"type": self.type, "coordinates": self.coordinates}}}}


class Range(Dsl):
    """
    http://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-range-query.html

    """

    def __init__(self, **kwargs):
        self.field = kwargs.pop("field", "_all")
        self.gte = kwargs.pop("gte", None)
        self.gt = kwargs.pop("gt", None)
        self.lte = kwargs.pop("lte", None)
        self.lt = kwargs.pop("lt", None)
        self.boost = kwargs.pop("boost", None)
        self.relation = kwargs.pop("relation", None)

        if self.boost:
            boost = {"boost": self.boost}
        else:
            boost = {}

        self.dsl = {"range": {self.field: boost}}

        if self.gte is None and self.gt is None and self.lte is None and self.lt is None:
            raise RangeDSLException(_("You need at least one of the following operators in a Range expression: gte, gt, lte, or lt"))
        if self.gte is not None and self.gt is not None:
            raise RangeDSLException(_("You can only use one of either: gte or gt"))
        if self.lte is not None and self.lt is not None:
            raise RangeDSLException(_("You can only use one of either: lte or lt"))

        if self.gte is not None:
            self.dsl["range"][self.field]["gte"] = self.gte
        if self.gt is not None:
            self.dsl["range"][self.field]["gt"] = self.gt
        if self.lte is not None:
            self.dsl["range"][self.field]["lte"] = self.lte
        if self.lt is not None:
            self.dsl["range"][self.field]["lt"] = self.lt
        if self.relation is not None:
            self.dsl["range"][self.field]["relation"] = self.relation


class RangeDSLException(Exception):
    pass


class SimpleQueryString(Dsl):
    """
    http://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-simple-query-string-query.html

    """

    def __init__(self, **kwargs):
        self.field = kwargs.pop("field", "_all")  # can be a list of fields
        self.query = kwargs.pop("query", "")
        self.operator = kwargs.pop("operator", "or")
        self.analyzer = kwargs.pop("analyzer", "snowball")
        self.flags = kwargs.pop("flags", "OR|AND|PREFIX")
        # The available flags are: ALL, NONE, AND, OR, PREFIX, PHRASE, PRECEDENCE, ESCAPE, WHITESPACE, FUZZY, NEAR, and SLOP.

        # if not isinstance(self.field, list):
        #     self.field = [self.field]

        self.dsl = {
            "simple_query_string": {"fields": self.field, "query": self.query, "default_operator": self.operator, "flags": self.flags}
        }

        self.dsl = {"prefix": {self.field: self.query}}


class Exists(Dsl):
    """
    https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-exists-query.html

    """

    def __init__(self, **kwargs):
        self.field = kwargs.pop("field", "")
        self.dsl = {"exists": {"field": self.field}}


class Ids(Dsl):
    """
    https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-ids-query.html

    Keyword Arguments:
    ids -- a single document id as a string, or a list of document ids

    """

    def __init__(self, **kwargs):
        self.ids = kwargs.pop("ids", None)
        if not isinstance(self.ids, list):
            self.ids = [self.ids]
        self.dsl = {"ids": {"values": self.ids}}


class Aggregation(Dsl):
    """
    https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations.html

    """

    def __init__(self, **kwargs):
        self.agg = {}
        self.name = kwargs.pop("name", None)
        self.field = kwargs.pop("field", None)
        self.script = kwargs.pop("script", None)
        self.type = kwargs.pop("type", None)
        self.size = kwargs.pop("size", None)

        if self.field is not None and self.script is not None:
            raise AggregationDSLException(_('You need to specify either a "field" or a "script"'))
        if self.name is None:
            raise AggregationDSLException(_("You need to specify a name for your aggregation"))
        if self.type is None:
            raise AggregationDSLException(_("You need to specify an aggregation type"))

        self.agg = {self.name: {self.type: {}}}

        if self.field is not None:
            self.agg[self.name][self.type]["field"] = self.field
        elif self.script is not None:
            self.agg[self.name][self.type]["script"] = self.script

        self.set_size(self.size)

        for key in kwargs:
            self.agg[self.name][self.type][key] = kwargs.get(key, None)

    def add_aggregation(self, agg=None):
        if agg is not None:
            if "aggs" not in self.agg[self.name]:
                self.agg[self.name]["aggs"] = {}

            self.agg[self.name]["aggs"][agg.name] = agg.agg[agg.name]

    def set_size(self, size):
        if size is not None and size > 0:
            self.agg[self.name][self.type]["size"] = size


class AggregationDSLException(Exception):
    pass


class GeoHashGridAgg(Aggregation):
    """
    https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-geohashgrid-aggregation.html

    """

    def __init__(self, **kwargs):
        self.field = kwargs.get("field", "")
        self.precision = kwargs.get("precision", 5)
        super(GeoHashGridAgg, self).__init__(type="geohash_grid", **kwargs)

        self.agg[self.name][self.type]["precision"] = self.precision


class GeoBoundsAgg(Aggregation):
    """
    https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-geohashgrid-aggregation.html

    """

    def __init__(self, **kwargs):
        self.field = kwargs.get("field", "")
        self.wrap_longitude = kwargs.get("wrap_longitude", False)
        super(GeoBoundsAgg, self).__init__(type="geo_bounds", **kwargs)

        self.agg[self.name][self.type]["wrap_longitude"] = self.wrap_longitude


class CoreDateAgg(Aggregation):
    """
    https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations.html

    """

    def __init__(self, **kwargs):
        self.field = kwargs.get("field", "")
        self.format = kwargs.pop("format", None)
        super(CoreDateAgg, self).__init__(**kwargs)

        if self.format:
            self.agg[self.name][self.type]["format"] = self.format


class MinAgg(CoreDateAgg):
    """
    https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-min-aggregation.html

    """

    def __init__(self, **kwargs):
        name = kwargs.pop("name", "min_%s" % kwargs.get("field", ""))
        super(MinAgg, self).__init__(name=name, type="min", **kwargs)


class MaxAgg(CoreDateAgg):
    """
    https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-max-aggregation.html

    """

    def __init__(self, **kwargs):
        name = kwargs.pop("name", "max_%s" % kwargs.get("field", ""))
        super(MaxAgg, self).__init__(name=name, type="max", **kwargs)


class DateRangeAgg(CoreDateAgg):
    """
    https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-daterange-aggregation.html

    """

    def __init__(self, **kwargs):
        min_date = kwargs.pop("min_date", None)
        max_date = kwargs.pop("max_date", None)
        key = kwargs.pop("key", None)
        super(DateRangeAgg, self).__init__(type="date_range", **kwargs)

        self.add(min_date=min_date, max_date=max_date, key=key, **kwargs)

    def add(self, **kwargs):
        date_range = {}
        min_date = kwargs.pop("min_date", None)
        max_date = kwargs.pop("max_date", None)
        key = kwargs.pop("key", None)

        if "ranges" not in self.agg[self.name][self.type]:
            self.agg[self.name][self.type]["ranges"] = []

        if min_date is not None:
            date_range["from"] = min_date
        if max_date is not None:
            date_range["to"] = max_date
        if key is not None:
            date_range["key"] = key

        if min_date is not None or max_date is not None:
            self.agg[self.name][self.type]["ranges"].append(date_range)


class RangeAgg(Aggregation):
    """
    https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-range-aggregation.html

    """

    def __init__(self, **kwargs):
        min_val = kwargs.pop("min", None)
        max_val = kwargs.pop("max", None)
        key = kwargs.pop("key", None)
        super(RangeAgg, self).__init__(type="range", **kwargs)

        self.add(min=min_val, max=max_val, key=key, **kwargs)

    def add(self, **kwargs):
        date_range = {}
        min_val = kwargs.pop("min", None)
        max_val = kwargs.pop("max", None)
        key = kwargs.pop("key", None)

        if "ranges" not in self.agg[self.name][self.type]:
            self.agg[self.name][self.type]["ranges"] = []

        if min_val is not None:
            date_range["from"] = min_val
        if max_val is not None:
            date_range["to"] = max_val
        if key is not None:
            date_range["key"] = key

        if min_val is not None or max_val is not None:
            self.agg[self.name][self.type]["ranges"].append(date_range)


class FiltersAgg(Aggregation):
    """
    http://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-range-query.html

    """

    def __init__(self, **kwargs):
        self.name = kwargs.pop("name", None)

        self.agg = {self.name: {"filters": {"filters": []}}}

    def add_filter(self, filter=None):
        if filter is not None:
            self.agg[self.name]["filters"]["filters"].append(filter.dsl)


class NestedAgg(Aggregation):
    """
    http://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-nested-aggregation.html

    """

    def __init__(self, **kwargs):
        self.aggregation = kwargs.pop("agg", {})
        self.path = kwargs.pop("path", None)
        if self.path is None:
            raise NestedAggDSLException(_("You need to specify a path for your nested aggregation"))
        super(NestedAgg, self).__init__(type="nested", path=self.path, **kwargs)

        if self.name:
            self.agg[self.name]["aggs"] = self.aggregation


class NestedAggDSLException(Exception):
    pass
