define(['knockout', 'turf', 'arches'], function(ko, turf, arches) {
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
