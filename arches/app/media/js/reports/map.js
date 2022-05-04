define([
    'underscore', 
    'knockout', 
    'knockout-mapping', 
    'viewmodels/map-report', 
    'utils/create-async-component',
    'reports/map-header',
], function(_, ko, koMapping, MapReportViewModel, createAsyncComponent) {
    return createAsyncComponent(
        'map-report',
        MapReportViewModel,
        'templates/views/report-templates/map.htm'
    );
});
