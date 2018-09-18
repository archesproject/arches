define([
    'jquery',
    'underscore',
    'knockout',
    'mapbox-gl',
    'arches',
    'bindings/nouislider',
    'bindings/sortable'
], function($, _, ko, mapboxgl, arches) {
    ko.bindingHandlers.mapboxgl = {
        init: function(element, valueAccessor, allBindings, viewModel) {
            var defaults = {
                container: element
            };
            var options = ko.unwrap(valueAccessor()).mapOptions;
            var mapInitOptions = {style: options.style};
            mapboxgl.accessToken = arches.mapboxApiKey;

            _.each(options, function(option, key){
              if (ko.isObservable(option)){
                mapInitOptions[key] = option();
              }
            })

            mapInitOptions['center'] = new mapboxgl.LngLat(mapInitOptions.centerX, mapInitOptions.centerY);

            var map = new mapboxgl.Map(
                _.defaults(mapInitOptions, defaults)
            );
            map.on('load', function() {
                _.each(arches.mapMarkers, function(marker) {
                    map.loadImage(marker.url, function(error, image) {
                        if (error) throw error;
                        map.addImage(marker.name, image);
                    });
                })
            });

            // prevents drag events from bubbling
            $(element).mousedown(function(event) {
                event.stopPropagation();
            });

            if (typeof ko.unwrap(valueAccessor()).afterRender === 'function') {
                ko.unwrap(valueAccessor()).afterRender(map)
            }

            options.zoom.subscribe(function(val) {
                map.setZoom(options.zoom())
            }, this);

            options.centerX.subscribe(function(val) {
                map.setCenter(new mapboxgl.LngLat(options.centerX(), options.centerY()))
            }, this);

            options.centerY.subscribe(function(val) {
                map.setCenter(new mapboxgl.LngLat(options.centerX(), options.centerY()))
            }, this);

            options.pitch.subscribe(function(val) {
                map.setPitch(options.pitch())
            }, this);

            options.bearing.subscribe(function(val) {
                map.setBearing(options.bearing())
            }, this);
        }
    }

    return ko.bindingHandlers.mapboxgl;
});
