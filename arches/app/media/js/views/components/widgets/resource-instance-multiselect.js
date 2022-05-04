define([
    'knockout',
    'viewmodels/resource-instance-select',
    'utils/create-async-component',
    'bindings/select2-query',
], function(ko, ResourceInstanceSelectViewModel, createAsyncComponent) {
    const viewModel =  function(params) {
        params.multiple = true;
        params.datatype = 'resource-instance-list';
        ResourceInstanceSelectViewModel.apply(this, [params]);
    };

    return createAsyncComponent(
        'resource-instance-multiselect-widget',
        viewModel,
        'templates/views/components/widgets/resource-instance-select.htm'

    );
});
