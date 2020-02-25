'use strict';

var base64 = require('base-64');

var tokenCache = {};

function parseToken(token) {
  if (tokenCache[token]) {
    return tokenCache[token];
  }

  var parts = token.split('.');
  var usage = parts[0];
  var rawPayload = parts[1];
  if (!rawPayload) {
    throw new Error('Invalid token');
  }

  var parsedPayload = parsePaylod(rawPayload);

  var result = {
    usage: usage,
    user: parsedPayload.u
  };
  if (has(parsedPayload, 'a')) result.authorization = parsedPayload.a;
  if (has(parsedPayload, 'exp')) result.expires = parsedPayload.exp * 1000;
  if (has(parsedPayload, 'iat')) result.created = parsedPayload.iat * 1000;
  if (has(parsedPayload, 'scopes')) result.scopes = parsedPayload.scopes;
  if (has(parsedPayload, 'client')) result.client = parsedPayload.client;
  if (has(parsedPayload, 'll')) result.lastLogin = parsedPayload.ll;
  if (has(parsedPayload, 'iu')) result.impersonator = parsedPayload.iu;

  tokenCache[token] = result;
  return result;
}

function parsePaylod(rawPayload) {
  try {
    return JSON.parse(base64.decode(rawPayload));
  } catch (parseError) {
    throw new Error('Invalid token');
  }
}

function has(obj, key) {
  return Object.prototype.hasOwnProperty.call(obj, key);
}

module.exports = parseToken;
