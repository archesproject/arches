define([
    'jquery',
    'knockout',
    'templates/views/components/search/core-search.htm',
], function($, ko, coreSearchTemplate) {
    const componentName = 'core-search';
    const viewModel = function(params) {
        this.query = params.query;
        let queryObj = this.query();
        queryObj[componentName] = true;
        this.query(queryObj);
    };

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: coreSearchTemplate,
    });
});
