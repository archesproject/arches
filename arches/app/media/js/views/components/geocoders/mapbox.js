define(['knockout', 'mapbox-gl', 'arches','views/components/geocoders/base-geocoder','geocoder-templates'],
function (ko, mapboxgl, arches, BaseGeocoderViewModel) {
    return ko.components.register('views/components/geocoders/mapbox', {
        viewModel: function(params) {
            BaseGeocoderViewModel.apply(this, [params]);
            var self = this;
            this.placeholder = params.placeholder || ko.observable('Locate a Place or Address');
            this.anchorLayerId = params.anchorLayerId;
            this.apiKey = params.api_key || arches.mapboxApiKey
            this.map = params.map;

            this.options.subscribe(function () {
                self.selection(null);
            });

            this.isFocused.subscribe(function () {
                self.focusItem(null);
            });
        },
        template: {
            require: 'text!templates/views/components/geocoders/mapbox.htm'
        }
    });
})
