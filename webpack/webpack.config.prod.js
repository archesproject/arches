const Webpack = require('webpack');
const { merge } = require('webpack-merge');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const common = require('./webpack.common.js');
const { PROJECT_PATH } = require('./webpack-paths.js');


module.exports = merge(common, {
    mode: 'production',
    devtool: false,
    bail: true,
    output: {
        chunkFilename: 'js/[name].chunk.js',
    },
    plugins: [
        new Webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify('production'),
        }),
        new MiniCssExtractPlugin(),
    ],
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                loader: `${PROJECT_PATH}/media/node_modules/babel-loader`,
                options: {
                    presets: ['@babel/preset-env'],
                    cacheDirectory: `${PROJECT_PATH}/media/node_modules/.cache/babel-loader`,
                }
            },
            {
                test: /\.s?css/i,
                use: [
                    {
                        'loader': MiniCssExtractPlugin.loader,
                    },
                    {
                        'loader': `${PROJECT_PATH}/media/node_modules/css-loader`,
                    },
                    {
                        'loader': `${PROJECT_PATH}/media/node_modules/postcss-loader`,
                    },
                    {
                        'loader': `${PROJECT_PATH}/media/node_modules/sass-loader`,
                    }
                ],
            },
        ],
    },
});