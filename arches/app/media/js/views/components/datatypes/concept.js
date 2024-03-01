define([
    'jquery',
    'underscore',
    'knockout', 
    'arches', 
    'viewmodels/concept-select', 
    'templates/views/components/datatypes/concept.htm',
    'bindings/key-events-click', 
], function($, _, ko, arches, ConceptSelectViewModel, conceptDatatypeTemplate) {
    var name = 'concept-datatype-config';
    const viewModel = function(params) {
        const self = this;
        this.search = params.search;
        if (this.search) {
            var filter = params.filterValue();
            params.config = ko.observable({
                options:[],
                placeholder: arches.translations.selectAnOption
            });
             
            this.op = ko.observable(filter.op || 'eq');
            this.multiple = ko.observable(false);
            this.searchValue = ko.observable(filter.val || '');
            this.node = params.node;
            if (!ko.isObservable(this.node.config.rdmCollection)) {
                this.node.config.rdmCollection = ko.observable(this.node.config.rdmCollection);
            }
            params.value = this.searchValue;
            ConceptSelectViewModel.apply(this, [params]);
            this.filterValue = ko.computed(function() {
                return {
                    op: self.op(),
                    val: self.searchValue()
                };
            });
            params.filterValue(this.filterValue());
            this.filterValue.subscribe(function(val) {
                params.filterValue(val);
            });
        } else {
            this.conceptCollections = ko.observableArray([]);
            this.isEditable = true;
            if (params.graph) {
                var cards = _.filter(params.graph.get('cards')(), function(card){return card.nodegroup_id === params.nodeGroupId();});
                if (cards.length) {
                    this.isEditable = cards[0].is_editable;
                }
            } else if (params.widget) {
                this.isEditable = params.widget.card.get('is_editable');
            }
            this.topConcept = params.config.rdmCollection;
            this.initialTopConcept = this.topConcept();
            if (arches.conceptCollections.length === 0) {
                $.ajax({
                    url: arches.urls.get_concept_collections,
                    type: 'json'
                }).done(function(data){
                    arches.conceptCollections = data;
                    self.conceptCollections(data);
                    self.conceptCollections.unshift({
                        'label': null,
                        'id': null
                    });
                    self.topConcept(self.initialTopConcept);
                }).fail(function(error){
                    console.log(error);
                });
            } else {
                this.conceptCollections(arches.conceptCollections);
                if (this.conceptCollections()[0].label != null) {
                    this.conceptCollections.unshift({
                        'label': null,
                        'id': null
                    });
                }
            }
        }
    };

    ko.components.register(name, {
        viewModel: viewModel,
        template: conceptDatatypeTemplate,
    });
    
    return name;
});
