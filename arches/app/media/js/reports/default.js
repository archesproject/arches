define(['knockout', 'viewmodels/report'], function(ko, ReportViewModel) {
    return ko.components.register('default-report', {
        viewModel: function(params) {
            params.configKeys = [];

            console.log("default report VM", self, params)
            ReportViewModel.apply(this, [params]);
        },
        template: { require: 'text!report-templates/default' }
    });
});
