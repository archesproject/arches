import logging
import math
from arches.app.utils.date_utils import ExtendedDateFormat
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.search.elasticsearch_dsl_builder import (
    Bool,
    Match,
    Query,
    Nested,
    Term,
    Terms,
    GeoShape,
    Range,
    MinAgg,
    MaxAgg,
    RangeAgg,
    Aggregation,
    GeoHashGridAgg,
    GeoBoundsAgg,
    FiltersAgg,
    NestedAgg,
)
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.models.system_settings import settings
from django.core.cache import cache
from django.utils.translation import get_language, gettext as _

logger = logging.getLogger(__name__)


class TimeWheel(object):
    def time_wheel_config(self, user):
        se = SearchEngineFactory().create()
        query = Query(se, limit=0)
        nested_agg = NestedAgg(path="dates", name="min_max_agg")
        nested_agg.add_aggregation(MinAgg(field="dates.date"))
        nested_agg.add_aggregation(MaxAgg(field="dates.date"))
        query.add_aggregation(nested_agg)
        results = query.search(index=RESOURCES_INDEX)

        if (
            results is not None
            and results["aggregations"]["min_max_agg"]["min_dates.date"]["value"]
            is not None
            and results["aggregations"]["min_max_agg"]["max_dates.date"]["value"]
            is not None
        ):
            min_date = (
                int(results["aggregations"]["min_max_agg"]["min_dates.date"]["value"])
                / 10000
            )
            max_date = (
                int(results["aggregations"]["min_max_agg"]["max_dates.date"]["value"])
                / 10000
            )
            # round min and max date to the nearest 1000 years
            min_date = (
                math.ceil(math.fabs(min_date) / 1000) * -1000
                if min_date < 0
                else math.floor(min_date / 1000) * 1000
            )
            max_date = (
                math.floor(math.fabs(max_date) / 1000) * -1000
                if max_date < 0
                else math.ceil(max_date / 1000) * 1000
            )
            query = Query(se, limit=0)
            range_lookup = {}

            def gen_range_agg(gte=None, lte=None, permitted_nodegroups=None):
                date_query = Bool()
                date_query.filter(
                    Range(field="dates.date", gte=gte, lte=lte, relation="intersects")
                )
                if permitted_nodegroups is not None:
                    date_query.filter(
                        Terms(field="dates.nodegroup_id", terms=permitted_nodegroups)
                    )
                date_ranges_query = Bool()
                date_ranges_query.filter(
                    Range(
                        field="date_ranges.date_range",
                        gte=gte,
                        lte=lte,
                        relation="intersects",
                    )
                )
                if permitted_nodegroups is not None:
                    date_ranges_query.filter(
                        Terms(
                            field="date_ranges.nodegroup_id", terms=permitted_nodegroups
                        )
                    )
                wrapper_query = Bool()
                wrapper_query.should(
                    Nested(path="date_ranges", query=date_ranges_query)
                )
                wrapper_query.should(Nested(path="dates", query=date_query))
                return wrapper_query

            date_tiers = {
                "name": "Millennium",
                "interval": 1000,
                "root": True,
                "child": {
                    "name": "Century",
                    "interval": 100,
                    "child": {"name": "Decade", "interval": 10},
                },
            }

            if abs(int(min_date) - int(max_date)) > 1000:
                date_tiers = {
                    "name": "Millennium",
                    "interval": 1000,
                    "root": True,
                    "child": {
                        "name": "Half-millennium",
                        "interval": 500,
                        "child": {"name": "Century", "interval": 100},
                    },
                }

            if settings.TIMEWHEEL_DATE_TIERS is not None:
                date_tiers = settings.TIMEWHEEL_DATE_TIERS

            def add_date_tier(date_tier, low_date, high_date, previous_period_agg=None):
                interval = date_tier["interval"]
                name = date_tier["name"]
                if "root" in date_tier:
                    high_date = int(high_date) + interval
                for period in range(int(low_date), int(high_date), interval):
                    within_range = True
                    min_period = period
                    max_period = period + interval
                    if "range" in date_tier:
                        within_range = (
                            min_period >= date_tier["range"]["min"]
                            and max_period <= date_tier["range"]["max"]
                        )
                    if within_range is True:
                        period_name = "{0} ({1} - {2})".format(
                            name, min_period, max_period
                        )
                        nodegroups = (
                            self.get_permitted_nodegroups(user)
                            if "root" in date_tier
                            else None
                        )
                        period_boolquery = gen_range_agg(
                            gte=ExtendedDateFormat(min_period).lower,
                            lte=ExtendedDateFormat(max_period).lower,
                            permitted_nodegroups=nodegroups,
                        )
                        period_agg = FiltersAgg(name=period_name)
                        period_agg.add_filter(period_boolquery)
                        if "root" not in date_tier:
                            previous_period_agg.add_aggregation(period_agg)
                        range_lookup[period_name] = [min_period, max_period]
                        if "child" in date_tier:
                            add_date_tier(
                                date_tier["child"], min_period, max_period, period_agg
                            )
                        if "root" in date_tier:
                            query.add_aggregation(period_agg)

            add_date_tier(date_tiers, min_date, max_date)

            root = d3Item(name="root")
            results = {"buckets": [query.search(index=RESOURCES_INDEX)["aggregations"]]}
            results_with_ranges = self.appendDateRanges(results, range_lookup)
            self.transformESAggToD3Hierarchy(results_with_ranges, root)

            # calculate total number of docs
            for child in root.children:
                root.size = root.size + child.size

            key = "time_wheel_config_{0}".format(user.username)
            if user.username in settings.CACHE_BY_USER:
                cache.set(key, root, settings.CACHE_BY_USER[user.username])
            else:
                try:
                    cache.set(key, root, settings.CACHE_BY_USER["default"])
                except KeyError:
                    logger.warning(
                        _(
                            "CACHE_BY_USER setting does not have a 'default'. Adding a default can improve search page performance."
                        )
                    )

            return root

    def transformESAggToD3Hierarchy(self, results, d3ItemInstance):
        if "buckets" not in results:
            return d3ItemInstance

        for key, value in results["buckets"][0].items():
            if key == "from":
                d3ItemInstance.start = int(value)
            elif key == "to":
                d3ItemInstance.end = int(value)
            elif key == "doc_count":
                d3ItemInstance.size = value
            elif key == "key":
                pass
            else:
                item = self.transformESAggToD3Hierarchy(value, d3Item(name=key))
                # only append items if they have a document count > 0
                if item.size > 0:
                    d3ItemInstance.children.append(item)

        d3ItemInstance.children = sorted(
            d3ItemInstance.children, key=lambda item: item.start
        )

        return d3ItemInstance

    def appendDateRanges(self, results, range_lookup):
        if "buckets" in results:
            bucket = results["buckets"][0]
            for key, value in bucket.items():
                if key in range_lookup:
                    bucket[key]["buckets"][0]["from"] = range_lookup[key][0]
                    bucket[key]["buckets"][0]["to"] = range_lookup[key][1]
                    self.appendDateRanges(value, range_lookup)

        return results

    def get_permitted_nodegroups(self, user):
        return get_nodegroups_by_perm(user, "models.read_nodegroup")


class d3Item(object):
    name = ""
    size = 0
    start = None
    end = None
    children = []

    def __init__(self, **kwargs):
        self.name = kwargs.pop("name", "")
        self.size = kwargs.pop("size", 0)
        self.start = kwargs.pop("start", None)
        self.end = kwargs.pop("end", None)
        self.children = kwargs.pop("children", [])
