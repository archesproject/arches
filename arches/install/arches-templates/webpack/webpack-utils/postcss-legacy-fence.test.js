/* eslint-disable */

const postcss = require('postcss');

const { postcssLegacyFence } = require('./postcss-legacy-fence');

const FENCE = ':where(:not([data-arches-core], [data-arches-core] *))';

function run(css) {
    return postcss([postcssLegacyFence({ boundary: '[data-arches-core]' })]).process(css, { from: undefined }).css;
}

describe('postcss-legacy-fence', () => {
    it('fences the subject of every selector, including the root and inside conditional groups', () => {
        expect(run('label, .a > .b{x:1}html{x:2}@media print{a:hover{x:3}}')).toBe(
            `label${FENCE}, .a > .b${FENCE}{x:1}html${FENCE}{x:2}@media print{a:hover${FENCE}{x:3}}`,
        );
    });

    it('keeps pseudo-elements last, ignoring colons inside parentheses and attribute values', () => {
        expect(run('.a::before{x:1}.b:after{x:1}::selection{x:1}.c:not(.d)::-webkit-scrollbar:hover{x:1}[e="f::g"]{x:1}')).toBe(
            `.a${FENCE}::before{x:1}.b${FENCE}:after{x:1}${FENCE}::selection{x:1}`
            + `.c:not(.d)${FENCE}::-webkit-scrollbar:hover{x:1}[e="f::g"]${FENCE}{x:1}`,
        );
    });

    it('leaves keyframes alone', () => {
        expect(run('@keyframes k{from{opacity:0}to{opacity:1}}')).toBe('@keyframes k{from{opacity:0}to{opacity:1}}');
    });
});
