/* eslint-disable */

const Path = require('path');
const TerserPlugin = require("terser-webpack-plugin");
const Webpack = require('webpack');
const { merge } = require('webpack-merge');

const commonWebpackConfigPromise = require('./webpack.common.js');

module.exports = () => {
    return new Promise((resolve, _reject) => {
        commonWebpackConfigPromise().then(commonWebpackConfig => {
            resolve(merge(commonWebpackConfig, {
                mode: 'production',
                devtool: false,
                bail: true,
                parallelism: 1,
                optimization: {
                    minimizer: [
                        new TerserPlugin({
                            parallel: 3,
                            terserOptions: {
                                mangle: { keep_fnames: true },
                            },
                        }),
                    ],
                },
                output: {
                    filename: Path.join('js', '[name].[chunkhash:8].js'),
                    chunkFilename: Path.join('js', '[name].[chunkhash:8].chunk.js'),
                },
                plugins: [
                    new Webpack.DefinePlugin({
                        'process.env.NODE_ENV': JSON.stringify('production'),
                    }),
                ],
            }));
        });
    })
};