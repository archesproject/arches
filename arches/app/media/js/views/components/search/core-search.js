define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'viewmodels/alert',
    'templates/views/components/search/core-search.htm',
], function($, _, ko, arches, AlertViewModel, coreSearchTemplate) {
    const componentName = 'core-search';
    const viewModel = function(params) {
        const self = this;
        this.query = params.query;
        this.queryString = params.queryString;
        this.updateRequest = params.updateRequest;
        this.searchResults = params.searchResults;
        this.userIsReviewer = params.userIsReviewer;
        this.total = params.total;
        this.userid = params.userid;
        this.hits = params.hits;
        this.alert = params.alert;
        let queryObj = this.query();
        queryObj[componentName] = true;
        this.query(queryObj);
    };

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: coreSearchTemplate,
    });
});
