define(['knockout', 
        'knockout-mapping',
        'viewmodels/function', 
        'models/card',
        'chosen'], 
function (ko, koMapping, FunctionViewModel, CardModel, data) {
    return ko.components.register('primary-name', {
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

            this.primaryNameTemplate = ko.observable();
            this.selectedNodegroup = ko.observable();
            this.selectedNodegroup.subscribe(function(nodegroup_id){
                this.primaryNameTemplate(nodegroup_id);
                var nodes = _.filter(this.graph.nodes, function(node){
                    return node.nodegroup_id === nodegroup_id;
                }, this);
                var templateFragments = [];
                _.each(nodes, function(node){
                    templateFragments.push('<' + node.name + '{' + node.nodeid + '}>');
                }, this);


                var template = templateFragments.join(', ');
                this.primaryNameTemplate(template);

            }, this);
            koMapping.fromJS({
                string_template: this.primaryNameTemplate,
                nodegroup_id: this.selectedNodegroup
            },params.primaryNameConfig);
        },
        template: {
            require: 'text!function-templates/primary-name'
        }
    });
})