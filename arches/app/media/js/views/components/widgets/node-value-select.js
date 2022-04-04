define([
    'knockout',
    'viewmodels/node-value-select',
    'bindings/select2-query'
], function(ko, NodeValueSelectViewModel) {
    return ko.components.register('node-value-select', {
        viewModel: NodeValueSelectViewModel,
        template: window['node-value-select-widget-template']
    });
});
