/* eslint-disable */

const fs = require('fs');
const Path = require('path');

// We answer every tsconfig.json lookup vue's type resolver makes with our own config, so it
// never walks into some dependency's own (possibly missing/broken) tsconfig.json chain.
// Don't move this below the vue-loader require -- it only patches compileScript once, on load.
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
        const virtualFileSystem = {
            ...ts.sys,
            fileExists: (filePath) => Path.basename(filePath) === 'tsconfig.json' || ts.sys.fileExists(filePath),
            readFile: (filePath, encoding) => Path.basename(filePath) === 'tsconfig.json' ? virtualTsconfigContent : ts.sys.readFile(filePath, encoding),
        };

        return originalCompileScript(descriptor, { ...options, fs: virtualFileSystem });
    };

    return require('vue-loader');
}

module.exports = { requireVueLoaderWithTypeResolutionPatch };
