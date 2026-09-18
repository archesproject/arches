/* eslint-disable */

const fs = require('fs');
const os = require('os');
const Path = require('path');

const { buildFilepathLookup } = require('./build-filepath-lookup');

describe('buildFilepathLookup', () => {
    let fixtureRoot;

    beforeAll(() => {
        fixtureRoot = Path.join(fs.mkdtempSync(Path.join(os.tmpdir(), 'build-filepath-lookup-')), 'fixtureRoot');

        fs.mkdirSync(Path.join(fixtureRoot, 'nested'), { recursive: true });
        fs.writeFileSync(Path.join(fixtureRoot, 'entry.js'), '');
        fs.writeFileSync(Path.join(fixtureRoot, 'nested', 'widget.js'), '');
        fs.writeFileSync(Path.join(fixtureRoot, 'styles.css'), '');
        fs.writeFileSync(Path.join(fixtureRoot, 'nested', 'theme.scss'), '');
        fs.writeFileSync(Path.join(fixtureRoot, 'logo.png'), '');
        fs.writeFileSync(Path.join(fixtureRoot, '.DS_Store'), '');
    });

    afterAll(() => {
        fs.rmSync(Path.dirname(fixtureRoot), { recursive: true, force: true });
    });

    test('returns undefined for a directory that does not exist', () => {
        expect(buildFilepathLookup(Path.join(fixtureRoot, 'does-not-exist'))).toBeUndefined();
    });

    test('ignores dotfiles', () => {
        expect(Object.keys(buildFilepathLookup(fixtureRoot)).some((key) => key.includes('DS_Store'))).toBe(false);
    });

    test('maps .js files to an entry-point descriptor, recursing into subdirectories', () => {
        const lookup = buildFilepathLookup(fixtureRoot);

        expect(lookup['entry']).toEqual({
            import: Path.join(fixtureRoot, 'entry.js'),
            filename: 'fixtureRoot/[name].[contenthash].js',
        });
        expect(lookup['nested/widget']).toEqual({
            import: Path.join(fixtureRoot, 'nested', 'widget.js'),
            filename: 'fixtureRoot/[name].[contenthash].js',
        });
    });

    test('maps .css and .scss files under a css/ prefix', () => {
        const lookup = buildFilepathLookup(fixtureRoot);

        expect(lookup['css/styles']).toEqual({
            import: Path.join(fixtureRoot, 'styles.css'),
            filename: 'fixtureRoot/[name].[contenthash].css',
        });
        expect(lookup['css/nested/theme']).toEqual({
            import: Path.join(fixtureRoot, 'nested', 'theme.scss'),
            filename: 'fixtureRoot/[name].[contenthash].scss',
        });
    });

    test('maps other extensions to their raw file path, keyed under an optional static URL prefix', () => {
        const filepath = Path.join(fixtureRoot, 'logo.png');

        expect(buildFilepathLookup(fixtureRoot)['fixtureRoot/logo.png']).toBe(filepath);
        expect(buildFilepathLookup(fixtureRoot, '/static/')['/static/fixtureRoot/logo.png']).toBe(filepath);
    });

    // kept in sync by hand across projects; this project and arches core are the two known copies
    const thisFile = Path.resolve(__dirname, 'build-filepath-lookup.test.js');
    const otherCopies = ['test-modular-reports', 'arches']
        .map((project) => Path.resolve(__dirname, '..', '..', '..', project, 'webpack', 'webpack-utils', 'build-filepath-lookup.test.js'))
        .filter((copy) => copy !== thisFile && fs.existsSync(copy));

    test.skipIf(otherCopies.length === 0)('stays byte-identical to the other project copies of this file', () => {
        const thisContent = fs.readFileSync(thisFile, 'utf-8');
        const mismatches = otherCopies.filter((copy) => fs.readFileSync(copy, 'utf-8') !== thisContent);
        expect(mismatches).toEqual([]);
    });
});
