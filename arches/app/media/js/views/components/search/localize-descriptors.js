define([
    'jquery',
    'knockout',
    'templates/views/components/search/localize-descriptors.htm',
], function($, ko, localizeDescriptorsTemplate) {
    const componentName = 'localize-descriptors';
    const viewModel = function(params) {
        this.query = params.query;
        let queryObj = this.query();
        queryObj[componentName] = true;
        this.query(queryObj);
    };

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: localizeDescriptorsTemplate,
    });
});
