var test = require('tap').test,
    Extent = require('../');

test('extent', function(t) {
    t.equal(Extent().bbox(), null, 'null');
    t.deepEqual(Extent()
        .include([0, 0]).bbox(),
            [0, 0, 0, 0], 'one point');
    t.deepEqual(Extent()
        .include([0, 0])
        .include([10, 10])
        .bbox(),
            [0, 0, 10, 10], 'two points');
    t.deepEqual(Extent()
        .include([0, 0])
        .include([10, 10])
        .include([-10, -10])
        .bbox(),
            [-10, -10, 10, 10], 'three points');
    t.deepEqual(Extent()
        .contains([0, 0]),
        null, 'contains - invalid');
    t.deepEqual(Extent()
        .include([0, 0])
        .contains([0, 0]),
        true, 'contains - true, zero size');
    t.deepEqual(Extent()
        .include([0, 0])
        .contains([0, 10]),
        false, 'contains - false, zero size');
    t.deepEqual(Extent()
        .include([0, 0])
        .include([10, 10])
        .contains([0, 10]),
        true, 'contains - true, has size');
    t.deepEqual(Extent()
        .include([0, 0])
        .include([10, 10])
        .contains()([5, 5]),
        true, 'fast contains - true, has size');
    t.deepEqual(Extent()
        .include([0, 0])
        .include([10, 10])
        .contains([15, 15]),
        false, 'contains - false, has size');
    t.deepEqual(Extent()
        .include([0, 0])
        .include([10, 10])
        .contains([15, 15]),
        false, 'contains - false, has size');
    t.deepEqual(Extent()
        .include([0, 0])
        .include([10, 10])
        .contains()([15, 15]),
        false, 'fast contains - false, has size');
    t.deepEqual(Extent()
        .include([0, 0])
        .include([10, 10])
        .include([-10, -10])
        .polygon(), {
            type: 'Polygon',
            coordinates: [[[-10,-10],[10,-10],[10,10],[-10,10],[-10,-10]]]
        }, 'polygon');
    t.equal(Extent().contains()([0, 0]), null, 'fast contains - invalid');
    t.equal(Extent().polygon(), null, 'polygon - invalid');

    t.test('union', function(t) {
        var a = Extent()
            .include([0, 0])
            .include([10, 10]);
        var b = Extent()
            .include([0, 0])
            .include([-10, -10]);
        var c = Extent()
            .include([10, 10])
            .include([-10, -10]);
        t.equal(a.equals(c), false, 'union - before');
        t.equal(a.union(b).equals(c), true, 'union');
        t.end();
    });

    t.test('union - bbox', function(t) {
        var a = Extent()
            .include([0, 0])
            .include([10, 10]);
        var b = Extent()
            .include([0, 0])
            .include([-10, -10]);
        var c = Extent()
            .include([10, 10])
            .include([-10, -10]);
        t.equal(a.equals(c), false, 'union - before');
        t.equal(a.equals(c.bbox()), false, 'union - before');
        t.equal(a.union(b.bbox()).equals(c), true, 'union');
        t.end();
    });

    t.test('center', function(t) {
        t.deepEqual(Extent()
            .include([0, 0])
            .include([10, 10])
            .center(), [5, 5]);
        t.deepEqual(Extent()
            .include([0, 0])
            .center(), [0, 0]);
        t.deepEqual(Extent()
            .include([0, 0])
            .include([10, 0])
            .center(), [5, 0]);
        t.end();
    });

    t.end();
});

test('intersect', function(t) {
	var bbox1 = [0,0,1,1];
	var bbox2 = [0.5,0.5,2,2];

	t.equals(Extent(bbox1).intersect(bbox2), true);
	t.equals(Extent(bbox2).intersect(bbox1), true)

	t.end()
})
