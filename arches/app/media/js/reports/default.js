define([
    'knockout', 
    'arches',
    'viewmodels/report', 
    'templates/views/report-templates/default.htm',
], function(ko, arches, ReportViewModel, defaultTemplate) {
    const viewModel = function(params) {
        params.configKeys = [];
        this.translations = arches.translations;
        
        ReportViewModel.apply(this, [params]);
    };

    return ko.components.register('default-report', {
        viewModel: viewModel,
        template: defaultTemplate
    });
});