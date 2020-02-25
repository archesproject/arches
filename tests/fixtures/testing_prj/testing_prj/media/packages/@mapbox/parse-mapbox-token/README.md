# @mapbox/parse-mapbox-token

[![Build Status](https://travis-ci.com/mapbox/parse-mapbox-token.svg?token=FB2dZNVWaGo68KZnwz9M&branch=master)](https://travis-ci.com/mapbox/parse-mapbox-token)

Parse a Mapbox API token, in any JS environment, including Node, browser, and React Native.

Learn about Mapbox API tokens by reading [Mapbox's API documentation](https://www.mapbox.com/api-documentation/#tokens).

## Installation

```
npm install @mapbox/parse-mapbox-token
```

## Usage

```js
var parseToken = require('@mapbox/parse-mapbox-token');
var parsed = parseToken('MY_MAPBOX_TOKEN');
var ownerId = parsed.user;
```

Returns an object representing the parsed token.
Properties vary depending on the type of token (public, secret, or temporary).

The following properties will always be present:

- **usage:** `pk`, `sk`, or `tk` (public, secret, or temporary).
- **user:** The ID of the token's owner.

The following properties may or may not be present:

- **authorization:** Authorization associated with the owner's account.
- **created:** Timestamp for the creation time of the token.
- **expires:** Timestamp for the expiration time of the token.
- **lastLogin:** Timestamp of the owner's last verified login.
- **scopes:** Array of scopes available to the token.
- **client:** OAuth client for which the token was granted.
- **impersonator:** ID of the user impersonating the account owner.

The token's payload is parsed with [`base-64`](https://github.com/mathiasbynens/base64).
