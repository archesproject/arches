define(['knockout', 'viewmodels/report'], function (ko, ReportViewModel) {
    return ko.components.register('image-report', {
        viewModel: function(params) {
            params.configKeys = [];

            ReportViewModel.apply(this, [params]);
        },
        template: { require: 'text!report-templates/image' }
    });
});
