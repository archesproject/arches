import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import BaseFilter from 'views/components/search/base-filter';
import sortResultsTemplate from 'templates/views/components/search/sort-results.htm';
import 'chosen';


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

export default ko.components.register(componentName, {
    viewModel: viewModel,
    template: sortResultsTemplate,
});
