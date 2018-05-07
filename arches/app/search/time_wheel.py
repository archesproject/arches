import math
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Term, Terms, GeoShape, Range, MinAgg, MaxAgg, RangeAgg, Aggregation, GeoHashGridAgg, GeoBoundsAgg, FiltersAgg, NestedAgg
from arches.app.utils.date_utils import ExtendedDateFormat
from arches.app.search.search_engine_factory import SearchEngineFactory
from django.core.cache import cache

class TimeWheel(object):

    def time_wheel_config(self, user):
        se = SearchEngineFactory().create()
        query = Query(se, limit=0)
        nested_agg = NestedAgg(path='dates', name='min_max_agg')
        nested_agg.add_aggregation(MinAgg(field='dates.date'))
        nested_agg.add_aggregation(MaxAgg(field='dates.date'))
        query.add_aggregation(nested_agg)
        results = query.search(index='resource')

        if results is not None and results['aggregations']['min_max_agg']['min_dates.date']['value'] is not None and results['aggregations']['min_max_agg']['max_dates.date']['value'] is not None:
            min_date = int(results['aggregations']['min_max_agg']['min_dates.date']['value'])/10000
            max_date = int(results['aggregations']['min_max_agg']['max_dates.date']['value'])/10000
            # round min and max date to the nearest 1000 years
            min_date = math.ceil(math.fabs(min_date)/1000)*-1000 if min_date < 0 else math.floor(min_date/1000)*1000
            max_date = math.floor(math.fabs(max_date)/1000)*-1000 if max_date < 0 else math.ceil(max_date/1000)*1000
            query = Query(se, limit=0)
            range_lookup = {}


            def gen_range_agg(gte=None, lte=None, permitted_nodegroups=None):
                date_query = Bool()
                date_query.filter(Range(field='dates.date', gte=gte, lte=lte, relation='intersects'))
                if permitted_nodegroups:
                    date_query.filter(Terms(field='dates.nodegroup_id', terms=permitted_nodegroups))
                date_ranges_query = Bool()
                date_ranges_query.filter(Range(field='date_ranges.date_range', gte=gte, lte=lte, relation='intersects'))
                if permitted_nodegroups:
                    date_ranges_query.filter(Terms(field='date_ranges.nodegroup_id', terms=permitted_nodegroups))
                wrapper_query = Bool()
                wrapper_query.should(Nested(path='date_ranges', query=date_ranges_query))
                wrapper_query.should(Nested(path='dates', query=date_query))
                return wrapper_query

            # if custom setting is true:
            #     ['big', 'little', 'tiny']
            # else:
            #     if range spans millenia:
            #         ['mill', 'halfmill', 'century']
            #         if range spans century:
            #             ['cent', 'half cent', 'decade']
            #             if range spans decades:
            #                 ['decade', 'half dec', 'year']

            date_tiers = {"name": "Millennium", "interval": 1000, "root": True, "child": {
                    "name": "Century", "interval": 100, "child": {
                        "name": "Decade", "interval": 10
                        }
                    }
                }

            def add_date_tier(date_tier, low_date, high_date, previous_period_agg=None):
                interval = date_tier["interval"]
                name = date_tier["name"]
                print name, interval, date_tier, low_date, high_date
                if "root" in date_tier:
                    high_date = int(high_date) + interval
                for period in range(int(low_date), int(high_date), interval):
                    min_period = period
                    max_period = period + interval
                    period_name = "{0} ({1} - {2})".format(name, min_period, max_period)
                    nodegroups = self.get_permitted_nodegroups(user) if "root" in date_tier else None
                    period_boolquery = gen_range_agg(gte=ExtendedDateFormat(min_period).lower,
                        lte=ExtendedDateFormat(max_period).lower,
                        permitted_nodegroups=nodegroups)
                    period_agg = FiltersAgg(name=period_name)
                    period_agg.add_filter(period_boolquery)
                    if "root" not in date_tier:
                        previous_period_agg.add_aggregation(period_agg)
                    range_lookup[period_name] = [min_period, max_period]
                    if "child" in date_tier:
                        add_date_tier(date_tier['child'], min_period, max_period, period_agg)
                    if "root" in date_tier:
                        query.add_aggregation(period_agg)

            add_date_tier(date_tiers, min_date, max_date)

            # for millennium in range(int(min_date),int(max_date)+1000,1000):
            #     min_millenium = millennium
            #     max_millenium = millennium + 1000
            #     millenium_name = "Millennium (%s - %s)"%(min_millenium, max_millenium)
            #     mill_boolquery = gen_range_agg(gte=ExtendedDateFormat(min_millenium).lower,
            #         lte=ExtendedDateFormat(max_millenium).lower,
            #         permitted_nodegroups=self.get_permitted_nodegroups(user))
            #     millenium_agg = FiltersAgg(name=millenium_name)
            #     millenium_agg.add_filter(mill_boolquery)
            #     range_lookup[millenium_name] = [min_millenium, max_millenium]
            #
            #     for century in range(min_millenium,max_millenium,100):
            #         min_century = century
            #         max_century = century + 100
            #         century_name="Century (%s - %s)"%(min_century, max_century)
            #         cent_boolquery = gen_range_agg(gte=ExtendedDateFormat(min_century).lower,
            #             lte=ExtendedDateFormat(max_century).lower)
            #         century_agg = FiltersAgg(name=century_name)
            #         century_agg.add_filter(cent_boolquery)
            #         millenium_agg.add_aggregation(century_agg)
            #         range_lookup[century_name] = [min_century, max_century]
            #
            #         for decade in range(min_century,max_century,10):
            #             min_decade = decade
            #             max_decade = decade + 10
            #             decade_name = "Decade (%s - %s)"%(min_decade, max_decade)
            #             dec_boolquery = gen_range_agg(gte=ExtendedDateFormat(min_decade).lower,
            #                 lte=ExtendedDateFormat(max_decade).lower)
            #             decade_agg = FiltersAgg(name=decade_name)
            #             decade_agg.add_filter(dec_boolquery)
            #             century_agg.add_aggregation(decade_agg)
            #             range_lookup[decade_name] = [min_decade, max_decade]
            #
            #     query.add_aggregation(millenium_agg)

            root = d3Item(name='root')
            results = {'buckets':[query.search(index='resource')['aggregations']]}
            results_with_ranges = self.appendDateRanges(results, range_lookup)
            self.transformESAggToD3Hierarchy(results_with_ranges, root)
            return root


    def transformESAggToD3Hierarchy(self, results, d3ItemInstance):
        if 'buckets' not in results:
            return d3ItemInstance

        for key, value in results['buckets'][0].iteritems():
            if key == 'from':
                d3ItemInstance.start = int(value)
            elif key == 'to':
                d3ItemInstance.end = int(value)
            elif key == 'doc_count':
                d3ItemInstance.size = value
            elif key == 'key':
                pass
            else:
                d3ItemInstance.children.append(self.transformESAggToD3Hierarchy(value, d3Item(name=key)))

        d3ItemInstance.children = sorted(d3ItemInstance.children, key=lambda item: item.start)

        return d3ItemInstance

    def appendDateRanges(self, results, range_lookup):
        if 'buckets' in results:
            bucket = results['buckets'][0]
            for key, value in bucket.iteritems():
                if key in range_lookup:
                    bucket[key]['buckets'][0]['from'] = range_lookup[key][0]
                    bucket[key]['buckets'][0]['to'] = range_lookup[key][1]
                    self.appendDateRanges(value, range_lookup)

        return results

    def get_permitted_nodegroups(self, user):
        return [str(nodegroup.pk) for nodegroup in get_nodegroups_by_perm(user, 'models.read_nodegroup')]


class d3Item(object):
    name = ''
    size = 0
    start = None
    end = None
    children = []

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name', '')
        self.size = kwargs.pop('size', 0)
        self.start = kwargs.pop('start',None)
        self.end = kwargs.pop('end', None)
        self.children = kwargs.pop('children', [])
