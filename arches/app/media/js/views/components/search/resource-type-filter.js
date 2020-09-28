define([
    'knockout',
    'views/components/search/base-filter'
], function(ko, BaseFilter) {
    var componentName = 'resource-type-filter';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({
            initialize: function(options) {
                options.name = 'Resource Type Filter';
                this.requiredFilters = ['term-filter'];
                BaseFilter.prototype.initialize.call(this, options);
                
                this.filter = ko.observableArray();

                var filterUpdated = ko.computed(function() {
                    return JSON.stringify(ko.toJS(this.filter()));
                }, this);
                filterUpdated.subscribe(function() {
                    this.updateQuery();
                }, this);

                this.filters[componentName](this);

                if (this.requiredFiltersLoaded() === false) {
                    this.requiredFiltersLoaded.subscribe(function() {
                        this.restoreState();
                    }, this);
                } else {
                    this.restoreState();
                }
            },

            updateQuery: function() {
                var queryObj = this.query();
                if(this.filter().length > 0){
                    queryObj[componentName] = ko.toJSON(this.filter);
                } else {
                    delete queryObj[componentName];
                }
                this.query(queryObj);
            },

            restoreState: function() {
                var query = this.query();
                if (componentName in query) {
                    var resourceTypeQuery = JSON.parse(query[componentName]);
                    if (resourceTypeQuery.length > 0) {
                        resourceTypeQuery.forEach(function(type){
                            type.inverted = ko.observable(!!type.inverted);
                            this.getFilter('term-filter').addTag(type.name, this.name, type.inverted);
                        }, this);
                        this.filter(resourceTypeQuery);
                    }
                }
            },

            clear: function() {
                this.filter.removeAll();
            },

            selectModelType: function(item){
                this.filter().forEach(function(item){
                    this.getFilter('term-filter').removeTag(item.name);
                }, this);
                if(!!item){
                    var inverted = ko.observable(false);
                    this.getFilter('term-filter').addTag(item.name(), this.name, inverted);
                    this.filter([{graphid:item.graphid, name: item.name(), inverted: inverted}]);
                }else{
                    this.clear();
                }
            }
        }),
        template: { require: 'text!templates/views/components/search/resource-type-filter.htm' }
    });
});
