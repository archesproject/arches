define(
    ['knockout', 'arches','views/components/geocoders/base-geocoder','geocoder-templates'],
    function (ko, arches, BaseGeocoderViewModel) {
        return ko.components.register('views/components/geocoders/mapbox', {
            viewModel: function(params) {
                BaseGeocoderViewModel.apply(this, [params]);
                var self = this;
                this.placeholder = params.placeholder || ko.observable('Locate a Place or Address');
                this.anchorLayerId = params.anchorLayerId;
                this.apiKey = params.api_key() || arches.mapboxApiKey
                this.map = params.map;

                this.options.subscribe(function () {
                    self.selection(null);
                });

                this.updateResults = function(data) {
                        self.options([]);
                        if (data.length > 3) {
                            self.loading(true);
                            $.ajax({
                                type: 'GET',
                                url: '//api.mapbox.com/geocoding/v5/mapbox.places/'+ self.query() + '.json',
                                data: {
                                    access_token: ko.unwrap(self.apiKey)
                                },
                                success: function(res){
                                    var results = _.map(res.features, function(feature){
                                        return {
                                            'id':feature['id'],
                                            'text':feature['place_name'],
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
                    };

                this.query.subscribe(this.updateResults);

                this.isFocused.subscribe(function () {
                    self.focusItem(null);
                });
            },
            template: {
                require: 'text!templates/views/components/geocoders/geocoder.htm'
            }
        });
    å}
)
