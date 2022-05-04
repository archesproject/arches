define([
    'knockout',
    'viewmodels/node-value-select',
    'utils/create-async-component',
    'bindings/select2-query',
], function(ko, NodeValueSelectViewModel, createAsyncComponent) {
    return createAsyncComponent(
        'node-value-select',
        NodeValueSelectViewModel,
        'templates/views/components/widgets/node-value-select.htm' 
    );
});
