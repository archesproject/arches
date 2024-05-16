
import js from "@eslint/js";
import pluginVue from 'eslint-plugin-vue';
import tseslint from 'typescript-eslint';

import vueESLintParser from 'vue-eslint-parser';

export default [
    js.configs.recommended,
    ...pluginVue.configs['flat/recommended'],
    ...tseslint.configs.recommended,
    {
        "languageOptions": {
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
            "parser": vueESLintParser,
            "parserOptions": {
                "ecmaVersion": 11,
                "sourceType": "module",
                "requireConfigFile": false,
                "parser": {
                    "ts": "@typescript-eslint/parser"
                }
            },
        },
        "rules": {
            "semi": ["error", "always"],
            "vue/html-indent": ["error", 4]
        },
    },
]