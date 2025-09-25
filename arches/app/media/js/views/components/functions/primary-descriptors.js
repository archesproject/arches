import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import koMapping from 'knockout-mapping';
import arches from 'arches';
import FunctionViewModel from 'viewmodels/function-view-model';
import chosen from 'bindings/chosen';
import primaryDescriptorsFunctionTemplate from 'templates/views/components/functions/primary-descriptors.htm';


const viewModel =  function(params) {
        
    FunctionViewModel.apply(this, arguments);
    var nodegroups = {};
    this.cards = ko.observableArray();
    this.loading = ko.observable(false);
    this.cards.unshift({
        'name': null,
    });

    this.graph.cards.forEach(function(card){
        this.cards.push(card);
        nodegroups[card.nodegroup_id] = true;
    }, this);

    this.name = params.config.descriptor_types.name;

    this.description = params.config.descriptor_types.description;
    this.map_popup = params.config.descriptor_types.map_popup;

    _.each([this.name, this.description, this.map_popup], function(property){
        if (property.nodegroup_id) {
            property.nodegroup_id.subscribe(function(nodegroup_id){
                property.string_template(nodegroup_id);
                var nodes = _.filter(this.graph.nodes, function(node){
                    return node.nodegroup_id === nodegroup_id;
                }, this);
                var templateFragments = [];
                _.each(nodes, function(node){
                    templateFragments.push('<' + node.name + '>');
                }, this);

                var template = templateFragments.join(', ');
                property.string_template(template);
            }, this);
        }
    }, this);

    this.reindexdb = function(){
        this.loading(true);
        $.ajax({
            type: "POST",
            url: arches.urls.reindex,
            context: this,
            data: JSON.stringify({'graphids': [this.graph.graphid]}),
            error: function() {
                console.log('error');
            },
            complete: function(){
                this.loading(false);
            }
        });
    };
    window.setTimeout(function(){$("select[data-bind^=chosen]").trigger("chosen:updated");}, 300);
};

export default ko.components.register('views/components/functions/primary-descriptors', {
    viewModel: viewModel,
    template: primaryDescriptorsFunctionTemplate,
});
