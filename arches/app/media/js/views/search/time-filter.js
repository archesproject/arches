define([
    'underscore',
    'knockout',
    'moment',
    'views/search/base-filter',
    'arches',
    'bindings/datepicker',
    'bindings/chosen',
    'bindings/time-wheel'
],
function(_, ko, moment, BaseFilter, arches) {
    return BaseFilter.extend({
        initialize: function(options) {
            var self = this;
            this.name = 'Time Filter';
            this.filter = {
                fromDate: ko.observable(null),
                toDate: ko.observable(null),
                dateNodeId: ko.observable(null),
                inverted: ko.observable(false)
            }
            this.filter.fromDate.subscribe(function (fromDate) {
                var toDate = self.filter.toDate();
                if (fromDate && toDate && !this.isFromLessThanTo(fromDate, toDate)) {
                    self.filter.toDate(fromDate);
                }
            }, this);
            this.filter.toDate.subscribe(function (toDate) {
                var fromDate = self.filter.fromDate();
                if (fromDate && toDate && !this.isFromLessThanTo(fromDate, toDate)) {
                    self.filter.fromDate(toDate);
                }
            }, this);
            this.dateRangeType = ko.observable('custom');
            this.format = 'YYYY-MM-DD';
            this.showWheel = ko.observable(false);
            this.breadCrumb = ko.observable();
            this.selectedPeriod = ko.observable();
            this.wheelConfig = ko.observable();
            this.getTimeWheelConfig();
            this.selectedPeriod.subscribe(function (d) {
                if (d) {
                    var start = moment(0, 'YYYY').add(d.start, 'years').format(self.format);
                    var end = moment(0, 'YYYY').add(d.end, 'years').format(self.format);
                    self.dateRangeType('custom');
                    self.filter.fromDate(end);
                    self.filter.toDate(end);
                    self.filter.fromDate(start);
                }
            })

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

            this.filterChanged = ko.computed(function(){
                if(!!this.filter.fromDate() || !!this.filter.toDate()){
                    this.termFilter.addTag(this.name, this.name, this.filter.inverted);
                }
                return ko.toJSON(this.filter);
            }, this).extend({ deferred: true });

            BaseFilter.prototype.initialize.call(this, options);
        },

        getTimeWheelConfig: function(){
            var self = this;
            $.ajax({
                type: "GET",
                url: arches.urls.time_wheel_config,
                success: function(response) {
                    self.wheelConfig(response);
                },
                error: function(response) {
                    self.breadCrumb(response.responseText);
                }
            });
        },

        appendFilters: function(filterParams) {
            var filters_applied = !!this.filter.fromDate() || !!this.filter.toDate();
            if(filters_applied){
                filterParams.temporalFilter = ko.toJSON(this.filter);
            }
            return filters_applied;
        },

        restoreState: function(query) {
            var doQuery = false;
            if ('temporalFilter' in query) {
                query.temporalFilter = JSON.parse(query.temporalFilter);
                this.filter.inverted(!!query.temporalFilter.inverted);
                this.termFilter.addTag(this.name, this.name, this.filter.inverted);
                ['fromDate', 'toDate', 'dateNodeId'].forEach(function(key) {
                    if (key in query.temporalFilter) {
                        this.filter[key](query.temporalFilter[key]);
                    }
                }, this);
                doQuery = true;
            }
            return doQuery;
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
            this.termFilter.removeTag(this.name);
            this.selectedPeriod(null);
            return;
        }
    });
});
