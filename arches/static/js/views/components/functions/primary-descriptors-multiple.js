define(['jquery',
        'arches',
        'knockout',
        'knockout-mapping',
        'viewmodels/function',
        'bindings/chosen'],
function ($, arches, ko, koMapping, FunctionViewModel, chosen) {
    return ko.components.register('views/components/functions/primary-descriptors-multiple', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);
            var nodegroups = {};
            this.cards = ko.observableArray();
            this.loading = ko.observable(false);

            this.graph.cards.forEach(function(card){
                var found = !!_.find(this.graph.nodegroups, function(nodegroup){
                    return nodegroup.parentnodegroup_id === card.nodegroup_id
                }, this);
                if(!found && !(card.nodegroup_id in nodegroups)){
                    this.cards.push(card);
                    nodegroups[card.nodegroup_id] = true;
                }
            }, this);

            this.name = params.config.name;
            this.description = params.config.description;
            this.map_popup = params.config.map_popup;
            this.marker = params.config.marker;

            _.each([this.name, this.description, this.map_popup, this.marker], function(property){
                property.nodegroup_id.subscribe(function(nodegroup_id){
                    var elements = [];
                    if(typeof(nodegroup_id) ==="string"){
                        elements = [nodegroup_id];
                    }else{
                         elements=nodegroup_id;
                    }
                    var template = '';

                    for (var i=0; i < elements.length; i++){
                        property.string_template(elements[i]);
                        var nodes = _.filter(this.graph.nodes, function(node){
                            return node.nodegroup_id === elements[i];
                        }, this);
                        var templateFragments = [];
                        _.each(nodes, function(node){
                            templateFragments.push('<' + node.name + '>');
                        }, this);

                        template = template + templateFragments.join(', ');
                    }

                    property.string_template(template);
                }, this);
            }, this)

            this.reindexdb = function(){
                this.loading(true);
                $.ajax({
                    type: "POST",
                    url: arches.urls.reindex,
                    context: this,
                    data: JSON.stringify({'graphids': [this.graph.graphid]}),
                    error: function(response) {
                        console.log('error');
                    },
                    complete: function(){
                        this.loading(false);
                    }
                });
            }

            window.setTimeout(function(){$("select[data-bind^=chosen]").trigger("chosen:updated")}, 300);
        },
        template: {
            require: 'text!templates/views/components/functions/primary-descriptors-multiple.htm'
        }
    });
})
