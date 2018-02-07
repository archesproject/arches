var test = require('tap').test,
    flatten = require('../flatten');

test('flatten', function(t) {
    t.deepEqual(flatten([0, 0]), [[0, 0]], 'unfold');
    t.deepEqual(flatten([[0, 0]]), [[0, 0]], 'noop');
    t.deepEqual(flatten([[[0, 0]]]), [[0, 0]], 'single level');
    t.deepEqual(flatten([[[0, 0], [10, 10]]]), [[0, 0], [10, 10]], 'double level');
    t.deepEqual(flatten([[[[0, 0], [10, 10]]]]), [[0, 0], [10, 10]], 'triple level');
    t.deepEqual(flatten([[[[0, 0], [10, 10]], [[[5, 5]]]]]), [[0, 0], [10, 10], [5, 5]], 'quadruple level');
    t.end();
});
