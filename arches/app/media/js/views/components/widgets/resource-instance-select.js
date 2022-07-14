define([
    'knockout',
    'templates/views/components/widgets/resource-instance-select.htm',
    'bindings/select2-query',
], function(ko, resourceInstanceSelectWidgetTemplate) {
    const viewModel = function(params) {
        const ResourceInstanceSelectViewModel = require('viewmodels/resource-instance-select');

         
        params.multiple = false;
        params.datatype = 'resource-instance';
        ResourceInstanceSelectViewModel.apply(this, [params]);
    };

    return ko.components.register('resource-instance-select-widget', {
        viewModel: viewModel,
        template: resourceInstanceSelectWidgetTemplate,
    });
});
