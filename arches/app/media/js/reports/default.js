define([
    'knockout', 
    'viewmodels/report', 
    'utils/create-async-component',
    '../../../templates/views/report-templates/default.htm'
], function(ko, ReportViewModel, createAsyncComponent) {
    const viewModel = function(params) {
        params.configKeys = [];
        ReportViewModel.apply(this, [params]);
    };

    return createAsyncComponent(
        'default-report',
        viewModel,
        '../../../templates/views/report-templates/default.htm'
    );
});