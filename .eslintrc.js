module.exports = {
    "parser": "@babel/eslint-parser",
    "extends": [
      "eslint:recommended"
    ],
    "env": {
      "browser": true,
      "es6": true,
      "node": true
    },
    "parserOptions": {
      "ecmaVersion": 8,
      "sourceType": "module",
      "requireConfigFile": false
    },
    "globals": {
        "define": false,
        "require": false,
        "window": false,
        "console": false,
        "history": false,
        "location": false,
        "Promise": false,
        "setTimeout": false,
        "URL": false,
        "URLSearchParams": false,
        "fetch": false
    },
    "rules": {
        "semi": ["error", "always"],
        "indent": ["error", 4],
        "space-before-function-paren": ["error", "never"],
        "no-extra-boolean-cast": 0, // 0=silence, 1=warning, 2=error
        // allow async-await
        'generator-star-spacing': 'off',
        // allow debugger during development
        'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
        "camelcase": [2, {"properties": "always"}]
    }
}
  