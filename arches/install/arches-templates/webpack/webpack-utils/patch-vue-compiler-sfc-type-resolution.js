/* eslint-disable */

const fs = require('fs');
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

    const frontendConfigurationDirectory = Path.join(__dirname, '..', '..', 'frontend_configuration');
    const { compilerOptions: { paths: tsconfigPathsRelativeToFrontendConfiguration } } = JSON.parse(
        fs.readFileSync(Path.join(frontendConfigurationDirectory, 'tsconfig-paths.json'), 'utf-8')
    );

    const archesApplicationPathAliases = Object.fromEntries(
        Object.entries(tsconfigPathsRelativeToFrontendConfiguration).map(([alias, relativePaths]) => [
            alias,
            relativePaths.map((relativePath) => Path.resolve(frontendConfigurationDirectory, relativePath)),
        ])
    );

    const virtualTsconfigContent = JSON.stringify({
        compilerOptions: {
            moduleResolution: 'bundler',
            module: 'ESNext',
            paths: archesApplicationPathAliases,
        },
    });

    const originalCompileScript = vueSingleFileComponentCompiler.compileScript;
    vueSingleFileComponentCompiler.compileScript = function (descriptor, options) {
        const tsConfigPath = Path.join(global.SITE_PACKAGES_DIRECTORY, 'tsconfig.json');

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
