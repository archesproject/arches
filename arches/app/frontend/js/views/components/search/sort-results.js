define(['jquery',
    'underscore',
    'views/components/search/base-filter',
    'knockout',
    'chosen'],
function($, _, BaseFilter, ko) {
    var componentName = 'sort-results';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({

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
            
        }),
        template: { require: 'text!templates/views/components/search/sort-results.htm' }
    });
});
