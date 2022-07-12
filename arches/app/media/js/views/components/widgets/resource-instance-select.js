define([
    'knockout',
    'arches',
    'templates/views/components/widgets/resource-instance-select.htm',
    'bindings/select2-query',
], function(ko, arches, resourceInstanceSelectWidgetTemplate) {
    const viewModel = function(params) {
        const ResourceInstanceSelectViewModel = require('viewmodels/resource-instance-select');

        this.translations = arches.translations;
        params.multiple = false;
        params.datatype = 'resource-instance';
        ResourceInstanceSelectViewModel.apply(this, [params]);
    };

    return ko.components.register('resource-instance-select-widget', {
        viewModel: viewModel,
        template: resourceInstanceSelectWidgetTemplate,
    });
});
