define([
    'knockout',
    'underscore',
    'arches',
    'views/components/widgets/resource-instance-select'
], function (ko, _, arches) {
    var name = 'resource-instance-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            var self = this;
            this.resourceModels = [{
                graphid: null,
                name: ''
            }].concat(_.filter(arches.graphs, function (graph) {
                return graph.isresource && graph.isactive;
            }));
            this.config = params.config;
            this.search = params.search;
            if (!this.search) {
                this.isEditable = params.graph ? params.graph.get('is_editable') : true;
            } else {
                var filter = params.filterValue();
                this.node = params.node;
                this.op = ko.observable(filter.op || '');
                this.searchValue = ko.observable(filter.val || '');
                this.filterValue = ko.computed(function () {
                    return {
                        op: self.op(),
                        val: self.searchValue()
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
