define([
    'knockout',
    'viewmodels/concept-select',
    'templates/views/components/widgets/concept-select.htm',
    'bindings/select2-query',
], function(ko, ConceptSelectViewModel, conceptMultiselectTemplate) {
    const viewModel = function(params) {
        params.multiple = true;
        params.configKeys = ['defaultValue'];

         
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
