define([
    'knockout',
    'viewmodels/concept-select',
    'bindings/select2-query'
], function(ko, ConceptSelectViewModel) {
    return ko.components.register('concept-select-widget', {
        viewModel: ConceptSelectViewModel,
        template: {
            require: 'text!widget-templates/concept-select'
        }
    });
});
