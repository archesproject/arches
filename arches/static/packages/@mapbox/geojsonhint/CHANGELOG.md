## 2.0.0

**This is the first stable release of geojsonhint that supports the [IETF GeoJSON standard](https://tools.ietf.org/html/rfc7946)**

* Fixes winding order reversal from beta releases.

## 2.0.0-beta2

* Fix missing `bin` directory from beta1 release.

## 2.0.0-beta1

* geojsonhint.js has been removed from this repository: it's a built file,
  useful for people who want to include geojson as a script tag. That file
  will still be available on unpkg, which is documented in the readme. This
  change ensures that contributors don't accidentally mess with the geojsonhint.js
  built file when they should be editing the source files in `lib`: now the
  repository contains only source files.
* vfile and vfile-reporter are upgraded. output is slightly different in formatting
  but functionally the same.

## 2.0.0-beta

* 2.0.0 will be released once the IETF Draft graduates to a specification
* geojsonhint now validates according to the [IETF specification of GeoJSON](https://datatracker.ietf.org/wg/geojson/documents/),
  which includes useful improvements in clarity.
* we now use `vfile` for fancier message formatting in output
* geojsonhint includes both warnings and errors now, so it can warn about
  things that are not technically wrong but can be improved, and enforce
  recommendations of the specification.

## 1.2.1

* Fixes a case where coordinate arrays that aren't nested deeply would trigger
  an uncaught exception
* Improves test coverage

## 1.2.0

* Introduces a new option, `noDuplicateMembers`, and a stricter default
  behavior: repeated properties, which are ambiguous in JSON, are now forbidden
  by default with geojsonhint.

## 1.1.0

* Adds purely object-based api, accessible via `require('geojsonhint/object')`.
  This is useful for performance-intensive browser libraries.
* Boosts code coverage testing to 100%

## 1.0.0

* Declares the public API
* This adds compatibility with objects as well as strings, and adds
  a benchmark to confirm that it's faster.
* Adds a .npmignore so that `npm install geojson` is significantly
  more efficient - excludes 496kb of testing fixtures
* Adds JSDoc comment to the source

## 0.3.4

* Tolerates `id` properties as numbers as well as strings, to match
  the actual specification.

## 0.3.3

* Enforces the type of the Feature.id property

## 0.3.2

* Detects & reports incorrectly nested LinearRing arrays

## 0.3.0

* Now uses `tap` for tests
* Modernized binary supports streams

## 0.2.0

* JSON parse errors are now parsed and output as objects rather than raw
  errors with strings.
* Stricter checking of LinearRing and Line coordinate length.
