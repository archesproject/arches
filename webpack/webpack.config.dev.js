const Path = require('path');
const Webpack = require('../arches/app/media/node_modules/webpack');
const { merge } = require('../arches/app/media/node_modules/webpack-merge');
const StylelintPlugin = require('../arches/app/media/node_modules/stylelint-webpack-plugin');
const MiniCssExtractPlugin = require('../arches/app/media/node_modules/mini-css-extract-plugin');
const ESLintPlugin = require('../arches/app/media/node_modules/eslint-webpack-plugin');

const common = require('./webpack.common.js');

module.exports = merge(common, {
    mode: 'development',
    devtool: 'inline-cheap-source-map',
    output: {
        chunkFilename: 'js/[name].chunk.js',
    },
    devServer: {
        inline: true,
        hot: true,
    },
    plugins: [
        // new ESLintPlugin({
        //     extensions: [`js`, `jsx`],
        // }),
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
                loader: 'babel-loader',
                options: {
                    presets: ['@babel/preset-env']
                }
            },
            {
                test: /\.s?css$/i,
                use: [
                    {
                        'loader': MiniCssExtractPlugin.loader,
                    },
                    {
                        'loader': 'css-loader',
                    },
                    {
                        'loader': 'postcss-loader',
                    },
                    {
                        'loader': 'sass-loader',
                    }
                ],
            },
        ],
    },
});