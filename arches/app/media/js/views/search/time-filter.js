define([
    'underscore',
    'knockout',
    'moment',
    'views/search/base-filter',
    'views/search/time-wheel-config',
    'bindings/datepicker',
    'bindings/chosen',
    'bindings/time-wheel'
],
function(_, ko, moment, BaseFilter, wheelConfig) {
    return BaseFilter.extend({
        initialize: function(options) {
            var self = this;
            this.fromDate = ko.observable(null);
            this.toDate = ko.observable(null);
            this.dateRangeType = ko.observable('custom');
            this.dateNodeId = ko.observable('all');
            this.format = 'YYYY-MM-DD';
            this.wheelConfig = wheelConfig;

            this.dateRangeType.subscribe(function(value) {
                var today = moment();
                var from = today.format(self.format);
                var to = today.format(self.format);
                switch (value) {
                    case "today":
                        break;
                    case "last-7":
                        from = today.subtract(7, 'days').format(self.format);
                        break;
                    case "last-30":
                        from = today.subtract(30, 'days').format(self.format);
                        break;
                    case "this-week":
                        from = today.day(0).format(self.format);
                        to = today.day(6).format(self.format);
                        break;
                    case "this-month":
                        from = today.date(1).format(self.format);
                        to = moment().month(today.month()+1).date(0).format(self.format);
                        break;
                    case "this-quarter":
                        from = moment().date(1).quarter(today.quarter()).format(self.format);
                        to = moment().date(1).quarter(today.quarter()+1).format(self.format);
                        break;
                    case "this-year":
                        var first = today.dayOfYear(1);
                        from = first.format(self.format);
                        to = first.add(1, 'years').subtract(1, 'days').format(self.format);
                        break;
                    default:
                        return;
                }
                self.toDate(to);
                self.fromDate(from);
            });

            BaseFilter.prototype.initialize.call(this, options);
        },

        appendFilters: function(filterParams) {
            var from = this.fromDate();
            var to = this.toDate();
            var node = this.dateNodeId();
            if (from || to) {
                filterParams.fromDate = this.fromDate();
                filterParams.toDate = this.toDate();
                if (node !== 'all') {
                    filterParams.dateNodeId = node;
                }
                return true;
            }
            return false;
        },

        restoreState: function(query) {
            var self = this;
            ['fromDate', 'toDate', 'dateNodeId'].forEach(function(key) {
                if (key in query) {
                    self[key](query[key]);
                }
            });
            return (this.fromDate() || this.toDate());
        },

        clear: function() {
            this.toDate(null);
            this.fromDate(null);
            this.dateRangeType('custom');
            this.dateNodeId('all');
            return;
        }
    });
});
