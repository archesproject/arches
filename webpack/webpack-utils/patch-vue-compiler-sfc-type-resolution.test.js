/* eslint-disable */

const fs = require('fs');
const Path = require('path');

const vueCompilerSfc = require('vue/compiler-sfc');
const { requireVueLoaderWithTypeResolutionPatch } = require('./patch-vue-compiler-sfc-type-resolution');

requireVueLoaderWithTypeResolutionPatch();  // must patch compileScript before reading it off below

const { parse, compileScript } = vueCompilerSfc;

function findVueFiles(directory) {
    if (!fs.existsSync(directory)) {
        return [];
    }
    return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
        const entryPath = Path.join(directory, entry.name);
        return entry.isDirectory() ? findVueFiles(entryPath) : (entry.name.endsWith('.vue') ? [entryPath] : []);
    });
}

const webpackMetadataPath = Path.join(__dirname, '..', '..', 'frontend_configuration', 'webpack-metadata.json');
const { ARCHES_APPLICATIONS, ARCHES_APPLICATIONS_PATHS } = fs.existsSync(webpackMetadataPath)
    ? JSON.parse(fs.readFileSync(webpackMetadataPath, 'utf-8'))
    : { ARCHES_APPLICATIONS: [], ARCHES_APPLICATIONS_PATHS: {} };  // this project's own manage.py hasn't generated it yet

describe('patch-vue-compiler-sfc-type-resolution', () => {
    for (const archesApplication of ARCHES_APPLICATIONS) {
        const vueFiles = findVueFiles(Path.join(ARCHES_APPLICATIONS_PATHS[archesApplication], 'src'));

        test.skipIf(vueFiles.length === 0)(`resolves @ alias type imports in every ${archesApplication} .vue file`, () => {
            const failures = vueFiles
                .map((filename) => {
                    const { descriptor } = parse(fs.readFileSync(filename, 'utf-8'), { filename });
                    if (!descriptor.script && !descriptor.scriptSetup) {
                        return null;
                    }
                    try {
                        compileScript(descriptor, { id: filename });
                        return null;
                    } catch (error) {
                        return `${filename}: ${error.message}`;
                    }
                })
                .filter(Boolean);

            expect(failures).toEqual([]);
        });
    }

    // kept in sync by hand across projects; this project and arches core are the two known copies
    const thisFile = Path.resolve(__dirname, 'patch-vue-compiler-sfc-type-resolution.js');
    const otherCopies = ['test-modular-reports', 'arches']
        .map((project) => Path.resolve(__dirname, '..', '..', '..', project, 'webpack', 'webpack-utils', 'patch-vue-compiler-sfc-type-resolution.js'))
        .filter((copy) => copy !== thisFile && fs.existsSync(copy));

    test.skipIf(otherCopies.length === 0)('stays byte-identical to the other project copies of this file', () => {
        const thisContent = fs.readFileSync(thisFile, 'utf-8');
        const mismatches = otherCopies.filter((copy) => fs.readFileSync(copy, 'utf-8') !== thisContent);
        expect(mismatches).toEqual([]);
    });
});
