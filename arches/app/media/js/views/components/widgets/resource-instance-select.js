define([
    'knockout',
    'viewmodels/resource-instance-select',
    'bindings/select2-query'
], function(ko, ResourceInstanceSelectViewModel) {
    return ko.components.register('resource-instance-select-widget', {
        viewModel: ResourceInstanceSelectViewModel,
        template: {
            require: 'text!widget-templates/resource-instance-select'
        }
    });
});
