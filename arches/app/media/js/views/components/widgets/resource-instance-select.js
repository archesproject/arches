define([
    'knockout',
    'utils/create-async-component',
    'bindings/select2-query',
], function(ko, createAsyncComponent) {
    const viewModel = function(params) {
        const ResourceInstanceSelectViewModel = require('viewmodels/resource-instance-select');
        params.multiple = false;
        params.datatype = 'resource-instance';
        ResourceInstanceSelectViewModel.apply(this, [params]);
    };

    return createAsyncComponent(
        'resource-instance-select-widget',
        viewModel,
        'templates/views/components/widgets/resource-instance-select.htm'
    );
});
