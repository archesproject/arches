var test = require('tape'),
    geojsonRandom = require('./');

test('random.position()', function(t) {
    var nobbox = geojsonRandom.position();
    t.equal(nobbox.length, 2);
    t.ok(nobbox[0] > -180 && nobbox[0] < 180, 'lon');
    t.ok(nobbox[1] > -90 && nobbox[1] < 90, 'lat');
    t.end();
});

test('random.position(bbox)', function(t) {
    var withBbox = geojsonRandom.position([0, 0, 10, 10]);
    t.equal(withBbox.length, 2);
    t.ok(withBbox[0] >= 0 && withBbox[0] <= 10, 'lon');
    t.ok(withBbox[1] >= 0 && withBbox[1] <= 10, 'lat');
    t.end();
});

test('random.point()', function(t) {
    var randomPoints = geojsonRandom.point(100);
    t.equal(randomPoints.features.length, 100, '100 points');
    t.equal(randomPoints.features[0].geometry.type, 'Point', 'features are points');
    t.end();
});

test('random.point(bbox)', function(t) {
    var randomPoints = geojsonRandom.point(1, [50, 50, 60, 60]);
    t.equal(randomPoints.features.length, 1, '1 points');
    var withBbox = randomPoints.features[0].geometry.coordinates;
    t.ok(withBbox[0] >= 50 && withBbox[0] <= 60, 'lon');
    t.ok(withBbox[1] >= 50 && withBbox[1] <= 60, 'lat');
    t.end();
});

test('random.point(bbox zero width)', function(t) {
    var randomPoints = geojsonRandom.point(1, [50, 50, 50, 60]);
    t.equal(randomPoints.features.length, 1, '1 points');
    var withBbox = randomPoints.features[0].geometry.coordinates;
    t.equal(withBbox[0], 50, 'lon');
    t.end();
});

test('random.polygon', function(t) {
    var randomPolygons = geojsonRandom.polygon(100);
    t.equal(randomPolygons.features.length, 100, '100 polygons');
    t.equal(randomPolygons.features[0].geometry.type, 'Polygon', 'features are polygons');
    t.equal(randomPolygons.features[0].geometry.coordinates[0].length, 11, 'and have 11 positions in their outer rings');

    var randomPolygonsHi = geojsonRandom.polygon(100, 20);
    t.equal(randomPolygonsHi.features[0].geometry.coordinates[0].length, 21, 'and have 21 positions in their outer rings');
    t.end();
});

test('random.polygon with bbox', function(t) {
    var randomPolygonRing = geojsonRandom.polygon(1, 5, 5, [50, 50, 60, 60]).features[0].geometry.coordinates[0];

    randomPolygonRing.forEach(function(withBbox) {
        t.ok(withBbox[0] >= 40 && withBbox[0] <= 70, 'lon');
        t.ok(withBbox[1] >= 40 && withBbox[1] <= 70, 'lat');
    });

    t.end();
});

