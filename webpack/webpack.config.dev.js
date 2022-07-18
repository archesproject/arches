const Path = require('path');
const Webpack = require('webpack');
const { merge } = require('webpack-merge');
const StylelintPlugin = require('stylelint-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const ESLintPlugin = require('eslint-webpack-plugin');

const commonWebpackConfig = require('./webpack.common.js');
const { PROJECT_PATH } = require('./webpack-metadata.js');


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
        port: 9001,
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
        }),
        new MiniCssExtractPlugin()
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
                test: /\.s?css$/i,
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