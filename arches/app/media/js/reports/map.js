define([
    'underscore', 
    'knockout', 
    'knockout-mapping', 
    'viewmodels/map-report', 
    'utils/create-async-component',
    'reports/map-header',
    '../../../templates/views/report-templates/map.htm'
], function(_, ko, koMapping, MapReportViewModel, createAsyncComponent) {
    return createAsyncComponent(
        'map-report',
        MapReportViewModel,
        '../../../templates/views/report-templates/map.htm'
    );
});
