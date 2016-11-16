define(['knockout', 'mapbox-gl', 'arches'], function(ko, mapboxgl, arches) {
    /**
     * A viewmodel used for a generic geocoder
     *
     * @constructor
     * @name GeocoderViewModel
     *
     */
    var GeocoderViewModel = function() {
        var self = this;
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

        this.setupGeocoder = function(vm) {
            var geocodeQueryPayload =
                function(term, page) {
                    return {
                        q: term,
                        geocoder: vm.geocoder()
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
                placeholder: vm.geocodePlaceholder()
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
         * @param  {object} vm the view model with the config to be updated
         * @return {null}
         */
        this.toggleGeocoder = function(vm) {
            if (vm.geocoderVisible() === true) {
                vm.geocoderVisible(false)
            } else {
                vm.geocoderVisible(true)
            }
        }

    };
    return GeocoderViewModel;
});
