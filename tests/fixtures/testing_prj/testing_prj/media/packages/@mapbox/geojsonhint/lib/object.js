var rightHandRule = require('./rhr');

/**
 * @alias geojsonhint
 * @param {(string|object)} GeoJSON given as a string or as an object
 * @param {Object} options
 * @param {boolean} [options.noDuplicateMembers=true] forbid repeated
 * properties. This is only available for string input, becaused parsed
 * Objects cannot have duplicate properties.
 * @param {boolean} [options.precisionWarning=true] warn if GeoJSON contains
 * unnecessary coordinate precision.
 * @returns {Array<Object>} an array of errors
 */
function hint(gj, options) {

    var errors = [];
    var precisionWarningCount = 0;
    var maxPrecisionWarnings = 10;
    var maxPrecision = 6;

    function root(_) {

        if ((!options || options.noDuplicateMembers !== false) &&
           _.__duplicateProperties__) {
            errors.push({
                message: 'An object contained duplicate members, making parsing ambigous: ' + _.__duplicateProperties__.join(', '),
                line: _.__line__
            });
        }

        if (requiredProperty(_, 'type', 'string')) {
            return;
        }

        if (!types[_.type]) {
            var expectedType = typesLower[_.type.toLowerCase()];
            if (expectedType !== undefined) {
                errors.push({
                    message: 'Expected ' + expectedType + ' but got ' + _.type + ' (case sensitive)',
                    line: _.__line__
                });
            } else {
                errors.push({
                    message: 'The type ' + _.type + ' is unknown',
                    line: _.__line__
                });
            }
        } else if (_) {
            types[_.type](_);
        }
    }

    function everyIs(_, type) {
        // make a single exception because typeof null === 'object'
        return _.every(function(x) {
            return x !== null && typeof x === type;
        });
    }

    function requiredProperty(_, name, type) {
        if (typeof _[name] === 'undefined') {
            return errors.push({
                message: '"' + name + '" member required',
                line: _.__line__
            });
        } else if (type === 'array') {
            if (!Array.isArray(_[name])) {
                return errors.push({
                    message: '"' + name +
                        '" member should be an array, but is an ' +
                        (typeof _[name]) + ' instead',
                    line: _.__line__
                });
            }
        } else if (type === 'object' && _[name] && _[name].constructor !== Object) {
            return errors.push({
                message: '"' + name +
                    '" member should be ' + (type) +
                    ', but is an ' + (_[name].constructor.name) + ' instead',
                line: _.__line__
            });
        } else if (type && typeof _[name] !== type) {
            return errors.push({
                message: '"' + name +
                    '" member should be ' + (type) +
                    ', but is an ' + (typeof _[name]) + ' instead',
                line: _.__line__
            });
        }
    }

    // https://tools.ietf.org/html/rfc7946#section-3.3
    function FeatureCollection(featureCollection) {
        crs(featureCollection);
        bbox(featureCollection);
        if (featureCollection.properties !== undefined) {
            errors.push({
                message: 'FeatureCollection object cannot contain a "properties" member',
                line: featureCollection.__line__
            });
        }
        if (featureCollection.coordinates !== undefined) {
            errors.push({
                message: 'FeatureCollection object cannot contain a "coordinates" member',
                line: featureCollection.__line__
            });
        }
        if (!requiredProperty(featureCollection, 'features', 'array')) {
            if (!everyIs(featureCollection.features, 'object')) {
                return errors.push({
                    message: 'Every feature must be an object',
                    line: featureCollection.__line__
                });
            }
            featureCollection.features.forEach(Feature);
        }
    }

    // https://tools.ietf.org/html/rfc7946#section-3.1.1
    function position(_, line) {
        if (!Array.isArray(_)) {
            return errors.push({
                message: 'position should be an array, is a ' + (typeof _) +
                    ' instead',
                line: _.__line__ || line
            });
        }
        if (_.length < 2) {
            return errors.push({
                message: 'position must have 2 or more elements',
                line: _.__line__ || line
            });
        }
        if (_.length > 3) {
            return errors.push({
                message: 'position should not have more than 3 elements',
                level: 'message',
                line: _.__line__ || line
            });
        }
        if (!everyIs(_, 'number')) {
            return errors.push({
                message: 'each element in a position must be a number',
                line: _.__line__ || line
            });
        }

        if (options && options.precisionWarning) {
            if (precisionWarningCount === maxPrecisionWarnings) {
                precisionWarningCount += 1;
                return errors.push({
                    message: 'truncated warnings: we\'ve encountered coordinate precision warning ' + maxPrecisionWarnings + ' times, no more warnings will be reported',
                    level: 'message',
                    line: _.__line__ || line
                });
            } else if (precisionWarningCount < maxPrecisionWarnings) {
                _.forEach(function(num) {
                    var precision = 0;
                    var decimalStr = String(num).split('.')[1];
                    if (decimalStr !== undefined)
                        precision = decimalStr.length;
                    if (precision > maxPrecision) {
                        precisionWarningCount += 1;
                        return errors.push({
                            message: 'precision of coordinates should be reduced',
                            level: 'message',
                            line: _.__line__ || line
                        });
                    }
                });
            }
        }
    }

    function positionArray(coords, type, depth, line) {
        if (line === undefined && coords.__line__ !== undefined) {
            line = coords.__line__;
        }
        if (depth === 0) {
            return position(coords, line);
        }
        if (depth === 1 && type) {
            if (type === 'LinearRing') {
                if (!Array.isArray(coords[coords.length - 1])) {
                    errors.push({
                        message: 'a number was found where a coordinate array should have been found: this needs to be nested more deeply',
                        line: line
                    });
                    return true;
                }
                if (coords.length < 4) {
                    errors.push({
                        message: 'a LinearRing of coordinates needs to have four or more positions',
                        line: line
                    });
                }
                if (coords.length &&
                    (coords[coords.length - 1].length !== coords[0].length ||
                    !coords[coords.length - 1].every(function(pos, index) {
                        return coords[0][index] === pos;
                }))) {
                    errors.push({
                        message: 'the first and last positions in a LinearRing of coordinates must be the same',
                        line: line
                    });
                    return true;
                }
            } else if (type === 'Line' && coords.length < 2) {
                return errors.push({
                    message: 'a line needs to have two or more coordinates to be valid',
                    line: line
                });
            }
        }
        if (!Array.isArray(coords)) {
            errors.push({
                message: 'a number was found where a coordinate array should have been found: this needs to be nested more deeply',
                line: line
            });
        } else {
            var results = coords.map(function(c) {
                return positionArray(c, type, depth - 1, c.__line__ || line);
            });
            return results.some(function(r) {
                return r;
            });
        }
    }

    function crs(_) {
        if (!_.crs) return;
        var defaultCRSName = 'urn:ogc:def:crs:OGC:1.3:CRS84';
        if (typeof _.crs === 'object' && _.crs.properties && _.crs.properties.name === defaultCRSName) {
            errors.push({
                message: 'old-style crs member is not recommended, this object is equivalent to the default and should be removed',
                line: _.__line__
            });
        } else {
            errors.push({
                message: 'old-style crs member is not recommended',
                line: _.__line__
            });
        }
    }

    function bbox(_) {
        if (!_.bbox) {
            return;
        }
        if (Array.isArray(_.bbox)) {
            if (!everyIs(_.bbox, 'number')) {
                errors.push({
                    message: 'each element in a bbox member must be a number',
                    line: _.bbox.__line__
                });
            }
            if (!(_.bbox.length === 4 || _.bbox.length === 6)) {
                errors.push({
                    message: 'bbox must contain 4 elements (for 2D) or 6 elements (for 3D)',
                    line: _.bbox.__line__
                });
            }
            return errors.length;
        }
        errors.push({
            message: 'bbox member must be an array of numbers, but is a ' + (typeof _.bbox),
            line: _.__line__
        });
    }

    function geometrySemantics(geom) {
        if (geom.properties !== undefined) {
            errors.push({
                message: 'geometry object cannot contain a "properties" member',
                line: geom.__line__
            });
        }
        if (geom.geometry !== undefined) {
            errors.push({
                message: 'geometry object cannot contain a "geometry" member',
                line: geom.__line__
            });
        }
        if (geom.features !== undefined) {
            errors.push({
                message: 'geometry object cannot contain a "features" member',
                line: geom.__line__
            });
        }
    }

    // https://tools.ietf.org/html/rfc7946#section-3.1.2
    function Point(point) {
        crs(point);
        bbox(point);
        geometrySemantics(point);
        if (!requiredProperty(point, 'coordinates', 'array')) {
            position(point.coordinates);
        }
    }

    // https://tools.ietf.org/html/rfc7946#section-3.1.6
    function Polygon(polygon) {
        crs(polygon);
        bbox(polygon);
        if (!requiredProperty(polygon, 'coordinates', 'array')) {
            if (!positionArray(polygon.coordinates, 'LinearRing', 2)) {
                rightHandRule(polygon, errors);
            }
        }
    }

    // https://tools.ietf.org/html/rfc7946#section-3.1.7
    function MultiPolygon(multiPolygon) {
        crs(multiPolygon);
        bbox(multiPolygon);
        if (!requiredProperty(multiPolygon, 'coordinates', 'array')) {
            if (!positionArray(multiPolygon.coordinates, 'LinearRing', 3)) {
                rightHandRule(multiPolygon, errors);
            }
        }
    }

    // https://tools.ietf.org/html/rfc7946#section-3.1.4
    function LineString(lineString) {
        crs(lineString);
        bbox(lineString);
        if (!requiredProperty(lineString, 'coordinates', 'array')) {
            positionArray(lineString.coordinates, 'Line', 1);
        }
    }

    // https://tools.ietf.org/html/rfc7946#section-3.1.5
    function MultiLineString(multiLineString) {
        crs(multiLineString);
        bbox(multiLineString);
        if (!requiredProperty(multiLineString, 'coordinates', 'array')) {
            positionArray(multiLineString.coordinates, 'Line', 2);
        }
    }

    // https://tools.ietf.org/html/rfc7946#section-3.1.3
    function MultiPoint(multiPoint) {
        crs(multiPoint);
        bbox(multiPoint);
        if (!requiredProperty(multiPoint, 'coordinates', 'array')) {
            positionArray(multiPoint.coordinates, '', 1);
        }
    }

    // https://tools.ietf.org/html/rfc7946#section-3.1.8
    function GeometryCollection(geometryCollection) {
        crs(geometryCollection);
        bbox(geometryCollection);
        if (!requiredProperty(geometryCollection, 'geometries', 'array')) {
            if (!everyIs(geometryCollection.geometries, 'object')) {
                errors.push({
                    message: 'The geometries array in a GeometryCollection must contain only geometry objects',
                    line: geometryCollection.__line__
                });
            }
            if (geometryCollection.geometries.length === 1) {
                errors.push({
                    message: 'GeometryCollection with a single geometry should be avoided in favor of single part or a single object of multi-part type',
                    line: geometryCollection.geometries.__line__
                });
            }
            geometryCollection.geometries.forEach(function(geometry) {
                if (geometry) {
                    if (geometry.type === 'GeometryCollection') {
                        errors.push({
                            message: 'GeometryCollection should avoid nested geometry collections',
                            line: geometryCollection.geometries.__line__
                        });
                    }
                    root(geometry);
                }
            });
        }
    }

    // https://tools.ietf.org/html/rfc7946#section-3.2
    function Feature(feature) {
        crs(feature);
        bbox(feature);
        // https://github.com/geojson/draft-geojson/blob/master/middle.mkd#feature-object
        if (feature.id !== undefined &&
            typeof feature.id !== 'string' &&
            typeof feature.id !== 'number') {
            errors.push({
                message: 'Feature "id" member must have a string or number value',
                line: feature.__line__
            });
        }
        if (feature.features !== undefined) {
            errors.push({
                message: 'Feature object cannot contain a "features" member',
                line: feature.__line__
            });
        }
        if (feature.coordinates !== undefined) {
            errors.push({
                message: 'Feature object cannot contain a "coordinates" member',
                line: feature.__line__
            });
        }
        if (feature.type !== 'Feature') {
            errors.push({
                message: 'GeoJSON features must have a type=feature member',
                line: feature.__line__
            });
        }
        requiredProperty(feature, 'properties', 'object');
        if (!requiredProperty(feature, 'geometry', 'object')) {
            // https://tools.ietf.org/html/rfc7946#section-3.2
            // tolerate null geometry
            if (feature.geometry) root(feature.geometry);
        }
    }

    var types = {
        Point: Point,
        Feature: Feature,
        MultiPoint: MultiPoint,
        LineString: LineString,
        MultiLineString: MultiLineString,
        FeatureCollection: FeatureCollection,
        GeometryCollection: GeometryCollection,
        Polygon: Polygon,
        MultiPolygon: MultiPolygon
    };

    var typesLower = Object.keys(types).reduce(function(prev, curr) {
        prev[curr.toLowerCase()] = curr;
        return prev;
    }, {});

    if (typeof gj !== 'object' ||
        gj === null ||
        gj === undefined) {
        errors.push({
            message: 'The root of a GeoJSON object must be an object.',
            line: 0
        });
        return errors;
    }

    root(gj);

    errors.forEach(function(err) {
        if ({}.hasOwnProperty.call(err, 'line') && err.line === undefined) {
            delete err.line;
        }
    });

    return errors;
}

module.exports.hint = hint;
