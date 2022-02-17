const Path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');

// const webpack = require('webpack');
const path = require('path');
const fs = require('fs');

const fileNames = function(path, outer_acc) {
    return fs.readdirSync(path).reduce((acc, v) => {
        const lastThreeCharacters = v.slice(v.length - 3);
    
        if (lastThreeCharacters === '.js') {
            var foo = (path + '/' + v).slice(5)
            return { ...acc, [foo]: `./js/${foo}` };
        }
        else {
            console.log(path + '/' + v)
            return fileNames(path + '/' + v, acc);
        }
    }, outer_acc);
};


var bar = fileNames('./js', {});

// console.log("hi", fileNames)

// var glob = require('glob');
// var path = require('path');

// const fs = require("fs")
// const path = require("path")

// const getAllFiles = function (dirPath, arrayOfFiles) {
//     var files = fs.readdirSync(dirPath)

//     arrayOfFiles = arrayOfFiles || []

//     files.forEach(function (file) {
//         if (fs.statSync(dirPath + "/" + file).isDirectory()) {
//             arrayOfFiles = getAllFiles(dirPath + "/" + file, arrayOfFiles)
//         } else {
//             arrayOfFiles.push(path.join(__dirname, dirPath, "/", file))
//         }
//     })

//     return arrayOfFiles
// }

// var foo = getAllFiles(Path.join(__dirname, '../js'))

// var bar = {};

// foo.forEach(function(path) {
//     var relativePathName = path.replace(Path.join(__dirname, '../js'), '')
//     bar[relativePathName] = path;
// });

console.log("HI", bar)

module.exports = {
    // entry: glob.sync('./js/**.js').reduce(function(obj, el) {
    //     obj[path.parse(el).name] = el;
    //     return obj;
    // }, {}),
    entry: bar,
    output: {
        path: Path.join(__dirname, '../build'),
        filename: 'js/[name]',
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