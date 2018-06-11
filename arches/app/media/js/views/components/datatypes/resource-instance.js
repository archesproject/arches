define([
    'knockout',
    'underscore',
    'view-data',
    'views/components/widgets/resource-instance-select'
], function (ko, _, data) {
    var name = 'resource-instance-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            var self = this;
            this.resourceModels = [{
                graphid: null,
                name: ''
            }].concat(_.filter(data.createableResources, function (graph) {
                return graph;
            }));
            this.config = params.config;
            this.search = params.search;
            if (!this.search) {
                this.isEditable = true;
                if (params.graph) {
                    var cards = _.filter(params.graph.get('cards')(), function(card){return card.nodegroup_id === params.nodeGroupId()})
                    if (cards.length) {
                        this.isEditable = cards[0].is_editable
                    }
                } else if (params.widget) {
                    this.isEditable = params.widget.card.get('is_editable')
                }
            } else {
                var filter = params.filterValue();
                this.node = params.node;
                this.op = ko.observable(filter.op || '');
                this.searchValue = ko.observable(filter.val || '');
                this.filterValue = ko.computed(function () {
                    return {
                        op: self.op(),
                        val: self.searchValue() || ''
                    }
                }).extend({ throttle: 750 });
                params.filterValue(this.filterValue());
                this.filterValue.subscribe(function (val) {
                    params.filterValue(val);
                });

            }
        },
        template: { require: 'text!datatype-config-templates/resource-instance' }
    });
    return name;
});
