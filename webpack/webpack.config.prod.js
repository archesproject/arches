/* eslint-disable */

const Path = require('path');
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
                    minimizeOptions: {
                        javascript: {
                            compress: {
                                drop_console: true,
                            },
                            mangle: true,
                            keep_classnames: true,
                            keep_fnames: true,
                        },
                    },
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