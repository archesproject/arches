const Path = require('path');
const Webpack = require('webpack');
const { merge } = require('webpack-merge');
const StylelintPlugin = require('stylelint-webpack-plugin');
const ESLintPlugin = require('eslint-webpack-plugin');

const commonWebpackConfig = require('./webpack.common.js');
const { WEBPACK_DEVELOPMENT_SERVER_PORT } = require('./webpack-meta-config.js');


module.exports = merge(commonWebpackConfig, {
    mode: 'development',
    devtool: 'inline-cheap-source-map',
    output: {
        chunkFilename: 'js/[name].chunk.js',
    },
    devServer: {
        historyApiFallback: true,
        client: {
            overlay: {
                errors: true,
                warnings: false,
            },
        },
        devMiddleware: {
            index: true,
            publicPath: '/static',
            writeToDisk: true,
        },
        port: WEBPACK_DEVELOPMENT_SERVER_PORT,
    },
    plugins: [
        new ESLintPlugin({
            extensions: [`js`, `jsx`],
        }),
        new Webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify('development'),
        }),
        new StylelintPlugin({
            files: Path.join('src', '**/*.s?(a|c)ss'),
        })
    ],
});