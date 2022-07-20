define(['knockout', 'turf', 'arches', 'underscore'], function(ko, turf, arches, _) {
    return function (searchAggregations) {
        var cellWidth = arches.hexBinSize;
        var units = 'kilometers';
        var hexGrid = turf.hexGrid(arches.hexBinBounds, cellWidth, units);
        _.each(hexGrid.features, function(feature, i) {
            feature.properties.id = i;
        });
        return ko.observable(hexGrid);
    };
});
