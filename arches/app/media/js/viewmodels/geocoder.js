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
        this.geocodeProvider = params.geocodeProvider || ko.observable('MapzenGeocoder');
        this.geocodePlaceholder = params.geocodePlaceholder || ko.observable('Search');
        this.geocoderVisible = params.geocoderVisible || ko.observable(true);
        this.pointstyle = {
            "id": "geocode-point",
            "source": "geocode-point",
            "type": "circle",
            "paint": {
                "circle-radius": 5,
                "circle-color": "red"
            }
        }

        this.selected = ko.observableArray()

        this.setupGeocoder = function() {
            var geocodeQueryPayload =
                function(term, page) {
                    return {
                        q: term,
                        geocoder: self.geocodeProvider()
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
                placeholder: self.geocodePlaceholder()
            }
        };

        this.geocoderOptions = ko.observableArray([{ //This should be a system config rather than hard-coded here
            'id': 'BingGeocoder',
            'name': 'Bing'
        }, {
            'id': 'MapzenGeocoder',
            'name': 'Mapzen'
        }]);

        /**
         * Reloads the geocode layer when a new geocode request is made
         * @return {null}
         */
        this.redrawLayer = function(map, anchorLayerId) {
            var cacheLayer = map.getLayer('geocode-point');
            map.removeLayer('geocode-point');
            map.addLayer(cacheLayer, anchorLayerId);
        }

        this.goToSelected = function(e) {
            var coords = e.geometry.coordinates;
            this.map.getSource('geocode-point').setData(e.geometry);
            self.redrawLayer(this.map, this.anchorLayerId);
            var centerPoint = new mapboxgl.LngLat(coords[0], coords[1])
            this.map.flyTo({
                center: centerPoint
            });
        }

        /**
         * toggles the visibility of the geocoder input in the map widget
         * @return {null}
         */
        this.toggleGeocoder = function() {
            if (self.geocoderVisible() === true) {
                self.geocoderVisible(false)
            } else {
                self.geocoderVisible(true)
            }
        }

    };
    return GeocoderViewModel;
});
