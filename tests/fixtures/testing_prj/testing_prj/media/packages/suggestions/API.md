# Suggestions

A typeahead component for inputs

**Parameters**

-   `el` **HTMLInputElement** A valid HTML input element
-   `data` **Array** An array of data used for results
-   `options` **Object** 
    -   `options.limit` **[Number]** Max number of results to display in the auto suggest list. (optional, default `5`)
    -   `options.minLength` **[Number]** Number of characters typed into an input to trigger suggestions. (optional, default `2`)

**Examples**

```javascript
// in the browser
var input = document.querySelector('input');
var data = [
  'Roy Eldridge',
  'Roy Hargrove',
  'Rex Stewart'
];

new Suggestions(input, data);

// with options
var input = document.querySelector('input');
var data = [{
  name: 'Roy Eldridge',
  year: 1911
}, {
  name: 'Roy Hargrove',
  year: 1969
}, {
  name: 'Rex Stewart',
  year: 1907
}];

var typeahead = new Suggestions(input, data, {
  filter: false, // Disable filtering
  minLength: 3, // Number of characters typed into an input to trigger suggestions.
  limit: 3 //  Max number of results to display.
});

// As we're passing an object of an arrays as data, override
// `getItemValue` by specifying the specific property to search on.
typeahead.getItemValue = function(item) { return item.name };

input.addEventListener('change', function() {
  console.log(typeahead.selected); // Current selected item.
});

// With browserify
var Suggestions = require('suggestions');

new Suggestions(input, data);
```

Returns **Suggestions** `this`

## clear

Clears data

## getItemValue

For a given item in the data array, return what should be used as the candidate string

**Parameters**

-   `item` **Object or String** an item from the data array

Returns **String** item

## match

Evaluates whether an array item qualifies as a match with the current query

**Parameters**

-   `candidate` **String** a possible item from the array passed
-   `query` **String** the current query

Returns **Boolean** 

## normalize

Normalize the results list and input value for matching

**Parameters**

-   `value` **String** 

Returns **String** 

## render

For a given item in the data array, return a string of html that should be rendered in the dropdown

**Parameters**

-   `item` **Object or String** an item from the data array
-   `sourceFormatting` **String** a string that has pre-formatted html that should be passed directly through the render function

Returns **String** html

## update

Update data previously passed

**Parameters**

-   `revisedData` **Array** 
