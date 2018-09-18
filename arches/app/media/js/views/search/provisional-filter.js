define([
    'knockout',
    'views/search/base-filter'
], function(ko, BaseFilter) {
    return BaseFilter.extend({
        initialize: function(options) {
            BaseFilter.prototype.initialize.call(this, options);
            this.name = 'Provisional Filter';
            this.filter = ko.observableArray();
            this.provisionalOptions = [{'name': 'Authoritative'},{'name': 'Provisional'}]
        },

        restoreState: function(query) {
            var doQuery = false;
            if ('provisionalFilter' in query) {
                query.provisionalFilter = JSON.parse(query.provisionalFilter);
                if (query.provisionalFilter.length > 0) {
                    query.provisionalFilter.forEach(function(type){
                        type.inverted = ko.observable(!!type.inverted);
                        this.termFilter.addTag(type.provisionaltype, this.provisionaltype, type.inverted);
                    }, this)
                    this.filter(query.provisionalFilter);
                }
                doQuery = true;
            }
            return doQuery;
        },

        selectProvisional: function(item) {
            this.filter().forEach(function(val){
                this.termFilter.removeTag(val.provisionaltype);
            }, this);

            if(!!item){
                var inverted = ko.observable(false)
                this.termFilter.addTag(item.name, this.name, inverted);
                this.filter([{provisionaltype: item.name, inverted: inverted}]);

            }else{
                this.clear();
            }

        },

        clear: function() {
            this.filter.removeAll();
        },

        appendFilters: function(filterParams) {
            if(this.filter().length > 0){
                filterParams.provisionalFilter = ko.toJSON(this.filter);
            }

            return this.filter().length > 0;
        }

    });
});
