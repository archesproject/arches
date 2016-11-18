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

        this.selected = ko.observableArray();

        this.config = ko.computed(function() {
            var geocodeQueryPayload =
                function(term, page) {
                    return {
                        q: term,
                        geocoder: self.provider()
                    };
                }

            return {
                ajax: {
                    url: arches.urls.geocoder,
                    dataType: 'json',
                    quietMillis: 250,
                    data: geocodeQueryPayload,
                    results: function(data, page) {
                        return {
                            results: data.results
                        };
                    },
                    cache: true
                },
                minimumInputLength: 4,
                multiple: false,
                maximumSelectionSize: 1,
                placeholder: self.placeholder()
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

        this.selected.subscribe(function(e) {
            if (self.map) {
                var coords = e.geometry.coordinates;
                self.map.getSource('geocode-point').setData(e.geometry);
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
