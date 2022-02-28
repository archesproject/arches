define([
    'knockout',
    'views/components/search/base-filter'
], function(ko, BaseFilter) {
    var componentName = 'provisional-filter';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({
            initialize: function(options) {
                options.name = 'Provisional Filter';
                this.requiredFilters = ['term-filter'];
                BaseFilter.prototype.initialize.call(this, options);
                this.filter = ko.observableArray();
                this.provisionalOptions = [{'name': 'Authoritative'},{'name': 'Provisional'}];

                if (this.requiredFiltersLoaded() === false) {
                    this.requiredFiltersLoaded.subscribe(function() {
                        this.restoreState();
                    }, this);
                } else {
                    this.restoreState();
                }

                var filterUpdated = ko.computed(function() {
                    return JSON.stringify(ko.toJS(this.filter()));
                }, this);
                filterUpdated.subscribe(function() {
                    this.updateQuery();
                }, this);

                this.filters[componentName](this);
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
                            this.getFilter('term-filter').addTag(type.provisionaltype, this.name, type.inverted);
                        }, this);
                        this.filter(provisionalQuery);
                    }
                }
            },

            selectProvisional: function(item) {
                this.filter().forEach(function(val){
                    this.getFilter('term-filter').removeTag(val.provisionaltype);
                }, this);

                if(!!item){
                    var inverted = ko.observable(false);
                    this.getFilter('term-filter').addTag(item.name, this.name, inverted);
                    this.filter([{provisionaltype: item.name, inverted: inverted}]);

                }else{
                    this.clear();
                }

            },

            clear: function() {
                this.filter.removeAll();
            }
        }),
        template: { require: 'text!templates/views/components/search/provisional-filter.htm' }
    });
});
