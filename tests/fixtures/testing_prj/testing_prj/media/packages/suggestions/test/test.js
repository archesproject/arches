'use strict';

var test = require('tape');
var Suggestions = require('../');

var keyUpEvent = document.createEvent('HTMLEvents');
keyUpEvent.initEvent('keyup', true, false);
var focusEvent = document.createEvent('HTMLEvents');
focusEvent.initEvent('focus', true, false);
var blurEvent = document.createEvent('HTMLEvents');
blurEvent.initEvent('blur', true, false);

test('basics', function(t) {
  var parent = document.createElement('div');
  var input = document.createElement('input');
  parent.appendChild(input);

  var data = ['bear', 'bearing', 'bar', 'ball'];
  var typeahead = new Suggestions(input, data);

  var suggestionsContainer = parent.querySelector('ul');

  t.ok(suggestionsContainer, 'suggestions container exists');
  t.equal(suggestionsContainer.style.display, 'none', 'suggestions container is initially hidden');
  t.equal(typeahead.data, data, 'data is set');

  input.value = 'ear';

  input.dispatchEvent(keyUpEvent);
  input.dispatchEvent(focusEvent);

  t.equal(suggestionsContainer.style.display, 'block', 'suggestions container is displayed');

  var suggestionList = suggestionsContainer.querySelectorAll('li');
  var suggestionResults = [];
  Array.prototype.forEach.call(suggestionList, function(el) {
    suggestionResults.push(el.textContent);
  });

  t.deepEqual(suggestionResults, ['bear', 'bearing'], 'populate a correct results');

  input.dispatchEvent(blurEvent);

  t.equal(suggestionsContainer.style.display, 'none', 'suggestions container hidden on blur');

  // Results are still present on focus
  input.dispatchEvent(focusEvent);
  t.ok(suggestionsContainer.querySelectorAll('li').length, 'results still present on focus');
  t.equal(suggestionList[0].classList.contains('active'), true, 'first item is active');

  // TODO test results hightlighting when keyboard events
  // emit up/down keystrokes.

  // TODO test that enter adds the result to the input containar
  t.end();
});

test('options', function(t) {
  var parent = document.createElement('div');
  var input = document.createElement('input');
  parent.appendChild(input);

  var data = ['bear', 'bearing', 'bar', 'ball'];
  new Suggestions(input, data, {
    minLength: 3,
    limit: 1
  });

  var suggestionsContainer = parent.querySelector('ul');

  input.value = 'be';
  input.dispatchEvent(keyUpEvent);
  input.dispatchEvent(focusEvent);
  t.equal(suggestionsContainer.style.display, 'none', 'options.minLength passed by not populating a result');

  input.value = 'bea';
  input.dispatchEvent(keyUpEvent);
  input.dispatchEvent(focusEvent);
  t.equal(suggestionsContainer.style.display, 'block', 'options.minLength passed by populating results after 3 chars');

  t.equal(suggestionsContainer.querySelectorAll('li').length, 1, 'options.limit passed');
  t.end();
});

test('option: no filtering', function(t) {
  var parent = document.createElement('div');
  var input = document.createElement('input');
  parent.appendChild(input);

  var data = ['bear', 'bearing', 'bar', 'ball'];
  new Suggestions(input, data, {
    filter: false
  });

  var suggestionsContainer = parent.querySelector('ul');

  input.value = 'be';
  input.dispatchEvent(keyUpEvent);
  input.dispatchEvent(focusEvent);
  t.equal(suggestionsContainer.querySelectorAll('li').length, 4, 'options.filter:false passed');
  t.end();
});

test('option: no filtering special characters', function(t) {
  var parent = document.createElement('div');
  var input = document.createElement('input');
  parent.appendChild(input);

  var data = ['pea', 'pea(nut)', 'pea(nut)butter'];
  new Suggestions(input, data, {
    filter: false
  });

  var suggestionsContainer = parent.querySelector('ul');

  input.value = 'ea(nu';
  input.dispatchEvent(keyUpEvent);
  input.dispatchEvent(focusEvent);

  var innerHTMLs = Array.from(suggestionsContainer.querySelectorAll('a')).map(function(a) {
    return a.innerHTML;
  });

  t.deepEqual(innerHTMLs, ['pea', 'p<strong>ea(nu</strong>t)', 'p<strong>ea(nu</strong>t)butter'], 'special characters options.filter:false passed');
  t.end();
});

test('option: no hide on blur', function(t) {
  var parent = document.createElement('div');
  var input = document.createElement('input');
  parent.appendChild(input);

  var data = ['testing'];
  new Suggestions(input, data, {
    minLength: 3,
    limit: 1,
    hideOnBlur: false
  });

  var suggestionsContainer = parent.querySelector('ul');

  input.value = 'test';
  input.dispatchEvent(keyUpEvent);
  input.dispatchEvent(focusEvent);
  t.equal(suggestionsContainer.style.display, 'block', 'options.hideOnBlur passed by not hiding prior to blur');
  input.dispatchEvent(blurEvent);
  t.equal(suggestionsContainer.style.display, 'block', 'options.hideOnBlur passed by not hiding on blur');

  t.end();
});

