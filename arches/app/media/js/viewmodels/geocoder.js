define(['knockout', 'mapbox-gl', 'arches'], function(ko, mapboxgl, arches) {
    /**
     * A viewmodel used for a generic geocoder
     *
     * @constructor
     * @name GeocoderViewModel
     *
     */
    var GeocoderViewModel = function(params) {
        /**
         * TODO:
         *      - add concept of focused row
         *      - add styles for selected + focused rows
         *      - add listener to up/down arrow keys to focus rows, enter to select
         *      - add "x" button to clear options and selection
         */
        var self = this;
        this.provider = params.provider || ko.observable('MapzenGeocoder');
        this.placeholder = params.placeholder || ko.observable('Search');
        this.anchorLayerId = params.anchorLayerId;
        this.map = params.map;
        this.pointstyle = {
            "id": "geocode-point",
            "source": "geocode-point",
            "type": "circle",
            "paint": {
                "circle-radius": 5,
                "circle-color": "red"
            }
        };

        this.selection = ko.observable();
        this.options = ko.observableArray();
        this.loading = ko.observable(false);
        this.query = ko.observable();
        this.query.extend({ rateLimit: { timeout: 500, method: "notifyWhenChangesStop" } });
        this.query.subscribe(function (query) {
            self.options([]);
            if (query.length > 3) {
                self.loading(true);
                $.ajax({
                    type: 'GET',
                    url: arches.urls.geocoder,
                    data: {
                        q: query,
                        geocoder: self.provider()
                    },
                    success: function(res){
                        self.options(res.results);
                    },
                    complete: function () {
                        self.loading(false);
                    }
                });
            }
        });

        /**
         * Reloads the geocode layer when a new geocode request is made
         * @return {null}
         */
        this.redrawLayer = function() {
            if (self.map) {
                var cacheLayer = self.map.getLayer('geocode-point');
                self.map.removeLayer('geocode-point');
                self.map.addLayer(cacheLayer, self.anchorLayerId);
            }
        };

        this.selection.subscribe(function(item) {
            if (self.map) {
                var coords = item.geometry.coordinates;
                self.map.getSource('geocode-point').setData(item.geometry);
                self.redrawLayer();
                var centerPoint = new mapboxgl.LngLat(coords[0], coords[1])
                self.map.flyTo({
                    center: centerPoint
                });
            }
        });

        this.setMap = function (map) {
            self.map = map;
        };
    };
    return GeocoderViewModel;
});
