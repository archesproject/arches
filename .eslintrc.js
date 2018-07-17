module.exports = {
    "extends": "standard",
    // add your custom rules here
    rules: {
        "semi": ["error", "always"],
        "indent": ["error", 4],
        "space-before-function-paren": ["error", "never"],
        "no-extra-boolean-cast": 0, // 0=silence, 1=warning, 2=error
        // allow async-await
        'generator-star-spacing': 'off',
        // allow debugger during development
        'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off'
    },
    "globals": {
        "define": false
    }
};
