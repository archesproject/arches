define([
    'knockout',
    'viewmodels/concept-select',
    'utils/create-async-component',
    'bindings/select2-query',
], function(ko, ConceptSelectViewModel, createAsyncComponent) {
    const viewModel = function(params) {
        params.configKeys = ['defaultValue'];
        ConceptSelectViewModel.apply(this, [params]);

        var defaultValue = ko.unwrap(this.defaultValue)
        var self = this;

        if (self.configForm){
            self.select2Config.value = self.defaultValue
        };
    };

    return createAsyncComponent(
        'concept-select-widget',
        viewModel,
        'templates/views/components/widgets/concept-select.htm'
    );
});
