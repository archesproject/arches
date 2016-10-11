define(['knockout', 'viewmodels/report', 'widgets/geometry'], function (ko, ReportViewModel) {
    return ko.components.register('map-report', {
        viewModel: function(params) {
            params.configKeys = [];

            ReportViewModel.apply(this, [params]);
        },
        template: { require: 'text!report-templates/map' }
    });
});
