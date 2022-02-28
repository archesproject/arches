define([
    'knockout',
    'viewmodels/resource-instance-select',
    'bindings/select2-query'
], function(ko, ResourceInstanceSelectViewModel) {
    return ko.components.register('resource-instance-multiselect-widget', {
        viewModel: function(params) {
            params.multiple = true;
            params.datatype = 'resource-instance-list';
            ResourceInstanceSelectViewModel.apply(this, [params]);
        },
        template: {
            require: 'text!widget-templates/resource-instance-select'
        }
    });
});
