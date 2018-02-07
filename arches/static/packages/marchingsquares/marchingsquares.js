/*!
* @license GNU Affero General Public License.
* Copyright (c) 2015, 2015 Ronny Lorenz <ronny@tbi.univie.ac.at>
* v. 1.2.0
* https://github.com/RaumZeit/MarchingSquares.js
*/

(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['./marchingsquares-isobands', './marchingsquares-isocontours'], factory);
    } else if (typeof module === 'object' && module.exports) {
        // Node. Does not work with strict CommonJS, but
        // only CommonJS-like environments that support module.exports,
        // like Node.
        module.exports = factory(require('./marchingsquares-isobands'),require('./marchingsquares-isocontours'));
    } else {
        // Browser globals (root is window)
        root.MarchingSquaresJS = factory(
                                    (root.MarchingSquaresJS) ? root.MarchingSquaresJS.isoBands : null,
                                    (root.MarchingSquaresJS) ? root.MarchingSquaresJS.isoContours : null
                                  );
    }
}(this, function (isoBands, isoContours) {
  return {
      isoBands : (typeof isoBands === 'function') ? isoBands : (((typeof isoBands === 'object') && (typeof isoBands.isoBands === 'function')) ? isoBands.isoBands : null),
      isoContours: (typeof isoContours === 'function') ? isoContours : (((typeof isoContours === 'object') && (typeof isoContours.isoContours === 'function')) ? isoContours.isoContours : null)
  };
}));
