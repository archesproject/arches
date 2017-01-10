define([
    'knockout',
    'views/search/base-filter'
], function(ko, BaseFilter) {
    return BaseFilter.extend({
        initialize: function(options) {
            BaseFilter.prototype.initialize.call(this, options);
            
            this.name = 'Resource Type Filter';
            
            this.filter = ko.observableArray();
        },

        restoreState: function(query) {
            var doQuery = false;
            if ('typeFilter' in query) {
                query.typeFilter = JSON.parse(query.typeFilter);
                if (query.typeFilter.length > 0) {
                    query.typeFilter.forEach(function(type){
                        type.inverted = ko.observable(!!type.inverted);
                        this.termFilter.addTag(type.name, this.name, type.inverted);
                    }, this)
                    this.filter(query.typeFilter);
                }
                doQuery = true;
            }
            return doQuery;
        },

        clear: function() {
            this.filter.removeAll();
        },

        appendFilters: function(filterParams) {
            if(this.filter().length > 0){
                filterParams.typeFilter = ko.toJSON(this.filter);
            }

            return this.filter().length > 0;
        },

        selectModelType: function(item){
            this.filter().forEach(function(item){
                this.termFilter.removeTag(item.name);
            }, this);
            if(!!item){
                var inverted = ko.observable(false)
                this.termFilter.addTag(item.name(), this.name, inverted);
                this.filter([{graphid:item.graphid, name: item.name(), inverted: inverted}]);
            }else{
                this.clear();
            }
        }
    });
});