test('Suggestion.getItemValue', function(t) {
  var parent = document.createElement('div');
  var input = document.createElement('input');
  parent.appendChild(input);

  var data = [{
    name: 'bear',
    id: 0
  }, {
    name: 'bearing',
    id: 1
  }, {
    name: 'bar',
    id: 2
  }, {
    name: 'ball',
    id: 3
  }];

  new Suggestions(input, data, {getItemValue: function(item) { return item.name; }});

  input.value = 'bear';
  input.dispatchEvent(keyUpEvent);
  input.dispatchEvent(focusEvent);

  t.ok(parent.querySelectorAll('ul li').length, 'results populated when an object of arrays were passed');
  var firstElement = parent.querySelectorAll('ul li').item(0).innerHTML;
  // remove the auto-formatted <strong>s so we can do an equality comparison
  firstElement = firstElement.split("<strong>").join("").split("</strong>").join("");
  t.equals(firstElement, "<a>bear</a>")
  t.end();
});

test('Suggestion.update', function(t) {
  var parent = document.createElement('div');
  var input = document.createElement('input');
  parent.appendChild(input);

  // Initial array of data
  var data = ['bear', 'bearing', 'bar', 'ball'];

  var typeahead = new Suggestions(input, data);
  var suggestionsContainer = parent.querySelector('ul');

  typeahead.update(['hear', 'hearing', 'har', 'hail']);
  input.value = 'hear';

  input.dispatchEvent(keyUpEvent);
  input.dispatchEvent(focusEvent);

  var suggestionList = suggestionsContainer.querySelectorAll('li');
  var suggestionResults = [];
  Array.prototype.forEach.call(suggestionList, function(el) {
    suggestionResults.push(el.textContent);
  });

  t.deepEqual(suggestionResults, ['hear', 'hearing'], 'data array was revised');
  t.end();
});

test('Suggestion.clear', function(t) {
  var parent = document.createElement('div');
  var input = document.createElement('input');
  parent.appendChild(input);

  // Initial array of data
  var data = ['bear', 'bearing', 'bar', 'ball'];

  var typeahead = new Suggestions(input, data);
  var suggestionsContainer = parent.querySelector('ul');

  typeahead.clear();
  input.value = 'hear';

  input.dispatchEvent(keyUpEvent);
  input.dispatchEvent(focusEvent);

  t.equal(suggestionsContainer.querySelectorAll('li').length, 0, 'no container results were returned');
  t.end();
});

test('Suggestion.render [no filter]', function(t) {
  var parent = document.createElement('div');
  var input = document.createElement('input');
  parent.appendChild(input);

  var data = [{
    name: 'bear',
    id: 0
  }, {
    name: 'bearing',
    id: 1
  }, {
    name: 'bar',
    id: 2
  }, {
    name: 'ball',
    id: 3
  }];

  var typeahead = new Suggestions(input, data, {filter: false});
  typeahead.render = function(item) { return '<b class="custom result">' + item.name +  "</b>"; };

  input.value = 'bear';
  input.dispatchEvent(keyUpEvent);
  input.dispatchEvent(focusEvent);

  t.ok(parent.querySelectorAll('ul li').length, 'results populated when an object of arrays were passed');
  var firstItem = parent.getElementsByTagName("b").item(0);
  t.equals(firstItem.className, 'custom result', 'the custom class name is applied to the rendered elements');
  t.equals(firstItem.innerHTML, 'bear', 'the rendered text is correct');
  t.end();
});

test('Suggestion.render [filter]', function(t) {
  var parent = document.createElement('div');
  var input = document.createElement('input');
  parent.appendChild(input);

  var data = [{
    name: 'bear',
    id: 0
  }, {
    name: 'bearing',
    id: 1
  }, {
    name: 'bar',
    id: 2
  }, {
    name: 'ball',
    id: 3
  }];

  var typeahead = new Suggestions(input, data);
  typeahead.render = function(item) { return '<b class="custom result">' + item.name +  "</b>"; };
  typeahead.getItemValue = function(item) { return item.name };
  input.value = 'bear';
  input.dispatchEvent(keyUpEvent);
  input.dispatchEvent(focusEvent);

  t.ok(parent.querySelectorAll('ul li').length, 'results populated when an object of arrays were passed');
  var firstItem = parent.getElementsByTagName("b").item(0);
  t.equals(firstItem.className, 'custom result', 'the custom class name is applied to the rendered elements');
  t.equals(firstItem.innerHTML, 'bear', 'the rendered text is correct');
  t.end();
});

test('Suggestion.render [filter with sourceformatted text]', function(t) {
  var parent = document.createElement('div');
  var input = document.createElement('input');
  parent.appendChild(input);

  var data = [{
    name: 'bear',
    id: 0
  }, {
    name: 'bearing',
    id: 1
  }, {
    name: 'bar',
    id: 2
  }, {
    name: 'ball',
    id: 3
  }];

  var typeahead = new Suggestions(input, data, {filter: false});
  typeahead.getItemValue = function(item) { return item.name };

  input.value = 'bear';
  input.dispatchEvent(keyUpEvent);
  input.dispatchEvent(focusEvent);

  t.ok(parent.querySelectorAll('ul li').length, 'results populated when an object of arrays were passed');
  var firstItem = parent.querySelectorAll('ul li').item(0);
  t.equals(firstItem.innerHTML, '<a><strong>bear</strong></a>', 'the rendered text is correct when no custom rendering function is given');
  t.end();
});

test('suggestion.renderError', function(t){
  var parent = document.createElement('div');
  var input = document.createElement('input');
  parent.appendChild(input)
  var typeahead = new Suggestions(input, [], {filter: false});
  typeahead.renderError("This is a test");
  var firstItem = parent.querySelectorAll('ul li').item(0);
  t.equals(firstItem.innerHTML, 'This is a test', 'the rendered text is correct when rendering an error');
  t.end();
})

// close the smokestack window once tests are complete
test('shutdown', function(t) {
  t.end();
  setTimeout(function() {
    window.close();
  });
});
