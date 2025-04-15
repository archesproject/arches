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

        this.sortBy = ko.observable('');
        this.sortOrder = ko.observable('asc');

        this.sortSymbol=ko.computed(function() {
            return this.sortOrder() === "asc" ? 
                '<i class="fa fa-sort-amount-asc fa-lg"></i>' :  
                '<i class="fa fa-sort-amount-desc fa-lg"></i>'
        }, this);

        this.searchFilterVms[componentName](this);

        this.sortBy.subscribe(function(){
            this.updateQuery();
        }, this);

        this.sortOrder.subscribe(function(){
            this.updateQuery();
        }, this);

        this.restoreState();
    },

    updateQuery: function() {
        var queryObj = this.query();
        if(this.sortBy() === '') {
            delete queryObj['sort-by'];
        } else {
            queryObj['sort-by'] = this.sortBy();
        }

        if(this.sortOrder() === '' | this.sortBy() === '') {
            delete queryObj['sort-order'];
        } else {
            queryObj['sort-order'] = this.sortOrder();
        }
                
        this.query(queryObj);
    },

    restoreState: function(){
        var query = this.query();
        if ('sort-by' in query) {
            this.sortBy(query['sort-by']);
        }

        if ('sort-order' in query) {
            this.sortOrder(query['sort-order']);
        }
    },

    clear: function(){
        this.sortBy('');
        this.sortOrder('')
    }

});

export default ko.components.register(componentName, {
    viewModel: viewModel,
    template: sortResultsTemplate,
});
