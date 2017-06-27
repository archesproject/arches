define(['knockout', 'mapbox-gl', 'arches', 'geocoder-templates'],
function (ko, mapboxgl, arches) {
    return ko.components.register('views/components/geocoders/mapzen', {
        viewModel: function(params) {
            var self = this;
            this.placeholder = params.placeholder || ko.observable('Locate a Place or Address');
            this.anchorLayerId = params.anchorLayerId;
            this.api_key = params.api_key;
            this.map = params.map;
            this.pointstyle = {
                "id": "geocode-point",
                "source": "geocode-point",
                "type": "circle",
                "maxzoom": 20,
                "paint": {
                    "circle-radius": 5,
                    "circle-color": "#FF0000"
                }
            };

            this.selection = ko.observable(null);
            this.focusItem = ko.observable(null);
            this.options = ko.observableArray();
            this.options.subscribe(function () {
                self.selection(null);
            });
            this.loading = ko.observable(false);
            this.isFocused = ko.observable(false).extend({
                throttle: 200
            });
            this.isFocused.subscribe(function () {
                self.focusItem(null);
            });
            this.query = ko.observable();
            console.log(self.api_key, 'key')
            this.query.subscribe(function (data) {
                self.options([]);
                if (data.length > 3) {
                    self.loading(true);
                    $.ajax({
                        type: 'GET',
                        url: 'http://search.mapzen.com/v1/search',
                        data: {
                            api_key: 'mapzen-yxnQbuj',
                            text: self.query()
                        },
                        success: function(res){
                            var results = _.map(res.features, function(feature){
                                return {
                                    'id':feature['id'],
                                    'text':feature['properties']['label'],
                                    'geometry': {
                                        "type": "Point",
                                        "coordinates": [
                                          feature['geometry']['coordinates'][0],
                                          feature['geometry']['coordinates'][1]
                                        ]
                                    }
                            }})
                            self.options(results);
                        },
                        complete: function () {
                            self.loading(false);
                        }
                    });
                }
            });

            this.handleKeys = function (vm, e) {
                var down = 40;
                var up = 38;
                var enter = 13;
                if (e.keyCode === down || e.keyCode === up) {
                    var options = self.options();
                    var focusIndex = options.indexOf(self.focusItem());
                    if (e.keyCode === down) {
                        focusIndex += 1;
                    }
                    if (e.keyCode === up) {
                        focusIndex -= 1;
                        if (focusIndex < -1) {
                            focusIndex = options.length-1;
                        }
                    }
                    if (focusIndex >= 0 && focusIndex < options.length) {
                        self.focusItem(options[focusIndex])
                    } else {
                        self.focusItem(null)
                    }
                    return false;
                }
                if (e.keyCode === enter) {
                    var focusItem = self.focusItem();
                    if (focusItem) {
                        self.selection(focusItem);
                    }
                }
                return true;
            }

            /**
             * Reloads the geocode layer when a new geocode request is made
             * @return {null}
             */
            this.redrawLayer = function() {
                if (self.map) {
                    var cacheLayer = self.map.getLayer('geocode-point');
                    if (cacheLayer) {
                        self.map.removeLayer('geocode-point');
                    }
                    self.map.addLayer(self.pointstyle, self.anchorLayerId);
                }
            };

            this.selection.subscribe(function(item) {
                if (self.map && item) {
                    var coords = item.geometry.coordinates;
                    self.map.getSource('geocode-point').setData(item.geometry);
                    self.redrawLayer();
                    var centerPoint = new mapboxgl.LngLat(coords[0], coords[1])
                    self.map.flyTo({
                        center: centerPoint
                    });
                } else {
                    self.map.removeLayer('geocode-point');
                }
            });
        },
        template: {
            require: 'text!templates/views/components/geocoders/mapzen.htm'
        }
    });
})
