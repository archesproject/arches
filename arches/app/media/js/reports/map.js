import _ from 'underscore';
import ko from 'knockout';
import koMapping from 'knockout-mapping';
import MapReportViewModel from 'viewmodels/map-report';
import mapReportTemplate from 'templates/views/report-templates/map.htm';


export default ko.components.register('map-report', {
    viewModel: MapReportViewModel,
    template: mapReportTemplate
});
