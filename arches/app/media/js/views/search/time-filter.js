define([
    'knockout',
    'views/search/base-filter',
    'bindings/datepicker',
    'bindings/chosen'
],
function(ko, BaseFilter) {
    return BaseFilter.extend({
        initialize: function(options) {
            // var updatingDateRange = false;
            this.fromDate = ko.observable(null);
            this.toDate = ko.observable(null);
            this.dateRangeType = ko.observable('custom');
            // this.dateRangeType = ko.pureComputed({
            //     read: function() {
            //         return 'today';
            //     },
            //     write: function(value) {
            //         // set date range value based on selection
            //     },
            //     owner: this
            // });
            // this.dateRangeType.subscribe(function(value) {
            //     if (value !== 'custom'){
            //         updatingDateRange = true;
            //         // TODO: update from & to dates
            //
            //     }
            //     updatingDateRange = false;
            // });


            BaseFilter.prototype.initialize.call(this, options);
        },

        appendFilters: function(queryStringObject) {
            return false;
        },

        restoreState: function(filter) {
            return;
        },

        clear: function() {
            return;
        }
    });
});
