define([
    'knockout',
    'views/search/base-filter'
], function(ko, BaseFilter) {
    return BaseFilter.extend({
        initialize: function(options) {
            BaseFilter.prototype.initialize.call(this, options);
            
            this.name = 'Resource Type Filter';
            
            this.filter.types = ko.observableArray();
            
            this.enabled = ko.computed(function(){
                return this.filter.types().length > 0;
            }, this);

            this.enabled.subscribe(function(enabled){
                console.log(enabled)
            })
        },

        restoreState: function(query) {
            var doQuery = false;
            if ('typeFilter' in query) {
                query.typeFilter = JSON.parse(query.typeFilter);
                if (query.typeFilter.types.length > 0) {
                    this.filter.types(query.typeFilter.types);
                    this.inverted(query.typeFilter.inverted);
                    query.typeFilter.types.forEach(function(item){
                        this.termFilter.addTag(item.name, this.inverted);
                    }, this);
                }
                doQuery = true;
            }
            return doQuery;
        },

        clear: function() {
            this.filter.types.removeAll();
        },

        appendFilters: function(filterParams) {
            if(this.filter.types().length !== 0){
                filterParams.typeFilter = ko.toJSON({
                    types: this.filter.types,
                    inverted: this.inverted
                });
            }

            return this.filter.types().length !== 0;
        },

        selectModelType: function(item){
            console.log(item);
            this.filter.types().forEach(function(item){
                this.termFilter.removeTag(item.name);
            }, this);
            if(!!item){
                this.termFilter.addTag(item.name(), this.inverted);
                this.filter.types([{graphid:item.graphid, name: item.name()}]);
            }else{
                this.clear();
            }
        }
    });
});
