var Benchmark = require('benchmark');
global.Extent = require('./');
global.pip = require('point-in-polygon');

var suite = new Benchmark.Suite();

// add tests
suite
.add({
    name: 'contains',
    fn: function() {
         ext.contains([0, 10]);
    },
    setup: function() {
        var ext = global.Extent()
            .include([0, 0])
            .include([10, 10]);
    }
})
.add({
    name: 'pip',
    fn: function() {
         global.pip([0, 10], extG);
    },
    setup: function() {
        var extG = global.Extent()
            .include([0, 0])
            .include([10, 10])
            .polygon().coordinates;
    }
})
.add({
    name: 'fastContains',
    fn: function() {
        extContains([0, 10]);
    },
    setup: function() {
        var extContains = global.Extent()
            .include([0, 0])
            .include([10, 10]).contains();
    }
})
// add listeners
.on('cycle', function(event) {
  console.log(String(event.target));
})
.on('complete', function() {
  console.log('Fastest is ' + this.filter('fastest').pluck('name'));
})
// run async
.run({ 'async': true });
