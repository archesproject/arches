define([
    'knockout',
    'viewmodels/widget',
    'bindings/select2-query'
], function(ko, WidgetViewModel) {
    return ko.components.register('node-value-select', {
        viewModel: function(params) {
            params.configKeys = ['placeholder'];

            WidgetViewModel.apply(this, [params]);
        },
        template: {
            require: 'text!widget-templates/node-value-select'
        }
    });
});
