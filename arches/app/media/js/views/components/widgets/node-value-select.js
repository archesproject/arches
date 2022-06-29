define([
    'knockout',
    'viewmodels/node-value-select',
    'templates/views/components/widgets/node-value-select.htm',
    'bindings/select2-query',
], function(ko, NodeValueSelectViewModel, nodeValueSelectTemplate) {

    return ko.components.register('node-value-select', {
        viewModel: NodeValueSelectViewModel,
        template: nodeValueSelectTemplate,
    });
});
