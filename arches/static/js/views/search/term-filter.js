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
            this.filter.tags = ko.observableArray();
        },

        restoreState: function(query) {
            var doQuery = false;
            if ('termFilter' in query) {
                query.termFilter = JSON.parse(query.termFilter);
                if (query.termFilter.length > 0) {
                    query.termFilter.forEach(function(term){
                        term.inverted = ko.observable(term.inverted);
                    })
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
                return term.type === 'string' || term.type === 'concept' || term.type === 'term';
            }, this);

            if(terms.length > 0){
                filterParams.termFilter = ko.toJSON(terms);
            }

            return terms.length > 0;
        },

        addTag: function(term, type, inverted){
            this.filter.tags.unshift({
                inverted: inverted,
                type: type,
                context: '',
                context_label: '',
                id: term,
                text: term,
                value: term
            });
        },

        removeTag: function(term){
            this.filter.tags.remove(function(term_item){
                return term_item.id == term && term_item.text == term && term_item.value == term;
            });
        },

        hasTag: function(tag_text){
            var has_tag = false;
            this.filter.terms().forEach(function(term_item){
                if (term_item.text == tag_text) {
                    has_tag = true;
                };
            });
            return has_tag;
        }

    });
});
