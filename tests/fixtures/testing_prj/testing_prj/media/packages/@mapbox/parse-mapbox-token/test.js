'use strict';

var test = require('tape');
var parse = require('.');

test('public token', function(t) {
  var k = parse(
    'pk.eyJ1IjoiZmFrZXVzZXIiLCJhIjoicHBvb2xsIn0.sbihZCZJ56-fsFNKHXF8YQ'
  );
  t.deepEqual(k, {
    usage: 'pk',
    user: 'fakeuser',
    authorization: 'ppooll'
  });
  t.end();
});

test('secret token', function(t) {
  var k = parse(
    'sk.eyJ1IjoidGVzdG1lIiwiYSI6ImFiY2RlZiJ9.g134XoHqd_YSBeBUlql3aA'
  );
  t.deepEqual(k, {
    usage: 'sk',
    user: 'testme',
    authorization: 'abcdef'
  });
  t.end();
});

test('temp token', function(t) {
  var k = parse(
    'tk.eyJ1IjoidGVzdG1lIiwiYSI6ImFiY2RlZiIsInNjb3BlcyI6WyJ1c2VyOnJlYWQiLCJ1c2VyOndyaXRlIl0sImNsaWVudCI6Im1hcGJveC5jb20iLCJsbCI6MTQ0NzIwNzIxNDk0NX0.pbDxiAiFv1lud1CfHMfe9A'
  );
  t.deepEqual(k, {
    usage: 'tk',
    user: 'testme',
    authorization: 'abcdef',
    lastLogin: 1447207214945,
    client: 'mapbox.com',
    scopes: ['user:read', 'user:write']
  });
  t.end();
});

test('temp token + impersonation', function(t) {
  var k = parse(
    'tk.eyJ1IjoidGVzdG1lIiwiYSI6ImFiY2RlZiIsInNjb3BlcyI6WyJ1c2VyOnJlYWQiLCJ1c2VyOndyaXRlIl0sImNsaWVudCI6Im1hcGJveC5jb20iLCJsbCI6MTQ0NzIwNzIxNDk0NSwiaXUiOiJwZW5ueSJ9.YVvhYvOcl8dRsw6-tnk56w'
  );
  t.deepEqual(k, {
    usage: 'tk',
    user: 'testme',
    authorization: 'abcdef',
    lastLogin: 1447207214945,
    impersonator: 'penny',
    client: 'mapbox.com',
    scopes: ['user:read', 'user:write']
  });
  t.end();
});

test('token without a payload', function(t) {
  t.throws(function() {
    parse('pk');
  }, 'Invalid token');
  t.end();
});

test('token with a payload containing corrupt JSON', function(t) {
  t.throws(function() {
    parse('pk.eyJ1IjoiZmFrZXVzZXIiLCJhIjoicHBvb2xsIn.sbihZCZJ56-fsFNKHXF8YQ');
  }, 'Invalid token');
  t.end();
});

test('token with a corrupt payload', function(t) {
  t.throws(function() {
    parse('pk.eyJ1IjoiZmFrZXVzZXIiLCJhIjoicHBvb2x___In.sbihZCZJ56-fsFNKHXF8YQ');
  }, 'Invalid token');
  t.end();
});
