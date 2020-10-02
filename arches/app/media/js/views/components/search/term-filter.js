define([
    'knockout',
    'knockout-mapping',
    'underscore',
    'views/components/search/base-filter',
    'bindings/term-search'
], function(ko, koMapping, _, BaseFilter, termSearchComponent) {
    var componentName = 'term-filter';
    return ko.components.register(componentName, {
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

                this.filter.tags.subscribe(function(tags){
                    _.each(tags, function(tag){
                        if(tag.status === 'deleted'){
                            var found = _.find(this.filter.tags, function(currentTag){
                               return tag.value.type === currentTag.type;
                            }, this);
                            if(!found){
                                _.each(this.filters, function(filter){
                                    if(!!filter() && filter().name === tag.value.type){
                                        filter().clear();
                                    }
                                }, this);
                            }
                        }
                    }, this);
                }, this, "arrayChange");

                this.filters[componentName](this);
                this.restoreState();
            },

            updateQuery: function() {
                var terms = _.filter(this.filter.terms(), function(term){
                    return term.type === 'string' || term.type === 'concept' || term.type === 'term';
                }, this);
                
                var queryObj = this.query();
                if (terms.length > 0){
                    queryObj[componentName] = ko.toJSON(terms);
                } else {
                    delete queryObj[componentName];
                }
                this.query(queryObj);
            },

            restoreState: function() {
                var query = this.query();
                if (componentName in query) {
                    var termQuery = JSON.parse(query[componentName]);
                    if (termQuery.length > 0) {
                        termQuery.forEach(function(term){
                            term.inverted = ko.observable(term.inverted);
                        });
                        this.filter.terms(termQuery);
                    }
                }
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
            },

            clear: function() {
                this.filter.terms.removeAll();
                this.filter.tags.removeAll();
            }
        }),
        template: { require: 'text!templates/views/components/search/term-filter.htm' }
    });
});
