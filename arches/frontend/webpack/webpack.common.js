const Path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
    entry: {
        app: Path.resolve(__dirname, '../src/scripts/index.js'),
    },
    output: {
        path: Path.join(__dirname, '../build'),
        filename: 'js/[name].js',
        publicPath: '/foo/',
    },
    optimization: {
        splitChunks: {
            chunks: 'all',
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name(module) {
                        // Extracts node_modules to separate packages
                        const packageName = module.context.match(
                            /[\\/]node_modules[\\/](.*?)([\\/]|$)/
                        )[1];
                        return `npm.${packageName.replace("@", "")}`;
                    }
                },
            }
        },
    },
    plugins: [
        new CleanWebpackPlugin(),
        new CopyWebpackPlugin({ patterns: [{ from: Path.resolve(__dirname, '../public'), to: 'public' }] }),
        new HtmlWebpackPlugin({
            template: Path.resolve(__dirname, '../src/index.html'),
        }),
        new BundleTracker({ filename: './webpack-stats.json' }),
    ],
    resolve: {
        alias: {
            '~': Path.resolve(__dirname, '../src'),
        },
    },
    module: {
        rules: [
            {
                test: /\.mjs$/,
                include: /node_modules/,
                type: 'javascript/auto',
            },
            {
                test: /\.(ico|jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2)(\?.*)?$/,
                use: {
                    loader: 'file-loader',
                    options: {
                        name: '[path][name].[ext]',
                    },
                },
            },
        ],
    },
};