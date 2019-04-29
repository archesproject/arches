define([
    'knockout',
    'knockout-mapping',
    'underscore',
    'views/components/search/base-filter',
    'bindings/term-search'
], function(ko, koMapping, _, BaseFilter, termSearchComponent) {
    return ko.components.register('term-filter', {
        viewModel: BaseFilter.extend({
            initialize: function(options) {
                options.name = 'Term Filter';
                BaseFilter.prototype.initialize.call(this, options);

                this.filter.terms = ko.observableArray();
                this.filter.tags = ko.observableArray();

                var updatedTerms = ko.computed(function() {
                    return ko.toJS(this.filter.terms);
                }, this);
                updatedTerms.subscribe(function() {
                    this.updateQuery();
                }, this);

                options.filters['term-filter'](this);

                this.restoreState();
            },

            updateQuery: function() {
                var terms = _.filter(this.filter.terms(), function(term){
                    return term.type === 'string' || term.type === 'concept' || term.type === 'term';
                }, this);
                
                var queryObj = this.query();
                if (terms.length > 0){
                    queryObj.termFilter = ko.toJSON(terms);
                } else {
                    delete queryObj.termFilter;
                }
                this.query(queryObj);
            },

            restoreState: function() {
                var query = this.query();
                if ('termFilter' in query) {
                    query.termFilter = JSON.parse(query.termFilter);
                    if (query.termFilter.length > 0) {
                        query.termFilter.forEach(function(term){
                            term.inverted = ko.observable(term.inverted);
                        });
                        this.filter.terms(query.termFilter);
                    }
                }
            },

            clear: function() {
                this.filter.terms.removeAll();
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
                    }
                });
                return has_tag;
            }
        }),
        template: { require: 'text!templates/views/components/search/term-filter.htm' }
    });
});
