define([
    'knockout',
    'arches',
    'views/components/search/base-filter',
    'templates/views/components/search/provisional-filter.htm',
], function(ko, arches, BaseFilter, provisionalFilterTemplate) {
    const componentName = 'provisional-filter';
    const viewModel = BaseFilter.extend({
        initialize: function(options) {
            options.name = 'Provisional Filter';
            this.translations = arches.translations;
            BaseFilter.prototype.initialize.call(this, options);
            this.filter = ko.observableArray();
            this.provisionalOptions = [{'name': 'Authoritative'},{'name': 'Provisional'}];
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
                var provisionalQuery = JSON.parse(query[componentName]);
                if (provisionalQuery.length > 0) {
                    provisionalQuery.forEach(function(type){
                        type.inverted = ko.observable(!!type.inverted);
                        this.getFilterByType('term-filter-type').addTag(type.provisionaltype, this.name, type.inverted);
                    }, this);
                    this.filter(provisionalQuery);
                }
            }
        },

        selectProvisional: function(item) {
            this.filter().forEach(function(val){
                this.getFilterByType('term-filter-type').removeTag(val.provisionaltype);
            }, this);

            if(!!item){
                var inverted = ko.observable(false);
                this.getFilterByType('term-filter-type').addTag(item.name, this.name, inverted);
                this.filter([{provisionaltype: item.name, inverted: inverted}]);

            }else{
                this.clear();
            }

        },

        clear: function() {
            this.filter.removeAll();
        }
    });

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: provisionalFilterTemplate,
    });
});
