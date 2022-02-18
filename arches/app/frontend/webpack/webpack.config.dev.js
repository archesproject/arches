const Path = require('path');
const Webpack = require('webpack');
const { merge } = require('webpack-merge');
const StylelintPlugin = require('stylelint-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const ESLintPlugin = require('eslint-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

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
        new HtmlWebpackPlugin({
            template: Path.resolve(__dirname, '../../templates/index.htm')
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
                // include: Path.resolve(__dirname, '../../media/js'),
                loader: 'babel-loader',
                // options: {
                //     presets: ['@babel/preset-env']
                // }
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