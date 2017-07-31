define([
    'knockout',
    'arches'
], function (ko, arches) {
    var name = 'resource-instance-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            var self = this;
            this.resourceModels = [{
                graphid: null,
                name: ''
            }].concat(arches.resources);
            this.config = params.config;
            this.search = params.search;
            if (!this.search) {
                this.isEditable = params.graph ? params.graph.get('is_editable') : true;
            }
        },
        template: { require: 'text!datatype-config-templates/resource-instance' }
    });
    return name;
});
