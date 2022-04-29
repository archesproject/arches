define([
    'knockout',
    'viewmodels/card-component',
    'utils/create-async-component',
    'templates/views/components/cards/default.htm'
], function(ko, CardComponentViewModel, createAsyncComponent) {
    return createAsyncComponent(
        'default-card',
        CardComponentViewModel,
        'templates/views/components/cards/default.htm'
    );
});
