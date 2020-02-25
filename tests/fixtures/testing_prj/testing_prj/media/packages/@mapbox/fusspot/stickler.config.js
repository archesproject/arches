'use strict';

module.exports = {
  jsLint: {
    es5: true,
    node: true,
    overrides: [
      {
        files: ['test/**', 'test/*'],
        jest: true
      }
    ]
  }
};
