/* eslint-disable */

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
                output: {
                    filename: 'js/[name].[chunkhash:8].js',
                    chunkFilename: 'js/[name].[chunkhash:8].chunk.js',
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