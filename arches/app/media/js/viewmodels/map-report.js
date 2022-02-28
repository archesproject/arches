define(['underscore', 'knockout', 'knockout-mapping', 'viewmodels/report', 'reports/map-header'], function(_, ko, koMapping, ReportViewModel) {
    return function(params) {
        var self = this;
        params.configKeys = ['zoom', 'centerX', 'centerY', 'geocoder', 'basemap', 'geometryTypes', 'pitch', 'bearing', 'geocodePlaceholder'];

        ReportViewModel.apply(this, [params]);

        this.featureCollection = ko.computed({
            read: function() {
                var features = [];
                ko.unwrap(self.tiles).forEach(function(tile) {
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
            },
            write: function() {
                return;
            }
        });

        this.featureCount = ko.computed(function() {
            var count = 0;
            ko.unwrap(self.tiles).forEach(function(tile) {
                _.each(tile.data, function(val) {
                    if ('features' in val) {
                        count += 1;
                    }
                }, this);
            }, this);
            return count;
        });
    };
});