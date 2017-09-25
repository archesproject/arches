define([
    'knockout',
    'viewmodels/paged-concept-select',
    'bindings/select2-query'
], function(ko, PagedConceptSelectViewModel) {
    return ko.components.register('concept-select-widget', {
        viewModel: PagedConceptSelectViewModel,
        template: {
            require: 'text!widget-templates/paged-concept-select'
        }
    });
});
