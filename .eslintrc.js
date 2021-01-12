module.exports = {
    "extends": "eslint:recommended",
    // add your custom rules here
    rules: {
        "semi": ["error", "always"],
        "indent": ["error", 4],
        "space-before-function-paren": ["error", "never"],
        "no-extra-boolean-cast": 0, // 0=silence, 1=warning, 2=error
        // allow async-await
        'generator-star-spacing': 'off',
        // allow debugger during development
        'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
        "camelcase": [2, {"properties": "always"}],
        "no-restricted-syntax": [
            "error",
            {
                selector: "LabeledStatement",
                message: "Labels are a form of GOTO; using them makes code confusing and hard to maintain and understand.",
            },
            {
                selector: "WithStatement",
                message: "`with` is disallowed in strict mode because it makes code impossible to predict and optimize.",
            }
        ]
    },
    "globals": {
        "define": false,
        "require": false,
        "window": false,
        "console": false,
        "history": false,
        "location": false,
        "Promise": false,
        "setTimeout": false
    }
};
