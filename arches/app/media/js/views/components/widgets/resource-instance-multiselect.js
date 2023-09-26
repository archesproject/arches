define([
    'knockout',
    'viewmodels/resource-instance-select',
    'templates/views/components/widgets/resource-instance-select.htm',
    'bindings/select2-query',
], function(ko, ResourceInstanceSelectViewModel, resourceInstanceSelectWidgetTemplate) {
    const viewModel =  function(params) {
        params.multiple = true;
        params.datatype = 'resource-instance-list';
        ResourceInstanceSelectViewModel.apply(this, [params]);
    };

    return ko.components.register('resource-instance-multiselect-widget', {
        viewModel: viewModel,
        template: resourceInstanceSelectWidgetTemplate,
    });
});
