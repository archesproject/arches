/* eslint-disable */

const fs = require('fs');
const os = require('os');
const Path = require('path');
const postcss = require('postcss');

const { postcssRemCorrection } = require('./postcss-rem-correction');

const coreDirectory = fs.mkdtempSync(Path.join(os.tmpdir(), 'postcss-rem-correction-'));

function run(css, from = Path.join(os.tmpdir(), 'Other.vue')) {
    return postcss([postcssRemCorrection({ chromeRootDirectories: [coreDirectory] })]).process(css, { from }).css;
}

afterAll(() => {
    fs.rmSync(coreDirectory, { recursive: true, force: true });
});

describe('postcss-rem-correction', () => {
    it('adds the correction next to any html font size', () => {
        expect(run('html{font-size:.62rem}')).toBe('html{font-size:.62rem;--arches-rem-correction:1.6129032258064517}');
        expect(run('html, body { font-size: 62.5%; }')).toBe('html, body { font-size: 62.5%; --arches-rem-correction: 1.6; }');
        expect(run(':root { font-size: 10px }')).toBe(':root { font-size: 10px; --arches-rem-correction: 1.6 }');
    });

    it('ignores font sizes on other selectors and roots it cannot evaluate', () => {
        expect(run('body{font-size:1.4rem}')).toBe('body{font-size:1.4rem}');
        expect(run('html{font-size:var(--x)}')).toBe('html{font-size:var(--x)}');
    });

    it('rescales rem only in files inside a chrome root directory', () => {
        expect(run('.a{margin:-0.2rem 1rem;--b:2rem}', Path.join(fs.realpathSync(coreDirectory), 'nested', 'A.vue'))).toBe(
            '.a{margin:calc(-0.124rem * var(--arches-rem-correction, 1)) calc(0.62rem * var(--arches-rem-correction, 1));'
            + '--b:calc(1.24rem * var(--arches-rem-correction, 1))}',
        );
        expect(run('.a{margin:1rem}')).toBe('.a{margin:1rem}');
    });

    it('leaves rem inside variable names, urls and strings alone', () => {
        const css = '.a{margin:var(--size-2rem);background:url(icons/2rem.svg);content:"2rem"}';
        expect(run(css, Path.join(fs.realpathSync(coreDirectory), 'A.vue'))).toBe(css);
    });

    it('ignores a zero root font size', () => {
        expect(run('html{font-size:0rem}')).toBe('html{font-size:0rem}');
    });
});
