define([
    'knockout',
    'views/search/base-filter',
    'bindings/term-search'
], function(ko, BaseFilter) {
    return BaseFilter.extend({
        initialize: function(options) {
            BaseFilter.prototype.initialize.call(this, options);
            this.filter.terms = ko.observableArray();
        },

        restoreState: function(query) {
            var self = this;
            var doQuery = false;
            if ('termFilter' in query) {
                query.termFilter = JSON.parse(query.termFilter);
                doQuery = true;
            }
            var filters = query.termFilter;
            if (typeof filters !== 'undefined' && filters.length > 0) {
                self.filter.terms(filters);
            }
            return doQuery;
        },

        clear: function() {
            this.filter.terms.removeAll();
        },

        appendFilters: function(filterParams) {
            filterParams.termFilter = ko.toJSON(this.filter.terms());
            return this.filter.terms().length === 0;
        }
    });
});
