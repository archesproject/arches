from datetime import datetime
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.date_utils import ExtendedDateFormat
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Bool, Nested, Term, Terms, Range
from arches.app.search.components.base import BaseSearchFilter
from django.db.models import Q

details = {
    "searchcomponentid": "",
    "name": "Time Filter",
    "icon": "fa fa-calendar",
    "modulename": "time_filter.py",
    "classname": "TimeFilter",
    "type": "popup",
    "componentpath": "views/components/search/time-filter",
    "componentname": "time-filter",
    "sortorder": "1",
    "enabled": True,
}


class TimeFilter(BaseSearchFilter):
    def append_dsl(self, search_results_object, permitted_nodegroups, include_provisional):
        search_query = Bool()
        querysting_params = self.request.GET.get(details["componentname"], "")
        temporal_filter = JSONDeserializer().deserialize(querysting_params)
        if "fromDate" in temporal_filter and "toDate" in temporal_filter:
            # now = str(datetime.utcnow())
            start_date = ExtendedDateFormat(temporal_filter["fromDate"])
            end_date = ExtendedDateFormat(temporal_filter["toDate"])
            date_nodeid = (
                str(temporal_filter["dateNodeId"]) if "dateNodeId" in temporal_filter and temporal_filter["dateNodeId"] != "" else None
            )
            query_inverted = False if "inverted" not in temporal_filter else temporal_filter["inverted"]

            temporal_query = Bool()

            if query_inverted:
                # inverted date searches need to use an OR clause and are generally more complicated to structure (can't use ES must_not)
                # eg: less than START_DATE OR greater than END_DATE
                inverted_date_query = Bool()
                inverted_date_ranges_query = Bool()

                if start_date.is_valid():
                    inverted_date_query.should(Range(field="dates.date", lt=start_date.lower))
                    inverted_date_ranges_query.should(Range(field="date_ranges.date_range", lt=start_date.lower))
                if end_date.is_valid():
                    inverted_date_query.should(Range(field="dates.date", gt=end_date.upper))
                    inverted_date_ranges_query.should(Range(field="date_ranges.date_range", gt=end_date.upper))

                date_query = Bool()
                date_query.filter(inverted_date_query)
                date_query.filter(Terms(field="dates.nodegroup_id", terms=permitted_nodegroups))

                if include_provisional is False:
                    date_query.filter(Terms(field="dates.provisional", terms=["false"]))

                elif include_provisional == "only provisional":
                    date_query.filter(Terms(field="dates.provisional", terms=["true"]))

                if date_nodeid:
                    date_query.filter(Term(field="dates.nodeid", term=date_nodeid))
                else:
                    date_ranges_query = Bool()
                    date_ranges_query.filter(inverted_date_ranges_query)
                    date_ranges_query.filter(Terms(field="date_ranges.nodegroup_id", terms=permitted_nodegroups))

                    if include_provisional is False:
                        date_ranges_query.filter(Terms(field="date_ranges.provisional", terms=["false"]))

                    elif include_provisional == "only provisional":
                        date_ranges_query.filter(Terms(field="date_ranges.provisional", terms=["true"]))

                    temporal_query.should(Nested(path="date_ranges", query=date_ranges_query))
                temporal_query.should(Nested(path="dates", query=date_query))

            else:
                date_query = Bool()
                date_query.filter(Range(field="dates.date", gte=start_date.lower, lte=end_date.upper))
                date_query.filter(Terms(field="dates.nodegroup_id", terms=permitted_nodegroups))

                if include_provisional is False:
                    date_query.filter(Terms(field="dates.provisional", terms=["false"]))
                elif include_provisional == "only provisional":
                    date_query.filter(Terms(field="dates.provisional", terms=["true"]))

                if date_nodeid:
                    date_query.filter(Term(field="dates.nodeid", term=date_nodeid))
                else:
                    date_ranges_query = Bool()
                    date_ranges_query.filter(
                        Range(field="date_ranges.date_range", gte=start_date.lower, lte=end_date.upper, relation="intersects")
                    )
                    date_ranges_query.filter(Terms(field="date_ranges.nodegroup_id", terms=permitted_nodegroups))

                    if include_provisional is False:
                        date_ranges_query.filter(Terms(field="date_ranges.provisional", terms=["false"]))
                    if include_provisional == "only provisional":
                        date_ranges_query.filter(Terms(field="date_ranges.provisional", terms=["true"]))

                    temporal_query.should(Nested(path="date_ranges", query=date_ranges_query))
                temporal_query.should(Nested(path="dates", query=date_query))

            search_query.filter(temporal_query)

            search_results_object["query"].add_query(search_query)

    def view_data(self):
        ret = {}
        date_datatypes = ["date", "edtf"]
        alt_widget_labels = {"datepicker-widget": "Date Widget", "edtf-widget": "Extended Date Time"}

        date_nodes = models.Node.objects.filter(datatype__in=date_datatypes, graph__isresource=True, graph__isactive=True)

        date_cardxnodesxwidgets = list(models.CardXNodeXWidget.objects.filter(node_id__in=list(date_nodes)))
        date_widget_ids = [str(cnw.widget_id) for cnw in date_cardxnodesxwidgets]
        date_widgets = list(models.Widget.objects.filter(widgetid__in=date_widget_ids))
        node_widget_dict = { str(cnw.node_id): str(cnw.widget_id) for cnw in date_cardxnodesxwidgets }
        widget_name_dict = {}
        try:
            widget_name_dict = { str(widget.widgetid): alt_widget_labels[str(widget.name)] for widget in date_widgets }
        except KeyError as e:
            for widget in date_widgets:
                if widget.name in alt_widget_labels.keys():
                    widget_name_dict[str(widget.widgetid)] = alt_widget_labels[str(widget.name)]
                else:
                    widget_name_dict[str(widget.widgetid)] = str(widget.name)
        
        node_widget_name_dict = { k: widget_name_dict[v] for k, v in node_widget_dict.items()}
        searchable_date_nodes = [ node for node in date_nodes if self.request.user.has_perm("read_nodegroup", node.nodegroup) ]

        ret["date_nodes"] = searchable_date_nodes
        ret["widget_name_lookup"] = node_widget_name_dict
        ret["graph_models"] = models.GraphModel.objects.all().exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        return ret
