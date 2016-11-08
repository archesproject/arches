define(['knockout', 
        'knockout-mapping',
        'viewmodels/function', 
        'models/card',
        'bindings/chosen'], 
function (ko, koMapping, FunctionViewModel, CardModel, chosen) {
    return ko.components.register('views/functions/primary-name', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, params);
            this.cards = ko.observableArray();
            this.graph.cards.forEach(function(card){
                var c = new CardModel({'data':card});
                if(c.isContainer()){
                    c.get('cards').forEach(function(innercard){
                        this.cards.push(innercard);
                    }, this);
                }else{
                    this.cards.push(card);
                }
            }, this);

            this.string_template = params.config.string_template;
            this.nodegroup_id = params.config.nodegroup_id;
            this.nodegroup_id.subscribe(function(nodegroup_id){
                this.string_template(nodegroup_id);
                var nodes = _.filter(this.graph.nodes, function(node){
                    return node.nodegroup_id === nodegroup_id;
                }, this);
                var templateFragments = [];
                _.each(nodes, function(node){
                    templateFragments.push('<' + node.name + '>');
                }, this);


                var template = templateFragments.join(', ');
                this.string_template(template);

            }, this);

            window.setTimeout(function(){$("select[data-bind^=chosen]").trigger("chosen:updated")}, 300);
        },
        template: {
            require: 'text!function-templates/primary-name'
        }
    });
})