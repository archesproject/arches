define([
    'jquery',
    'underscore',
    'views/components/search/base-filter',
    'knockout',
    'templates/views/components/search/sort-results.htm',
    'chosen',
], function($, _, BaseFilter, ko, sortResultsTemplate) {
    var componentName = 'sort-results';
    const viewModel = BaseFilter.extend({
        initialize: function(options) {
            options.name = 'Sort Results';
            BaseFilter.prototype.initialize.call(this, options);

            this.filter = ko.observable('');
            this.searchFilterVms[componentName](this);
            
            this.filter.subscribe(function(){
                this.updateQuery();
            }, this);

            this.restoreState();
        },

        updateQuery: function() {
            var queryObj = this.query();
            if(this.filter() === '') {
                delete queryObj[componentName];
            } else {
                queryObj[componentName] = this.filter();
            }
            this.query(queryObj);
        },

        restoreState: function(){
            var query = this.query();
            if (componentName in query) {
                this.filter(query[componentName]);
            }
        },

        clear: function(){
            this.filter('');
        }
        
    });

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: sortResultsTemplate,
    });
});
