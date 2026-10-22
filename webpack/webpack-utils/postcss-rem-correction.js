/* eslint-disable */

const fs = require('fs');
const Path = require('path');

// Legacy Arches chrome sets a 0.62rem html root, which shrinks every rem on the page.
// 1. Any rule that sets the html font size also gets --arches-rem-correction, the factor
//    back to the browser default, so every page carries its own correction (unset = 1).
// 2. Stylesheets from files inside chromeRootDirectories were written for chrome's root;
//    their rem is rescaled so they render the same on any page.

const CHROME_ROOT = 0.62;
// url()s and strings are matched only to be skipped; standalone numbers are the rem values
const REM = /url\([^)]*\)|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|(?<![\w.-])(-?(?:\d+\.?\d*|\.\d+))rem(?![\w-])/gi;
const ROOT_SELECTORS = new Set(['html', ':root']);

function rootFontSizeRatio(value) {
    const match = value.replace(/\s*!important$/, '').trim().match(/^(\d*\.?\d+)(rem|em|%|px)$/);
    if (!match) {
        return value.trim() === 'medium' ? 1 : null;
    }
    const amount = parseFloat(match[1]);
    return { rem: amount, em: amount, '%': amount / 100, px: amount / 16 }[match[2]];
}

function postcssRemCorrection({ chromeRootDirectories = [] } = {}) {
    const directories = chromeRootDirectories.map((directory) => fs.realpathSync(directory) + Path.sep);

    return {
        postcssPlugin: 'postcss-rem-correction',
        Once(root, { result }) {
            root.walkRules((rule) => {
                if (!rule.selectors.some((selector) => ROOT_SELECTORS.has(selector.trim()))) {
                    return;
                }
                let fontSize;
                rule.walkDecls('font-size', (declaration) => { fontSize = declaration; });
                const ratio = fontSize && rootFontSizeRatio(fontSize.value);
                if (ratio > 0) {
                    fontSize.cloneAfter({ prop: '--arches-rem-correction', value: String(1 / ratio) });
                }
            });

            const from = result.opts.from;
            if (!from || !directories.some((directory) => from.startsWith(directory))) {
                return;
            }
            root.walkDecls((declaration) => {
                declaration.value = declaration.value.replace(REM, (match, amount) => (amount === undefined
                    ? match
                    : `calc(${parseFloat((amount * CHROME_ROOT).toPrecision(6))}rem * var(--arches-rem-correction, 1))`
                ));
            });
        },
    };
}
postcssRemCorrection.postcss = true;

module.exports = { postcssRemCorrection };
