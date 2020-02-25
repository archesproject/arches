# knockout.mapping

[![Build Status](https://travis-ci.org/crissdev/knockout.mapping.svg?branch=master)](https://travis-ci.org/crissdev/knockout.mapping)
[![npm version](https://badge.fury.io/js/knockout-mapping.svg)](http://badge.fury.io/js/knockout-mapping)


> Object mapping plugin for [Knockout](http://knockoutjs.com/)


## Documentation

Official documentation [here](http://knockoutjs.com/documentation/plugins-mapping.html).


## Install

#### Bower

```sh
bower install bower-knockout-mapping --save-dev
```

#### NPM

```sh
npm install knockout-mapping --save
```


## Quick Start

```js

var data = {
    email: 'demo@example.com',
    name: 'demo',
    addresses: [
        { type: 'home', country: 'Romania', city: 'Cluj' },
        { type: 'work', country: 'Spain', city: 'Barcelona' }
    ]
};

// Create a view model from data
var viewModel = ko.mapping.fromJS(data);

// Now use the viewModel to change some values (properties are now observable)
viewModel.email('demo2@example.com');
viewModel.name('demo2');
viewModel.addresses()[0].city('Bucharest');

// Retrieve the updated data (as JS object)
var newData = ko.mapping.toJS(viewModel);

// newData now looks like this
{
  email: 'demo2@example.com',
  name: 'demo2',
  addresses: [
    { type: 'home', country: 'Romania', city: 'Bucharest' },
    { type: 'work', country: 'Spain', city: 'Barcelona' }
  ]
}

```

Run this example in [JSFiddle](http://jsfiddle.net/wmeqx7ss/141/).


## Test

Continuous Integration tests are done with Travis, and the associated Gulp task is `test-ci`.
For development `test` task is used, which runs the tests against the latest version of Knockout.


## License

[MIT](http://www.opensource.org/licenses/mit-license.php)
