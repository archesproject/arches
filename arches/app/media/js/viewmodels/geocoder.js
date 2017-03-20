define(['knockout', 'mapbox-gl', 'arches'], function(ko, mapboxgl, arches) {
    /**
     * A viewmodel used for a generic geocoder
     *
     * @constructor
     * @name GeocoderViewModel
     *
     */
    var GeocoderViewModel = function(params) {
        var self = this;
        this.provider = params.provider || ko.observable('MapzenGeocoder');
        this.placeholder = params.placeholder || ko.observable('Locate a Place or Address');
        this.anchorLayerId = params.anchorLayerId;
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
        this.queryData = ko.computed(function () {
            return {
                q: self.query(),
                geocoder: self.provider()
            }
        }).extend({
            rateLimit: {
                timeout: 500,
                method: "notifyWhenChangesStop"
            }
        });
        this.queryData.subscribe(function (data) {
            self.options([]);
            if (data.q.length > 3) {
                self.loading(true);
                $.ajax({
                    type: 'GET',
                    url: arches.urls.geocoder,
                    data: data,
                    success: function(res){
                        self.options(res.results);
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
                self.map.removeLayer('geocode-point');
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

        this.setMap = function (map) {
            self.map = map;
        };
    };
    return GeocoderViewModel;
});
