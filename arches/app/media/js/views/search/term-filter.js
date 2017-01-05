define([
    'knockout',
    'underscore',
    'views/search/base-filter',
    'bindings/term-search'
], function(ko, _, BaseFilter, termSearchComponent) {
    return BaseFilter.extend({
        initialize: function(options) {
            BaseFilter.prototype.initialize.call(this, options);
            
            this.name = 'Term Filter';
            
            this.filter.terms = ko.observableArray();
        },

        restoreState: function(query) {
            var doQuery = false;
            if ('termFilter' in query) {
                query.termFilter = JSON.parse(query.termFilter);
                if (query.termFilter.length > 0) {
                    this.filter.terms(query.termFilter);
                }
                doQuery = true;
            }
            return doQuery;
        },

        clear: function() {
            this.filter.terms.removeAll();
        },

        appendFilters: function(filterParams) {
            var terms = _.filter(this.filter.terms(), function(term){
                return term.type !== 'filter-flag';
            }, this);

            filterParams.termFilter = ko.toJSON(terms);
            return terms.length !== 0;
        },

        addTag: function(term, inverted){
            this.filter.terms.unshift({
                inverted: inverted,
                type: 'filter-flag',
                context: '',
                context_label: '',
                id: term,
                text: term,
                value: term
            });

            //this.updateTerms(this.filter.terms);
        },

        removeTag: function(term){
            this.filter.terms.remove(function(term_item){ 
                return term_item.id == term && term_item.text == term && term_item.value == term; 
            });

            //this.updateTerms(terms);
        },

        // updateTerms: function(terms){
        //     //searchbox.select2('data', terms);

        //     $('.resource_search_widget').find('.select2-search-choice').each(function(i, el) {
        //         if ($(el).data('select2-data').type === 'filter-flag') {
        //             $(el).addClass('filter-flag');
        //         }
        //         if ($(el).data('select2-data').inverted) {
        //             $(el).addClass('inverted');
        //         }
        //     });
        // }


    });
});
