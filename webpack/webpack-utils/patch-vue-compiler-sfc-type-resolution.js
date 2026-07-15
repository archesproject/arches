/* eslint-disable */

const Path = require('path');

// vue's compiler can't find a tsconfig.json for a regular (non-editable) pip install, so
// defineProps<T>() type resolution breaks. We feed it a fake one in memory using its own fs
// option. Don't move this below the vue-loader require. vue-loader grabs compileScript once when
// it loads and never looks again.
function requireVueLoaderWithTypeResolutionPatch() {
    const ts = require('typescript');
    const vueSingleFileComponentCompiler = require('vue/compiler-sfc');

    if (typeof vueSingleFileComponentCompiler.compileScript !== 'function') {
        throw new Error(
            'vue/compiler-sfc.compileScript is not a function; the installed vue/vue-loader ' +
            'version may no longer support this patch and it needs to be revisited.'
        );
    }

    const originalCompileScript = vueSingleFileComponentCompiler.compileScript;
    vueSingleFileComponentCompiler.compileScript = function (descriptor, options) {
        const tsConfigPath = Path.join(global.SITE_PACKAGES_DIRECTORY, 'tsconfig.json');

        const archesApplicationPathAliases = [
            Path.join(global.APP_ROOT, 'src') + '/*',
            ...global.ARCHES_APPLICATIONS.map((archesApplication) => (
                Path.join(global.ARCHES_APPLICATIONS_PATHS[archesApplication], 'src') + '/*'
            )),
            Path.join(global.ROOT_DIR, 'app', 'src') + '/*',
        ];

        const virtualTsconfigContent = JSON.stringify({
            compilerOptions: {
                moduleResolution: 'bundler',
                module: 'ESNext',
                paths: { '@/*': archesApplicationPathAliases },
            },
        });

        const virtualFileSystem = {
            fileExists(filePath) {
                if (filePath === tsConfigPath) {
                    return true;
                }
                return ts.sys.fileExists(filePath);
            },
            readFile(filePath, encoding) {
                if (filePath === tsConfigPath) {
                    return virtualTsconfigContent;
                }
                return ts.sys.readFile(filePath, encoding);
            },
            realpath: ts.sys.realpath,
        };

        return originalCompileScript(descriptor, { ...options, fs: virtualFileSystem });
    };

    return require('vue-loader');
}

module.exports = { requireVueLoaderWithTypeResolutionPatch };
