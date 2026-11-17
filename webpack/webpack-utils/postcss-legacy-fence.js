/* eslint-disable */

// Fences the Arches chrome's legacy stylesheets off from core Vue components: each selector's
// subject gets :where(:not(boundary, boundary *)), so legacy rules stop matching at any element
// matching `boundary`. :where adds no specificity and needs no @scope, so the cascade is unchanged
// and older browsers (Firefox ESR, Safari < 17.4) keep working. Pseudo-elements stay last.

const PSEUDO_ELEMENT = /^(::|:(before|after|first-line|first-letter)\b|:-(webkit|moz|ms|o)-)/i;
const KEYFRAMES = /keyframes$/i;

function subjectEnd(selector) {
    let depth = 0;
    let quote = null;
    for (let i = 0; i < selector.length; i++) {
        const character = selector[i];
        if (character === '\\') {
            i++;
        } else if (quote) {
            if (character === quote) quote = null;
        } else if (character === '"' || character === "'") {
            quote = character;
        } else if (character === '(' || character === '[') {
            depth++;
        } else if (character === ')' || character === ']') {
            depth--;
        } else if (character === ':' && depth === 0 && PSEUDO_ELEMENT.test(selector.slice(i))) {
            return i;
        }
    }
    return selector.length;
}

function postcssLegacyFence({ boundary }) {
    const fence = `:where(:not(${boundary}, ${boundary} *))`;
    return {
        postcssPlugin: 'postcss-legacy-fence',
        Once(root) {
            root.walkRules((rule) => {
                if (rule.parent.type === 'atrule' && KEYFRAMES.test(rule.parent.name)) {
                    return;
                }
                rule.selectors = rule.selectors.map((selector) => {
                    const end = subjectEnd(selector);
                    return `${selector.slice(0, end)}${fence}${selector.slice(end)}`;
                });
            });
        },
    };
}
postcssLegacyFence.postcss = true;

module.exports = { postcssLegacyFence };
