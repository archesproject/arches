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
                optimization: {
                    minimize: true,
                    minimizer: [
                        new TerserPlugin({
                            parallel: true,
                            terserOptions: {
                                compress: {
                                    drop_console: true,
                                },
                                mangle: true,
                            },
                        }),
                    ],
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