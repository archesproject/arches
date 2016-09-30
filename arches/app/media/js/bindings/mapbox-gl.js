define([
    'jquery',
    'underscore',
    'knockout',
    'mapbox-gl',
    'arches',
    'plugins/mapbox-gl-draw',
    'map/mapbox-style',
    'bindings/nouislider',
    'bindings/sortable'
], function($, _, ko, mapboxgl, arches, Draw, mapStyle) {
    ko.bindingHandlers.mapboxgl = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
            var defaults = {
                container: element
            };
            var options = ko.unwrap(valueAccessor()).mapOptions;
            var mapCenter = new mapboxgl.LngLat(viewModel.centerX(), viewModel.centerY());
            var draw = Draw();

            mapboxgl.accessToken = arches.mapboxApiKey;
            options.zoom = viewModel.zoom();
            options.center = mapCenter;
            options.pitch = viewModel.pitch();
            options.bearing = viewModel.bearing();

            var map = new mapboxgl.Map(
                _.defaults(options, defaults)
            );

            viewModel.map = map;
            map.addControl(draw);

            viewModel.basemaps = _.filter(arches.mapLayers, function(baselayer) {
                return baselayer.isoverlay === false
            });
            viewModel.setBasemap = function(basemapType) {
                var lowestOverlay = _.last(_.last(overlays).layer_definitions);
                this.basemaps.forEach(function(basemap) {
                    if (basemap.name === basemapType.name) {
                        basemap.layer_definitions.forEach(function(layer) {
                            viewModel.map.addLayer(layer, lowestOverlay.id)
                        })
                    } else {
                        basemap.layer_definitions.forEach(function(layer) {
                            if (viewModel.map.getLayer(layer.id) !== undefined) {
                                viewModel.map.removeLayer(layer.id);
                            }
                        })
                    }
                }, this)
            };

            viewModel.selectEditingTool = function(val, e) {
                switch (val) {
                    case 'Point':
                        draw.changeMode('draw_point');
                        break;
                    case 'Line':
                        draw.changeMode('draw_line_string');
                        break;
                    case 'Polygon':
                        draw.changeMode('draw_polygon');
                        break;
                    default:
                        draw.trash();
                }
            }

            viewModel.overlays.subscribe(function(overlays) {
                var anchorLayer = 'gl-draw-active-line.hot';
                for (var i = overlays.length; i-- > 0;) { //Using a conventional loop because we want to go backwards over the array without creating a copy
                    overlays[i].layer_definitions.forEach(function(layer) {
                        map.removeLayer(layer.id)
                    })
                }
                for (var i = overlays.length; i-- > 0;) {
                    overlays[i].layer_definitions.forEach(function(layer) {
                        map.addLayer(layer, anchorLayer);
                        map.setPaintProperty(layer.id, layer.type + '-opacity', overlays[i].opacity() / 100.0);
                    })
                }
                viewModel.redrawGeocodeLayer();
            })

            viewModel.editingToolIcons = {
                Point: 'ion-location',
                Line: 'ion-steam',
                Polygon: 'fa fa-pencil-square-o',
                Delete: 'ion-trash-a'
            }

            viewModel.redrawGeocodeLayer = function() {
                var cacheLayer = map.getLayer('geocode-point');
                map.removeLayer('geocode-point');
                map.addLayer(cacheLayer, 'gl-draw-active-line.hot');
            }

            $('.geocodewidget').select2({
                ajax: {
                    url: arches.urls.geocoder,
                    dataType: 'json',
                    quietMillis: 250,
                    data: function(term, page) {
                        return {
                            q: term,
                            geocoder: viewModel.geocoder
                        };
                    },
                    results: function(data, page) {
                        return {
                            results: data.results
                        };
                    },
                    cache: true
                },
                minimumInputLength: 4,
                multiple: false,
                maximumSelectionSize: 1
            });

            $('.geocodewidget').on("select2-selecting", function(e) {
                map.getSource('geocode-point').setData(e.object.geometry);
                viewModel.redrawGeocodeLayer();
                map.flyTo({
                    center: e.object.geometry.coordinates
                });
            });

            viewModel.map.on('moveend', function(e) {
                var mapCenter = viewModel.map.getCenter()
                var zoom = viewModel.map.getZoom()
                if (viewModel.zoom() !== zoom) {
                    viewModel.zoom(zoom);
                };
                viewModel.centerX(mapCenter.lng)
                viewModel.centerY(mapCenter.lat)
            })

            viewModel.zoom.subscribe(function(val) {
                viewModel.map.setZoom(viewModel.zoom())
            })

            viewModel.centerX.subscribe(function(val) {
                viewModel.map.setCenter(new mapboxgl.LngLat(viewModel.centerX(), viewModel.centerY()))
            })

            viewModel.centerY.subscribe(function(val) {
                viewModel.map.setCenter(new mapboxgl.LngLat(viewModel.centerX(), viewModel.centerY()))
            })

            viewModel.pitch.subscribe(function(val) {
                viewModel.map.setPitch(viewModel.pitch())
            })

            viewModel.bearing.subscribe(function(val) {
                viewModel.map.setBearing(viewModel.bearing())
            })

            // prevents drag events from bubbling
            $(element).mousedown(function(event) {
                event.stopPropagation();
            });

            if (typeof ko.unwrap(valueAccessor()).afterRender === 'function') {
                ko.unwrap(valueAccessor()).afterRender(map)
            }
        }
    }

    return ko.bindingHandlers.mapboxgl;
});
