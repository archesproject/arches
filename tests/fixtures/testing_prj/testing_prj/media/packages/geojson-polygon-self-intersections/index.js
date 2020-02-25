// Find self-intersections in geojson polygon (possibly with interior rings)
var rbush = require('rbush');


var merge = function(){
  var output = {};
  Array.prototype.slice.call(arguments).forEach(function(arg){
    if(arg){
      Object.keys(arg).forEach(function(key){
        output[key]=arg[key];
      });
    }
  });
  return output;
};
var defaults = {
  useSpatialIndex: true,
  epsilon: 0,
  reportVertexOnVertex: false,
  reportVertexOnEdge: false
};

module.exports = function(feature, filterFn, options0) {
  var options;
  if("object" === typeof options0){
    options = merge(defaults,options0);
  } else {
    options = merge(defaults,{useSpatialIndex:options0});
  }

  if (feature.geometry.type != "Polygon") throw new Error("The input feature must be a Polygon");

  var coord = feature.geometry.coordinates;

  var output = [];
  var seen = {};

  if (options.useSpatialIndex) {
    var allEdgesAsRbushTreeItems = [];
    for (var ring0 = 0; ring0 < coord.length; ring0++) {
      for (var edge0 = 0; edge0 < coord[ring0].length-1; edge0++) {
        allEdgesAsRbushTreeItems.push(rbushTreeItem(ring0, edge0))
      }
    }
    var tree = rbush();
    tree.load(allEdgesAsRbushTreeItems);
  }

  for (var ring0 = 0; ring0 < coord.length; ring0++) {
    for (var edge0 = 0; edge0 < coord[ring0].length-1; edge0++) {
      if (options.useSpatialIndex) {
        var bboxOverlaps = tree.search(rbushTreeItem(ring0, edge0));
        bboxOverlaps.forEach(function(bboxIsect) {
          var ring1 = bboxIsect.ring;
          var edge1 = bboxIsect.edge;
          ifIsectAddToOutput(ring0, edge0, ring1, edge1);
        });
      }
      else {
        for (var ring1 = 0; ring1 < coord.length; ring1++) {
          for (var edge1 = 0 ; edge1 < coord[ring1].length-1; edge1++) {
            // TODO: speedup possible if only interested in unique: start last two loops at ring0 and edge0+1
            ifIsectAddToOutput(ring0, edge0, ring1, edge1);
          }
        }
      }
    }
  }

  if (!filterFn) output = {type: "Feature", geometry: {type: "MultiPoint", coordinates: output}};
  return output;

  // true if frac is (almost) 1.0 or 0.0
  function isBoundaryCase(frac){
    var e2 = options.epsilon * options.epsilon;
    return e2 >= (frac-1)*(frac-1) || e2 >= frac*frac;
  }
  function isOutside(frac){
    return frac < 0 - options.epsilon || frac > 1 + options.epsilon;
  }
  // Function to check if two edges intersect and add the intersection to the output
  function ifIsectAddToOutput(ring0, edge0, ring1, edge1) {
    var start0 = coord[ring0][edge0];
    var end0 = coord[ring0][edge0+1];
    var start1 = coord[ring1][edge1];
    var end1 = coord[ring1][edge1+1];

    var isect = intersect(start0, end0, start1, end1);

    if (isect == null) return; // discard parallels and coincidence
    frac0, frac1;
    if (end0[0] != start0[0]) {
      var frac0 = (isect[0]-start0[0])/(end0[0]-start0[0]);
    } else {
      var frac0 = (isect[1]-start0[1])/(end0[1]-start0[1]);
    };
    if (end1[0] != start1[0]) {
      var frac1 = (isect[0]-start1[0])/(end1[0]-start1[0]);
    } else {
      var frac1 = (isect[1]-start1[1])/(end1[1]-start1[1]);
    };

    // There are roughly three cases we need to deal with.
    // 1. If at least one of the fracs lies outside [0,1], there is no intersection.
    if (isOutside(frac0) || isOutside(frac1)) {
      return; // require segment intersection
    }

    // 2. If both are either exactly 0 or exactly 1, this is not an intersection but just
    // two edge segments sharing a common vertex.
    if (isBoundaryCase(frac0) && isBoundaryCase(frac1)){
      if(! options.reportVertexOnVertex) return;
    }

    // 3. If only one of the fractions is exactly 0 or 1, this is
    // a vertex-on-edge situation.
    if (isBoundaryCase(frac0) || isBoundaryCase(frac1)){
      if(! options.reportVertexOnEdge) return;
    }

    var key = isect;
    var unique = !seen[key];
    if (unique) {
      seen[key] = true;
    }

    if (filterFn) {
      output.push(filterFn(isect, ring0, edge0, start0, end0, frac0, ring1, edge1, start1, end1, frac1, unique));
    } else {
      output.push(isect);
    }
  }

  // Function to return a rbush tree item given an ring and edge number
  function rbushTreeItem(ring, edge) {

    var start = coord[ring][edge];
    var end = coord[ring][edge+1];

    if (start[0] < end[0]) {
      var minX = start[0], maxX = end[0];
    } else {
      var minX = end[0], maxX = start[0];
    };
    if (start[1] < end[1]) {
      var minY = start[1], maxY = end[1];
    } else {
      var minY = end[1], maxY = start[1];
    }
    return {minX: minX, minY: minY, maxX: maxX, maxY: maxY, ring: ring, edge: edge};
  }

}

// Function to compute where two lines (not segments) intersect. From https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
function intersect(start0, end0, start1, end1) {
  if (equalArrays(start0,start1) || equalArrays(start0,end1) || equalArrays(end0,start1) || equalArrays(end1,start1)) return null;
  var x0 = start0[0],
      y0 = start0[1],
      x1 = end0[0],
      y1 = end0[1],
      x2 = start1[0],
      y2 = start1[1],
      x3 = end1[0],
      y3 = end1[1];
  var denom = (x0 - x1) * (y2 - y3) - (y0 - y1) * (x2 - x3);
  if (denom == 0) return null;
  var x4 = ((x0 * y1 - y0 * x1) * (x2 - x3) - (x0 - x1) * (x2 * y3 - y2 * x3)) / denom;
  var y4 = ((x0 * y1 - y0 * x1) * (y2 - y3) - (y0 - y1) * (x2 * y3 - y2 * x3)) / denom;
  return [x4, y4];
}

// Function to compare Arrays of numbers. From http://stackoverflow.com/questions/7837456/how-to-compare-arrays-in-javascript
function equalArrays(array1, array2) {
  // if the other array is a falsy value, return
  if (!array1 || !array2)
      return false;

  // compare lengths - can save a lot of time
  if (array1.length != array2.length)
      return false;

  for (var i = 0, l=array1.length; i < l; i++) {
      // Check if we have nested arrays
      if (array1[i] instanceof Array && array2[i] instanceof Array) {
          // recurse into the nested arrays
          if (!equalArrays(array1[i],array2[i]))
              return false;
      }
      else if (array1[i] != array2[i]) {
          // Warning - two different object instances will never be equal: {x:20} != {x:20}
          return false;
      }
  }
  return true;
}
