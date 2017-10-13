define(['arches', 'knockout', 'viewmodels/concept-select'], function (arches, ko, ConceptSelectViewModel) {
    var name = 'concept-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            this.search = params.search;
            if (this.search) {
                var self = this;
                var filter = params.filterValue();
                params.config = ko.observable({options:[]});
                this.op = ko.observable(filter.op || '');
                this.placeholder = ko.observable('Select a concept');
                this.multiple = ko.observable(false);
                this.searchValue = ko.observable(filter.val || '');
                this.node = params.node;
                if (!ko.isObservable(this.node.config.rdmCollection)) {
                    this.node.config.rdmCollection = ko.observable(this.node.config.rdmCollection);
                }
                params.value = this.searchValue;
                ConceptSelectViewModel.apply(this, [params]);
                this.filterValue = ko.computed(function () {
                    return {
                        op: self.op(),
                        val: self.searchValue()
                    }
                });
                params.filterValue(this.filterValue());
                this.filterValue.subscribe(function (val) {
                    params.filterValue(val);
                });
            } else {
                this.isEditable = true;
                if (params.graph) {
                    var cards = _.filter(params.graph.get('cards')(), function(card){return card.nodegroup_id === params.nodeGroupId()})
                    if (cards.length) {
                        this.isEditable = cards[0].is_editable
                    }
                } else if (params.widget) {
                    this.isEditable = params.widget.card.get('is_editable')
                }
                this.topConcept = params.config.rdmCollection;
                this.conceptCollections = arches.conceptCollections;
                this.conceptCollections.unshift({
                  'label': null,
                  'id': null
                })
            }
        },
        template: { require: 'text!datatype-config-templates/concept' }
    });
    return name;
});
