import _ from 'underscore';
import ko from 'knockout';
import koMapping from 'knockout-mapping';
import ReportViewModel from 'viewmodels/report';
import 'reports/map-header';


export default function(params) {
    var self = this;
    params.configKeys = ['zoom', 'centerX', 'centerY', 'geocoder', 'basemap', 'geometryTypes', 'pitch', 'bearing', 'geocodePlaceholder'];

    ReportViewModel.apply(this, [params]);

    this.featureCollection = ko.computed({
        read: function() {
            var features = [];
            ko.unwrap(self.tiles).forEach(function(tile) {
                _.each(tile.data, function(val) {
                    if (val?.features) {
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
                if (val?.features) {
                    count += 1;
                }
            }, this);
        }, this);
        return count;
    });
};
