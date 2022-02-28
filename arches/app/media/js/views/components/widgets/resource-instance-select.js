define([
    'knockout',
    'bindings/select2-query'
], function(ko) {
    return ko.components.register('resource-instance-select-widget', {
        viewModel: function(params) {
            const ResourceInstanceSelectViewModel = require('viewmodels/resource-instance-select');
            params.multiple = false;
            params.datatype = 'resource-instance';
            ResourceInstanceSelectViewModel.apply(this, [params]);
        },
        template: {
            require: 'text!widget-templates/resource-instance-select'
        }
    });
});
