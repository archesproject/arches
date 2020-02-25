var test = require('tap').test,
    geojsonCoords = require('../');

test('coordinates', function(t) {
    t.deepEqual(geojsonCoords({
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [125.6, 10.1]
      },
      "properties": {
        "name": "Dinagat Islands"
      }
    }), [[125.6, 10.1]], 'geojson.org example');

    t.deepEqual(geojsonCoords({ "type": "FeatureCollection",
    "features": [
        { "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
            "properties": {"prop0": "value0"}
    },
    { "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]
            ]
        },
        "properties": {
            "prop0": "value0",
            "prop1": 0.0
        }
    },
    { "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
                    [100.0, 1.0], [100.0, 0.0] ]
            ]
        },
        "properties": {
            "prop0": "value0",
            "prop1": {"this": "that"}
        }
    }
    ]
    }), [[102, 0.5],
        [102,0],
        [103,1],
        [104,0],
        [105,1],
        [100,0],
        [101,0],
        [101,1],
        [100,1],
        [100,0]], 'geojson.org example');






        t.deepEqual(geojsonCoords(
             { "type": "GeometryCollection",
    "geometries": [
      { "type": "Point",
        "coordinates": [100.0, 0.0]
        },
      { "type": "LineString",
        "coordinates": [ [101.0, 0.0], [102.0, 1.0] ]
        }
    ]
  }
        ), [
            [100, 0],
            [101, 0],
            [102, 1]], 'geometrycollection');



    t.end();
});
