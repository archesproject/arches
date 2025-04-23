/* eslint-disable */

const Path = require('path');
const Webpack = require('webpack');
const { merge } = require('webpack-merge');
const StylelintPlugin = require('stylelint-webpack-plugin');

const commonWebpackConfigPromise = require('./webpack.common.js');

class WatchArchesUrlsPlugin {
    constructor(watchPath) {
        this.watchPath = watchPath;
    }

    apply(compiler) {
        compiler.hooks.afterCompile.tap('WatchArchesUrlsPlugin', (compilation) => {
            if (
                compilation.fileDependencies &&
                typeof compilation.fileDependencies.add === 'function'
            ) {
                compilation.fileDependencies.add(this.watchPath);
            }
            else if (Array.isArray(compilation.fileDependencies)) {
                compilation.fileDependencies.push(this.watchPath);
            }
        });
    }
}

module.exports = () => {
    return new Promise((resolve) => {
        commonWebpackConfigPromise().then(commonWebpackConfig => {
            resolve(merge(commonWebpackConfig, {
                mode: 'development',
                cache: {
                    type: 'filesystem',
                    buildDependencies: {
                        config: [__filename],
                    },
                },
                devtool: 'inline-source-map',
                target: 'web',
                devServer: {
                    historyApiFallback: true,
                    client: { overlay: false },
                    hot: true,
                    host: '0.0.0.0',
                    port: commonWebpackConfig.WEBPACK_DEVELOPMENT_SERVER_PORT,
                    devMiddleware: {
                        index: true,
                        writeToDisk: true,
                    },
                },
                watchOptions: {
                    ignored: '**/node_modules',
                },
                stats: {
                    modules: false,
                },
                plugins: [
                    new Webpack.DefinePlugin({
                        'process.env.NODE_ENV': JSON.stringify('development'),
                    }),
                    new StylelintPlugin({
                        files: Path.join('src', '**/*.s?(a|c)ss'),
                    }),
                    new WatchArchesUrlsPlugin(Path.join(__dirname, "..", "frontend_configuration", 'urls.json')),
                ],
            }));
        });
    });
};
