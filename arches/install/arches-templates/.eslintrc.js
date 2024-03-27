module.exports = {
    "extends": [
        "eslint:recommended",
        'plugin:@typescript-eslint/recommended',
        'plugin:vue/vue3-recommended',
    ],
    "root": true,
    "env": {
        "browser": true,
        "es6": true,
        "node": true
    },
    "parser": "vue-eslint-parser",
    "parserOptions": {
        "ecmaVersion": 11,
        "sourceType": "module",
        "requireConfigFile": false,
        "parser": {
            "ts": "@typescript-eslint/parser"
        }
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
    },
    "overrides": [
        {
            "files": [ "*.vue" ],
            "rules": {
                "vue/html-indent": [2, 4],
            }
        },
        {
            "files": [ "*.js" ],
            "rules": {
                "indent": ["error", 4],
                "space-before-function-paren": ["error", "never"],
                "no-extra-boolean-cast": 0, // 0=silence, 1=warning, 2=error
                // allow async-await
                'generator-star-spacing': 'off',
                // allow debugger during development
                'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
                'no-unused-vars': [1, {
                    argsIgnorePattern: '^_'
                }],
                "camelcase": [1, {"properties": "always"}],
            }
        }
    ]
};
  