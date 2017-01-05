define([
    'knockout',
    'views/search/base-filter'
], function(ko, BaseFilter) {
    return BaseFilter.extend({
        initialize: function(options) {
            BaseFilter.prototype.initialize.call(this, options);
            this.filter.types = ko.observableArray();
        },

        restoreState: function(query) {
            var doQuery = false;
            if ('typeFilter' in query) {
                query.typeFilter = JSON.parse(query.typeFilter);
                if (query.typeFilter.length > 0) {
                    this.filter.types(query.typeFilter);
                }
                doQuery = true;
            }
            return doQuery;
        },

        clear: function() {
            this.filter.types.removeAll();
        },

        appendFilters: function(filterParams) {
            filterParams.typeFilter = ko.toJSON(this.filter.types());
            return this.filter.types().length === 0;
        },

        test: function(item){
            console.log(item);
            if(!!item){
                this.filter.types([item.graphid]);
            }else{
                this.clear();
            }
        }
    });
});
