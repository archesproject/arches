import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import arches from 'arches';
import ConceptSelectViewModel from 'viewmodels/concept-select';
import conceptDatatypeTemplate from 'templates/views/components/datatypes/concept.htm';
import 'bindings/key-events-click';


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
                params._node(JSON.stringify(params))  // prevents dirty state trigger on Graph Designer concept node load
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

export default name;
