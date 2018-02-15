define([
    'knockout',
    'views/search/base-filter'
], function(ko, BaseFilter) {
    return BaseFilter.extend({
        initialize: function(options) {
            BaseFilter.prototype.initialize.call(this, options);
            this.name = 'Provisional Filter';
            this.filter = ko.observable(false);
        },

        restoreState: function(filter) {
            return;
        },

        clear: function() {
            this.filter.false();
        },

        appendFilters: function(filterParams) {
            if(this.filter() === true){
                filterParams.provisionalFilter = ko.toJSON(this.filter());
            }
            return this.filter();
        }

    });
});
