define([
    'jquery',
    'underscore',
    'knockout',
    'mapbox-gl',
    'arches',
    'plugins/mapbox-gl-draw'
], function ($, _, ko, mapboxgl, arches, Draw) {
    ko.bindingHandlers.mapboxgl = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext){
            var defaults = {
                container: element
            };
            var options = ko.unwrap(valueAccessor());
            var mapCenter = new mapboxgl.LngLat(viewModel.centerX(), viewModel.centerY());

            mapboxgl.accessToken = arches.mapboxApiKey;
            options.zoom = viewModel.zoom();
            options.center = mapCenter;

            var map = new mapboxgl.Map(
                _.defaults(options, defaults)
            );
            viewModel.basemaps = arches.basemaps;
            viewModel.map = map;
            viewModel.setBasemap = function(basemapType) {
                arches.basemapLayers.forEach(function(layer) {
                    if (layer.name === basemapType.name && !map.getLayer(layer.layer.id)) {
                        map.addLayer(layer.layer)
                    } else if (map.getLayer(layer.layer.id) && layer.name !== basemapType.name) {
                        map.removeLayer(layer.layer.id)
                    }
                }, this)
            };


            //TODO I wanted to make the map events update the configurations, but it made the map animations too rough
            // viewModel.map.on('zoomend', function(e){
            //   viewModel.zoom(viewModel.map.getZoom());
            // })
            //
            // viewModel.map.on('zoomend', function(e){
            // var mapCenter = viewModel.map.getCenter()
            // var eventCenter = e.lngLat;
            // if (eventCenter !== mapCenter) {
            //   viewModel.centerX(eventCenter.lng)
            //   viewModel.centerY(eventCenter.lat)
            //   }
            // })

            viewModel.updateMapProperties = function(property) {
              this.map.setCenter(new mapboxgl.LngLat(viewModel.centerX(), viewModel.centerY()))
              this.map.zoomTo(viewModel.zoom())
            }

            viewModel.zoom.subscribe(function (val) {
                viewModel.updateMapProperties()
              })

            viewModel.centerX.subscribe(function (val) {
              viewModel.updateMapProperties()
              })

            viewModel.centerY.subscribe(function (val) {
              viewModel.updateMapProperties()
              })

            var draw = Draw();
            map.addControl(draw);
        }
    }

    return ko.bindingHandlers.mapboxgl;
});
