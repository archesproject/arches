define([
    'jquery',
    'underscore',
    'knockout',
    'mapbox-gl',
    'arches',
    'plugins/mapbox-gl-draw',
    'chosen'
], function ($, _, ko, mapboxgl, arches, Draw, chosen) {
    ko.bindingHandlers.mapboxgl = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext){
            var defaults = {
                container: element
            };
            var options = ko.unwrap(valueAccessor());
            var mapCenter = new mapboxgl.LngLat(viewModel.centerX(), viewModel.centerY());
            var draw = Draw();

            mapboxgl.accessToken = arches.mapboxApiKey;
            options.zoom = viewModel.zoom();
            options.center = mapCenter;

            var map = new mapboxgl.Map(
                _.defaults(options, defaults)
            );

            map.on('load', function() {
                map.addSource('single-point', {
                    "type": "geojson",
                    "data": {
                        "type": "FeatureCollection",
                        "features": []
                    }
                });

                map.addLayer({
                    "id": "point",
                    "source": "single-point",
                    "type": "circle",
                    "paint": {
                        "circle-radius": 5,
                        "circle-color": "red"
                    }
                });
            });

            map.addControl(draw);
            viewModel.basemaps = arches.basemaps;
            viewModel.map = map;
            viewModel.setBasemap = function(basemapType) {
                arches.basemapLayers.forEach(function(layer) {
                    if (layer.name === basemapType.name && !map.getLayer(layer.layer.id)) {
                        map.addLayer(layer.layer, 'gl-draw-active-line.hot')
                    } else if (map.getLayer(layer.layer.id) && layer.name !== basemapType.name) {
                        map.removeLayer(layer.layer.id)
                    }
                }, this)
            };

            viewModel.selectEditingTool = function(val, e) {
              switch (val) {
                case 'Point': draw.changeMode('draw_point'); break;
                case 'Line': draw.changeMode('draw_line_string'); break;
                case 'Polygon': draw.changeMode('draw_polygon'); break;
              }
            }

            viewModel.editingToolIcons = {
              Point: 'ion-location',
              Line: 'ion-steam',
              Polygon: 'ion-star'
            }

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

            $('.geocodewidget').select2({
                ajax: {
                    url: arches.urls.geocoder,
                    dataType: 'json',
                    quietMillis: 250,
                    data: function (term, page) {
                        return {
                            q: term,
                            geocoder: viewModel.geocoder
                        };
                    },
                    results: function (data, page) {
                        return { results: data.results };
                    },
                    cache: true
                },
                minimumInputLength: 4,
                multiple: true,
                maximumSelectionSize: 1
            });

            // $('.geocodwidget input').autocomplete({
            //     source: function( request, response ) {
            //       $.ajax({
            //         url: "/change/name/autocomplete/"+request.term+"/",
            //         dataType: "json",
            //         beforeSend: function(){$('ul.chzn-results').empty();},
            //         success: function( data ) {
            //           response( $.map( data, function( item ) {
            //             $('ul.chzn-results').append('<li class="active-result">' + item.name + '</li>');
            //           }));
            //         }
            //       });
            //     }
            //   });

            $('.geocodewidget').on("select2-selecting", function(e) {
                map.getSource('single-point').setData(e.object.geometry);
                map.flyTo({
                    center: e.object.geometry.coordinates
                });
            });

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

        }
    }

    return ko.bindingHandlers.mapboxgl;
});
