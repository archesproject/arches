define([
    'jquery',
    'knockout',
], function($, ko) {
    const componentName = 'localize-descriptors';
    const viewModel = function(params) {
        this.query = params.query;
        let queryObj = this.query();
        queryObj[componentName] = true;
        this.query(queryObj);
    };

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: '<div style="display:none;"></div>',
    });
});