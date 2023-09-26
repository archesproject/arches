define([
    'knockout',
    'viewmodels/concept-select',
    'templates/views/components/widgets/concept-select.htm',
    'bindings/select2-query',
], function(ko, ConceptSelectViewModel, conceptSelectTemplate) {
    const viewModel = function(params) {
        params.configKeys = ['defaultValue'];
        ConceptSelectViewModel.apply(this, [params]);

        var defaultValue = ko.unwrap(this.defaultValue);
        var self = this;

        if (self.configForm){
            self.select2Config.value = self.defaultValue;
        }
    };

    return ko.components.register('concept-select-widget', {
        viewModel: viewModel,
        template: conceptSelectTemplate,
    });
});
