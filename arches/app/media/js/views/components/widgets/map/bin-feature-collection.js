import ko from 'knockout';
import { hexGrid as turfHexGrid } from 'turf';
import arches from 'arches';
import _ from 'underscore';


export default function(searchAggregations) {
    var cellWidth = arches.hexBinSize;
    var units = 'kilometers';
    var hexGrid = turfHexGrid(arches.hexBinBounds, cellWidth, units);
    _.each(hexGrid.features, function(feature, i) {
        feature.properties.id = i;
    });
    return ko.observable(hexGrid);
};
