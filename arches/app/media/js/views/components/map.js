import _ from 'underscore';
import ko from 'knockout';
import MapViewModel from 'viewmodels/map';
import mapTemplate from 'templates/views/components/map.htm';
import 'bindings/mapbox-gl';
import 'bindings/sortable';

ko.components.register('arches-map', {
    viewModel: MapViewModel,
    template: mapTemplate,
});

export default MapViewModel;
