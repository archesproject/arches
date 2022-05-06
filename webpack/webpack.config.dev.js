const Path = require('path');
const Webpack = require('webpack');
const { merge } = require('webpack-merge');
const StylelintPlugin = require('stylelint-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const ESLintPlugin = require('eslint-webpack-plugin');

const commonWebpackConfig = require('./webpack.common.js');

ARCHES_CORE_PATH = Path.resolve(__dirname.split('/webpack')[0], './arches/app');

module.exports = merge(commonWebpackConfig, {
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
        //     fix: true,
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
                loader: `${ARCHES_CORE_PATH}/media/node_modules/babel-loader`,
                options: {
                    presets: ['@babel/preset-env'],
                    cacheDirectory: `${ARCHES_CORE_PATH}/media/node_modules/.cache/babel-loader`,
                }
            },
            {
                test: /\.s?css$/i,
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