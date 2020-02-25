Suggestions
---

A typeahead component for inputs

[![npm version](http://img.shields.io/npm/v/suggestions.svg)](https://npmjs.org/package/suggestions) [![Circle CI](https://circleci.com/gh/tristen/suggestions/tree/gh-pages.svg?style=svg)](https://circleci.com/gh/tristen/suggestions/tree/gh-pages)

[__Demo__](http://tristen.ca/suggestions/demo/)

### Usage

#### Quick start

``` html
<script src='suggestions.js'></script>

<script>
  var input = document.querySelector('input');
  var data = ['foo', 'bar', 'baz', 'qux'];
  new Suggestions(input, data);
</script>
```

#### Usage with Browserify

```js
var Suggestions = require('suggestions');

var input = document.querySelector('input');
var data = ['foo', 'bar', 'baz', 'qux'];
new Suggestions(input, data);
```

#### Suggestions with options

```js
var Suggestions = require('suggestions');

var input = document.querySelector('input');

var data = [{
  name: 'Roy Eldridge',
  year: 1911
}, {
  name: 'Roy Hargrove',
  year: 1969
}, {
  name: 'Tim Hagans',
  year: 1954
}, {
  name: 'Tom Harrell',
  year: 1946
}, {
  name: 'Freddie Hubbard',
  year: 1938
}, {
  name: 'Nicholas Payton',
  year: 1973
}, {
  name: 'Miles Davis',
  year: 1926
}, {
  name: 'Dizzy Gillespie',
  year: 1917
}, {
  name: 'Rex Stewart',
  year: 1907
}];

var typeahead = new Suggestions(input, data, {
  minLength: 3, // Number of characters typed into an input to trigger suggestions.
  limit: 3 //  Max number of results to display. 
});

typeahead.getItemValue = function(item) {
  return item.name
};

input.addEventListener('change', function() {
  console.log(typeahead.selected); // Current selected item.
});
```

### [`API`](https://github.com/tristen/suggestions/blob/gh-pages/API.md)

### Running locally

    npm install && npm start

`npm start` will run a server on port 9966. Visit http://localhost:9966/demo/
to view the example.

### Testing

    npm run test

### Credit

This project is adapted from https://github.com/marcojetson/type-ahead.js
