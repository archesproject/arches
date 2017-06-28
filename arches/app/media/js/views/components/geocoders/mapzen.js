define(['knockout', 'mapbox-gl', 'arches', 'views/components/geocoders/base-geocoder', 'geocoder-templates'],
function (ko, mapboxgl, arches) {
    return ko.components.register('views/components/geocoders/mapzen', {
        viewModel: function(params) {
            BaseGeocoderViewModel.apply(this, [params]);
            var self = this;
            this.placeholder = params.placeholder || ko.observable('Locate a Place or Address');
            this.anchorLayerId = params.anchorLayerId;
            this.apiKey = params.api_key || arches.mapboxApiKey
            this.map = params.map;

            this.updateResults = function (data) {
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
            }

            this.options.subscribe(function () {
                self.selection(null);
            });

            this.isFocused.subscribe(function () {
                self.focusItem(null);
            });
        },
        template: {
            require: 'text!templates/views/components/geocoders/mapzen.htm'
        }
    });
})
