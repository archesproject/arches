import ko from 'knockout';
import arches from 'arches';
import BaseFilter from 'views/components/search/base-filter';
import lifecycleStateFilterTemplate from 'templates/views/components/search/lifecycle-state-filter.htm';


var componentName = 'lifecycle-state-filter';
const viewModel = BaseFilter.extend({
    initialize: async function(options) {
        options.name = 'Lifecycle State Filter';

        this.requiredFilters = ['term-filter'];
        BaseFilter.prototype.initialize.call(this, options);

        this.lifecycleStates = ko.observableArray();
        this.filter = ko.observableArray();

        const self = this;  // eslint-disable-line @typescript-eslint/no-this-alias

        const response = await fetch(arches.urls.api_resource_instance_lifecycle_states);
        if (response.ok) {
            const data = await response.json();
            data.forEach(function(lifecycleState) {
                self.lifecycleStates.push(lifecycleState);
            });
        } else {
            console.error('Failed to fetch resource instance list');
        }

        var filterUpdated = ko.computed(function() {
            return JSON.stringify(ko.toJS(this.filter()));
        }, this);
        filterUpdated.subscribe(function() {
            this.updateQuery();
        }, this);

        this.filters[componentName](this);

        if (this.requiredFiltersLoaded() === false) {
            this.requireFiltersLoadedSubscription = this.requiredFiltersLoaded.subscribe(function() {
                this.restoreState();
                self.requireFiltersLoadedSubscription.dispose();
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
            var lifecycleStateQuery = JSON.parse(query[componentName]);
            if (lifecycleStateQuery.length > 0) {
                lifecycleStateQuery.forEach(function(type){
                    type.inverted = ko.observable(!!type.inverted);
                    this.getFilter('term-filter').addTag(type.name, this.name, type.inverted);
                }, this);
                this.filter(lifecycleStateQuery);
            }
        }
    },

    clear: function() {
        this.filter.removeAll();
    },

    selectLifecycleState: function(item){
        this.filter().forEach(function(filterItem){
            this.getFilter('term-filter').removeTag(filterItem.name);
        }, this);

        if (item) {
            var inverted = ko.observable(false);
            this.getFilter('term-filter').addTag(item.name, this.name, inverted);
            this.filter([{id: item.id, name: item.name, inverted: inverted}]);
        }
        else{
            this.clear();
        }
    }
});

export default ko.components.register(componentName, {
    viewModel: viewModel,
    template: lifecycleStateFilterTemplate,
});
