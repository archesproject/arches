define([
    'jquery',
    'underscore',
    'knockout',
    'moment',
    'views/components/search/base-filter',
    'arches',
    'bindings/datepicker',
    'bindings/chosen',
    'bindings/time-wheel'
],
function($, _, ko, moment, BaseFilter, arches) {
    var componentName = 'time-filter';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({
            initialize: function(options) {
                options.name = 'Time Filter';
                this.dateDropdownEleId = 'dateDropdownEleId' + _.random(2000, 3000000);
                BaseFilter.prototype.initialize.call(this, options);
                this.filter = {
                    fromDate: ko.observable(null),
                    toDate: ko.observable(null),
                    dateNodeId: ko.observable(null),
                    inverted: ko.observable(false)
                };
                this.filter.fromDate.subscribe(function (fromDate) {
                    var toDate = this.filter.toDate();
                    if (fromDate && toDate && !this.isFromLessThanTo(fromDate, toDate)) {
                        this.filter.toDate(fromDate);
                    }
                }, this);
                this.filter.toDate.subscribe(function (toDate) {
                    var fromDate = this.filter.fromDate();
                    if (fromDate && toDate && !this.isFromLessThanTo(fromDate, toDate)) {
                        this.filter.fromDate(toDate);
                    }
                }, this);
                this.dateRangeType = ko.observable('custom');
                this.format = 'YYYY-MM-DD';
                this.breadCrumb = ko.observable();
                this.selectedPeriod = ko.observable();
                this.wheelConfig = ko.observable();
                this.loading = ko.observable(false);
                this.getTimeWheelConfig();
                this.date_nodes = ko.observableArray();
                this.graph_models = ko.observableArray();
                this.selectedPeriod.subscribe(function (d) {
                    if (d) {
                        var start = moment(0, 'YYYY').add(d.data.start, 'years').format(this.format);
                        var end = moment(0, 'YYYY').add(d.data.end, 'years').format(this.format);
                        this.dateRangeType('custom');
                        this.filter.fromDate(end);
                        this.filter.toDate(end);
                        this.filter.fromDate(start);
                    }
                }, this);

                this.dateRangeType.subscribe(function(value) {
                    var today = moment();
                    var from = today.format(this.format);
                    var to = today.format(this.format);
                    switch (value) {
                        case "today":
                            break;
                        case "last-7":
                            from = today.subtract(7, 'days').format(this.format);
                            break;
                        case "last-30":
                            from = today.subtract(30, 'days').format(this.format);
                            break;
                        case "this-week":
                            from = today.day(0).format(this.format);
                            to = today.day(6).format(this.format);
                            break;
                        case "this-month":
                            from = today.date(1).format(this.format);
                            to = moment().month(today.month()+1).date(0).format(this.format);
                            break;
                        case "this-quarter":
                            from = moment().date(1).quarter(today.quarter()).format(this.format);
                            to = moment().date(1).quarter(today.quarter()+1).format(this.format);
                            break;
                        case "this-year":
                            var first = today.dayOfYear(1);
                            from = first.format(this.format);
                            to = first.add(1, 'years').subtract(1, 'days').format(this.format);
                            break;
                        default:
                            return;
                    }
                    this.filter.toDate(to);
                    this.filter.fromDate(from);
                }, this);


                $.ajax({
                    type: "GET",
                    url: arches.urls.api_search_component_data + componentName,
                    context: this
                }).done(function(response) {
                    this.date_nodes(response.date_nodes);
                    this.graph_models(response.graph_models);
                    this.restoreState();
                    $("#" + this.dateDropdownEleId).trigger("chosen:updated");

                    this.filterChanged = ko.computed(function(){
                        if(!!this.filter.fromDate() || !!this.filter.toDate()){
                            this.getFilter('term-filter').addTag(this.name, this.name, this.filter.inverted);
                        }
                        return ko.toJSON(this.filter);
                    }, this).extend({ deferred: true });

                    this.filterChanged.subscribe(function() {
                        this.updateQuery();
                    }, this);
                });

                this.filters[componentName](this);
            },

            updateQuery: function() {
                var queryObj = this.query();
                var filters_applied = !!this.filter.fromDate() || !!this.filter.toDate();
                if(filters_applied){
                    queryObj[componentName] = ko.toJSON(this.filter);
                } else {
                    delete queryObj[componentName];
                }
                this.query(queryObj);
            },

            getTimeWheelConfig: function(){
                this.loading(true);
                $.ajax({
                    type: "GET",
                    context: this,
                    url: arches.urls.time_wheel_config
                }).done(function(response) {
                    this.wheelConfig(response);
                }).fail(function(response) {
                    this.breadCrumb(response.responseText);
                }).always(function(){
                    this.loading(false);
                });
            },

            restoreState: function() {
                var query = this.query();
                if (componentName in query) {
                    var timeQuery = JSON.parse(query[componentName]);
                    this.filter.inverted(!!timeQuery.inverted);
                    this.getFilter('term-filter').addTag(this.name, this.name, this.filter.inverted);
                    ['fromDate', 'toDate', 'dateNodeId'].forEach(function(key) {
                        if (key in timeQuery) {
                            this.filter[key](timeQuery[key]);
                        }
                    }, this);
                }
            },

            isFromLessThanTo: function(fromDate, toDate) {
                if(!this.isBCE(fromDate) && !this.isBCE(toDate)) {
                    return fromDate < toDate;
                }else if(this.isBCE(fromDate) && !this.isBCE(toDate)) {
                    return true;
                }else if(!this.isBCE(fromDate) && this.isBCE(toDate)) {
                    return false;
                }else if(this.isBCE(fromDate) && this.isBCE(toDate)) {
                    return fromDate > toDate;
                }
                return true;
            },

            isBCE: function(date) {
                return (date.charAt(0) === '-');
            },

            clear: function() {
                this.filter.fromDate(null);
                this.filter.toDate(null);
                this.filter.dateNodeId(null);
                this.filter.inverted(false);
                this.dateRangeType('custom');
                this.getFilter('term-filter').removeTag(this.name);
                this.selectedPeriod(null);
                return;
            }
        }),
        template: { require: 'text!templates/views/components/search/time-filter.htm' }
    });
});
