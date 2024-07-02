define([
    'knockout',
    'arches',
    'views/components/search/base-filter',
    'templates/views/components/search/lifecycle-state-filter.htm',
], function(ko, arches, BaseFilter, lifecycleStateFilterTemplate) {
    var componentName = 'lifecycle-state-filter';
    const viewModel = BaseFilter.extend({
        initialize: async function(options) {
            options.name = 'Lifecycle State Filter';


            this.requiredFilters = ['term-filter'];
            BaseFilter.prototype.initialize.call(this, options);
            this.lifecycleStates = ko.observableArray();
            this.filter = ko.observableArray();
            const self = this;  // eslint-disable-line @typescript-eslint/no-this-alias

            const response = await fetch(arches.urls.api_resource_instance_lifecycle );

            if (response.ok) {
                const data = await response.json();
                data.forEach(function(lifecycleState) {
                    self.lifecycleStates.push(lifecycleState);
                });
            } else {
                 
                console.log('Failed to fetch resource instance list');
            }

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

        selectFoo: function(item){
            this.filter().forEach(function(item){
                this.getFilter('term-filter').removeTag(item.name);
            }, this);
            if(item){
                console.log("!!", item);
                var inverted = ko.observable(false);
                this.getFilter('term-filter').addTag(item, this.name, inverted);
                this.filter([{name: item, inverted: inverted}]);
            }else{
                this.clear();
            }
        }
    });

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: lifecycleStateFilterTemplate,
    });
});
