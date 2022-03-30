define(['knockout', 'viewmodels/report'], function(ko, ReportViewModel) {
    return ko.components.register('default-report', {
        viewModel: function(params) {
            params.configKeys = [];

            ReportViewModel.apply(this, [params]);
        },
        template: window['default-report-template']
    });
});
