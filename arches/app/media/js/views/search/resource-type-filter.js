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
                    //this.termFilter.addTag(this.name, this.inverted());
                }
                doQuery = true;
            }
            return doQuery;
        },

        clear: function() {
            this.filter.types.removeAll();
        },

        appendFilters: function(filterParams) {
            filterParams.typeFilter = ko.toJSON({
                types: this.filter.types(),
                inverted: this.inverted()
            });

            return this.filter.types().length !== 0;
        },

        selectModelType: function(item){
            console.log(item);
            if(!!item){
                this.filter.types([item.graphid]);
            }else{
                this.clear();
            }
        }
    });
});
