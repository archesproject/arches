define([
    'underscore', 
    'knockout', 
    'knockout-mapping', 
    'viewmodels/map-report', 
    'templates/views/report-templates/map.htm',
], function(_, ko, koMapping, MapReportViewModel, mapReportTemplate) {
    return ko.components.register('map-report', {
        viewModel: MapReportViewModel,
        template: mapReportTemplate
    });
});
