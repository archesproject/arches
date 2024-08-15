define([
    'knockout',
    'knockout-mapping',
    'underscore',
    'views/components/search/base-filter',
    'arches',
    'templates/views/components/search/term-filter.htm',
    'bindings/term-search', 
], function(ko, koMapping, _, BaseFilter, arches, termFilterTemplate) {
    var componentName = 'term-filter';
    const viewModel = BaseFilter.extend({
        initialize: function(options) {
            options.name = 'Term Filter';
            BaseFilter.prototype.initialize.call(this, options);

            this.filter.terms = ko.observableArray();
            this.filter.tags = ko.observableArray();

            this.language = ko.observable("*");
            this.languages = ko.observableArray();
            const languages = arches.languages.slice();
            languages.unshift({"code": "*", "name": "All"});
            this.languages(languages);

            var updatedTerms = ko.computed(function() {
                return ko.toJS(this.filter.terms);
            }, this);

            updatedTerms.subscribe(function() {
                this.updateQuery();
            }, this);

            this.language.subscribe(function() {
                this.updateQuery();
            }, this);

            this.filter.tags.subscribe(function(tags){
                _.each(tags, function(tag){
                    if(tag.status === 'deleted'){
                        var found = _.find(this.filter.tags, function(currentTag){
                            return tag.value.type === currentTag.type;
                        }, this);
                        if(!found){
                            _.each(this.searchFilterVms, function(filter){
                                if(!!filter() && filter().name === tag.value.type){
                                    filter().clear();
                                }
                            }, this);
                        }
                    }
                }, this);
            }, this, "arrayChange");

            this.searchFilterVms[componentName](this);
            this.restoreState();
        },

        updateQuery: function() {
            var terms = _.filter(this.filter.terms(), function(term){
                return term.type === 'string' || term.type === 'concept' || term.type === 'term';
            }, this);
            
            var queryObj = this.query();
            if (terms.length > 0){
                queryObj[componentName] = ko.toJSON(terms);
                queryObj['language'] = this.language();
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
            if(!this.hasTag(term)){
                this.filter.tags.unshift({
                    inverted: inverted,
                    type: type,
                    context: '',
                    context_label: '',
                    id: term,
                    text: term,
                    value: term
                });
            }
        },

        removeTag: function(term){
            this.filter.tags.remove(function(term_item){
                return term_item.id == term && term_item.text == term && term_item.value == term;
            });
        },

        hasTag: function(tag_text){
            var has_tag = false;
            this.filter.tags().forEach(function(term_item){
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
    });

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: termFilterTemplate,
    });
});
