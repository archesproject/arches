const Path = require('path');
const Webpack = require('webpack');
const { merge } = require('webpack-merge');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const common = require('./webpack.common.js');

ARCHES_CORE_PATH = Path.resolve(__dirname.split('/webpack')[0], './arches/app');

module.exports = merge(common, {
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
        new MiniCssExtractPlugin({
            filename: 'css/app-[contenthash].css',
        }),
    ],
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                loader: `${ARCHES_CORE_PATH}/media/node_modules/babel-loader`,
                options: {
                    presets: ['@babel/preset-env'],
                    cacheDirectory: `${ARCHES_CORE_PATH}/media/node_modules/.cache/babel-loader`,
                }
            },
            {
                test: /\.s?css/i,
                use: [
                    {
                        'loader': MiniCssExtractPlugin.loader,
                    },
                    {
                        'loader': `${ARCHES_CORE_PATH}/media/node_modules/css-loader`,
                    },
                    {
                        'loader': `${ARCHES_CORE_PATH}/media/node_modules/postcss-loader`,
                    },
                    {
                        'loader': `${ARCHES_CORE_PATH}/media/node_modules/sass-loader`,
                    }
                ],
            },
        ],
    },
});