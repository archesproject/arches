define([
    'knockout',
    'knockout-mapping',
    'underscore',
    'geojson-extent',
    'views/components/map',
    'views/components/cards/select-feature-layers',
], function(ko, koMapping, _, geojsonExtent, MapComponentViewModel, selectFeatureLayersFactory) {
    ko.components.register('report-header-map', {
        viewModel: function(params) {
            var self = this;
            var featureCollection = ko.computed(function() {
                var features = [];
                ko.unwrap(params.tiles).forEach(function(tile) {
                    _.each(tile.data, function(val) {
                        if ('features' in val) {
                            features = features.concat(koMapping.toJS(val.features));
                        }
                    }, this);
                }, this);
                return {
                    type: 'FeatureCollection',
                    features: features
                };
            });
            
            if (featureCollection().features.length > 0) {
                params.bounds = geojsonExtent(featureCollection());
                params.fitBoundsOptions = { padding: 40 };
            }
            
            params.sources = Object.assign({
                "report-header-map-data": {
                    "type": "geojson",
                    "data": featureCollection()
                }
            }, params.sources);
            params.layers = selectFeatureLayersFactory(
                '',
                'report-header-map-data',
                undefined,
                [],
                true
            );
            MapComponentViewModel.apply(this, [Object.assign({},  params,
                {
                    "activeTab": ko.observable(false),
                    "zoom": null
                }
            )]);
            
            featureCollection.subscribe(function(featureCollection) {
                var map = self.map();
                if (map && map.getStyle()) map.getSource('report-header-map-data')
                    .setData(featureCollection);
            });
        },
        template: { require: 'text!templates/views/components/map.htm' }
    });
});
