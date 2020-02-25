# 1.0.1

* Fix `coordInBBBOX` function to fix the output of points within small bounding
  boxes.

# 1.0.0

* Total change to API: types are now separated into their own individual
  functions. Call `.polygon` and `.point` instead of specifying a type
  parameter.
* Add `geojsonRandom.position(bbox?)`
* Add optional `bbox` parameter to points.
