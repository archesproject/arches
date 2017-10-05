define([
    'knockout',
    'viewmodels/concept-select',
    'bindings/select2-query'
], function(ko, ConceptSelectViewModel) {
    return ko.components.register('concept-multiselect-widget', {
        viewModel: function(params) {
            params.multiple = true;
            ConceptSelectViewModel.apply(this, [params]);
        },
        template: {
            require: 'text!widget-templates/concept-select'
        }
    });
});
