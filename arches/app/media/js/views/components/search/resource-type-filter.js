import ko from 'knockout';
import arches from 'arches';
import BaseFilter from 'views/components/search/base-filter';
import resourceTypeFilterTemplate from 'templates/views/components/search/resource-type-filter.htm';


var componentName = 'resource-type-filter';
const viewModel = BaseFilter.extend({
    initialize: async function(options) {
        options.name = 'Resource Type Filter';
        BaseFilter.prototype.initialize.call(this, options);
        this.resourceModels = ko.observableArray();
        this.filter = ko.observableArray();
        const self = this;

        const response = await fetch(arches.urls.api_search_component_data + componentName);
        if (response.ok) {
            const data = await response.json();
            data.resources.forEach(function(res) {
                //if (res.isactive === true) { // TODO: Uncomment once active flag is re-added to graph model
                self.resourceModels.push(res);
                //}
            });
            self.resourceModels.sort(function(a,b) {
                return a.name.toLowerCase().localeCompare(b.name.toLowerCase());
            });  // sort resource model list alphabetically
        } else {
            // eslint-disable-next-line no-console
            console.log('Failed to fetch resource instance list');
        }

        var filterUpdated = ko.computed(function() {
            return JSON.stringify(ko.toJS(this.filter()));
        }, this);
        filterUpdated.subscribe(function() {
            this.updateQuery();
        }, this);

        this.searchFilterVms[componentName](this);

        if (this.searchViewFiltersLoaded() === false) {
            this.searchViewFiltersLoaded.subscribe(function() {
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
                    this.getFilterByType('term-filter-type').addTag(type.name, this.name, type.inverted);
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
            this.getFilterByType('term-filter-type').removeTag(item.name);
        }, this);
        if(!!item){
            var inverted = ko.observable(false);
            this.getFilterByType('term-filter-type').addTag(item.name, this.name, inverted);
            this.filter([{graphid:item.graphid, name: item.name, inverted: inverted}]);
        }else{
            this.clear();
        }
    }
});

export default ko.components.register(componentName, {
    viewModel: viewModel,
    template: resourceTypeFilterTemplate,
});
