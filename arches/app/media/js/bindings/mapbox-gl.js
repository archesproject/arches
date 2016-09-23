define([
    'jquery',
    'underscore',
    'knockout',
    'mapbox-gl',
    'arches',
    'plugins/mapbox-gl-draw',
    'bindings/chosen'
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

            // viewModel.geocodeQueryVal = ko.observable();
            // viewModel.geocodeSearchVal = ko.observable('')
            // viewModel.geocodeSearchResults = ko.observable({})

            // var $element = $(element);

            // $element.on('chosen:showing_dropdown', function() {
            //       $('.chosen-search input').on('keyup', function() {
            //         viewModel.geocodeQueryVal(this.value)
            //         // viewModel.geocodeSearchVal(this.value)
            //       });
            //     });
            //
            // viewModel.geocodeQueryVal.subscribe(function (val) {
            //     var opts = _.pluck(viewModel.geocodeSearchResults(), 'text');
            //     if (_.contains(opts, val) === false) {
            //       viewModel.updateGeoSearchOptions(val)
            //     } else {
            //       console.log(val, 'geocodeme!')
            //     }
            //   })
            //
            // viewModel.updateGeoSearchOptions = function(val){
            //     var term = val === undefined ? "" : val;
            //     $.ajax({
            //       url: arches.urls.geocoder,
            //       dataType: "json",
            //       data: {
            //           q: term,
            //           geocoder: viewModel.geocoder
            //       }
            //     })
            //     .done(
            //       function(data){
            //         viewModel.geocodeSearchResults(data.results);
            //       }
            //     )
            //     .fail(function(e){console.log(e, 'failed')})
            //     .always(function(e){console.log(e, 'all done')});
            //   }

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
                  multiple: false,
                  maximumSelectionSize: 1
              });


            $('.geocode-container').autocomplete({
                source: function( request, response ) {
                  $.ajax({
                    url: arches.urls.geocoder,
                    dataType: "json",
                    quietMillis: 250,
                    data: {
                        q: request.term,
                        geocoder: viewModel.geocoder
                    },
                    beforeSend: function(){$('ul.chzn-results').empty();}
                  })
                  .done(
                    function(data){
                      console.log(data)
                      var opts = _.pluck(data.results, 'text');
                      console.log(opts)
                      viewModel.geocodeSearchResults(opts);
                      // var result = '';
                      // _.each( data.results, function(item) {
                      //     result += '<option value="' + item.geometry.coordinates + '">' + item.text + '</option>';
                      // });
                    }
                  )
                  .fail(function(e){console.log(e, 'failed')})
                  .always(function(e){console.log(e, 'all done')});
                }
              });

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
