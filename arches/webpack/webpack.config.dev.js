/* eslint-disable */

const Path = require('path');
const Webpack = require('webpack');
const { merge } = require('webpack-merge');
const StylelintPlugin = require('stylelint-webpack-plugin');
const ESLintPlugin = require('eslint-webpack-plugin');

const commonWebpackConfigPromise = require('./webpack.common.js');

module.exports = () => {
    return new Promise((resolve, _reject) => {
        commonWebpackConfigPromise().then(commonWebpackConfig => {
            resolve(merge(commonWebpackConfig, {
                mode: 'development',
                // devtool: 'inline-source-map',
                output: {
                    chunkFilename: Path.join('js', '[name].chunk.js'),
                },
                devServer: {
                    historyApiFallback: true,
                    client: {
                        overlay: {
                            errors: true,
                            warnings: false,
                            runtimeErrors: (error) => {
                                if (error.message === "ResizeObserver loop limit exceeded") {
                                  return false;
                                }
                                return true;
                            },
                        },
                    },
                    hot: true,
                    host: '0.0.0.0',
                    devMiddleware: {
                        index: true,
                        publicPath: commonWebpackConfig.STATIC_URL,
                        writeToDisk: true,
                    },
                    port: commonWebpackConfig.WEBPACK_DEVELOPMENT_SERVER_PORT,
                },
                target: 'web',
                plugins: [
                    // new ESLintPlugin({
                    //     extensions: [`js`, `jsx`],
                    // }),
                    new Webpack.DefinePlugin({
                        'process.env.NODE_ENV': JSON.stringify('development'),
                    }),
                    new StylelintPlugin({
                        files: Path.join('src', '**/*.s?(a|c)ss'),
                    })
                ],
            }));
        });
    });
};