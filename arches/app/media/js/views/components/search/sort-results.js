define([
    'jquery',
    'underscore',
    'views/components/search/base-filter',
    'knockout',
    'utils/create-async-component',
    'chosen',
    'templates/views/components/search/sort-results.htm'
], function($, _, BaseFilter, ko, createAsyncComponent) {
    var componentName = 'sort-results';
    const viewModel = BaseFilter.extend({
        initialize: function(options) {
            options.name = 'Sort Results';
            BaseFilter.prototype.initialize.call(this, options);

            this.filter = ko.observable('asc');
            this.filters[componentName](this);
            
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

    return createAsyncComponent(
        componentName,
        viewModel,
        'templates/views/components/search/sort-results.htm'
    );
});
