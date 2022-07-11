define([
    'knockout',
    'arches',
    'viewmodels/concept-select',
    'templates/views/components/widgets/concept-select.htm',
    'bindings/select2-query',
], function(ko, arches, ConceptSelectViewModel, conceptMultiselectTemplate) {
    const viewModel = function(params) {
        params.multiple = true;
        params.configKeys = ['defaultValue'];

        this.translations = arches.translations;
        ConceptSelectViewModel.apply(this, [params]);

        var defaultValue = ko.unwrap(this.defaultValue);
        var self = this;

        if (self.configForm){
            self.select2Config.value = self.defaultValue;
        }
    };

    return ko.components.register('concept-multiselect-widget', {
        viewModel: viewModel,
        template: conceptMultiselectTemplate,
    });
});
