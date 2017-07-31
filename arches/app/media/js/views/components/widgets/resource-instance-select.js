define([
    'knockout',
    'viewmodels/widget'
], function(ko, WidgetViewModel) {
    return ko.components.register('resource-instance-select-widget', {
        viewModel: function(params) {
            params.configKeys = [];
            WidgetViewModel.apply(this, [params]);
        },
        template: {
            require: 'text!widget-templates/resource-instance-select'
        }
    });
});
