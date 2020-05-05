define([
    'knockout',
    'viewmodels/resource-instance-select',
    'bindings/select2-query'
], function(ko, ResourceInstanceSelectViewModel) {
    return ko.components.register('resource-instance-select-widget', {
        viewModel: function(params) {
            params.multiple = false;
            params.datatype = 'resource-instance';
            ResourceInstanceSelectViewModel.apply(this, [params]);
        },
        template: {
            require: 'text!widget-templates/resource-instance-select'
        }
    });
});
