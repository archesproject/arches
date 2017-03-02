define(['knockout', 'viewmodels/report', 'views/components/widgets/map'], function (ko, ReportViewModel) {
    return ko.components.register('map-report', {
        viewModel: function(params) {
            params.configKeys = ['zoom', 'centerX', 'centerY', 'geocoder', 'basemap', 'geometryTypes', 'pitch', 'bearing', 'geocodePlaceholder'];

            ReportViewModel.apply(this, [params]);

            // this.configObservable = ko.observable()
        },
        template: { require: 'text!report-templates/map' }
    });
});
