const Path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');

const fs = require('fs');

const fileNames = function(path, outer_acc) {
    return fs.readdirSync(path).reduce((acc, v) => {
        const lastThreeCharacters = v.slice(v.length - 3);
    
        if (lastThreeCharacters === '.js') {
            var foo = (path + '/' + v).slice(5)
            return { ...acc, [foo]: { 'import': `./js/${foo}`, 'filename': `./js/${foo}` } };
        }
        else {
            return fileNames(path + '/' + v, acc);
        }
    }, outer_acc);
};


var bar = fileNames('./js', {});

var baz = Object.keys(bar).reduce((acc, key) => {
    var foo = (key).slice(0, key.length - 3)
    acc[foo] = Path.resolve(__dirname, '../js', key)
    return acc;
}, {});


// images
const fooFileNames = function(path, outer_acc) {
    return fs.readdirSync(path).reduce((acc, v) => {
        if (fs.lstatSync(path + '/' + v).isDirectory() ) {
            return fooFileNames(path + '/' + v, acc);
        }
        else {
            var foo = (path + '/' + v).slice(6)
            return { ...acc, [foo]: { 'import': `./img/${foo}`, 'filename': `./img/${foo}` } };
        }

    }, outer_acc);
};


var bar_img = fooFileNames('./img', {});

var baz_img = Object.keys(bar).reduce((acc, key) => {
    var foo = (key).slice(0, key.length - 4)
    acc[foo] = Path.resolve(__dirname, '../img', key)
    return acc;
}, {});

// const foo_plugins = fileNames('./plugins', {})
// var bar_plugins = Object.keys(foo_plugins).reduce((acc, key) => {
//     var foo = (key).slice(0, key.length - 3)
//     acc[foo] = Path.resolve(__dirname, '../js', key)
//     return acc;
// }, {});
console.log("HI", bar_img);
// console.log("HI", baz)

module.exports = {
    entry: {
        ...bar,
        // ...bar_img,
        'arches': { 'import': './css/arches.scss', 'filename': './css/arches.scss' },
    },
    output: {
        path: Path.join(__dirname, '../build'),
        filename: '[name]',
        publicPath: '/foo/',
    },
    optimization: {
        // splitChunks: {
        //     chunks: 'all',
        //     cacheGroups: {
        //         vendor: {
        //             test: /[\\/]node_modules[\\/]/,
        //             name(module) {
        //                 // Extracts node_modules to separate packages
        //                 const packagePath = module.context.match(
        //                     /[\\/]node_modules[\\/](.*?)([\\/]|$)/
        //                 );

        //                 let packageName = null;

        //                 if (packagePath) { 
        //                     packageName = packagePath[1]; 
        //                     return `js/npm.${packageName.replace("@", "")}.js`;
        //                 }

        //             }
        //         },
        //     }
        // },
    },
    plugins: [
        new CleanWebpackPlugin(),
        new CopyWebpackPlugin({ patterns: [{ from: Path.resolve(__dirname, '../public'), to: 'public' }] }),
        new HtmlWebpackPlugin({
            template: Path.resolve(__dirname, '../../templates/index.htm'),
        }),
        new BundleTracker({ filename: './webpack-stats.json' }),
    ],
    resolve: {
        // moduleDirectories: [__dirname, "node_modules"],
        alias: {
            ...baz,
            'arches': Path.resolve(__dirname, '../templates', 'javascript.htm'),
            'resource-edit-history-data': Path.resolve(__dirname, '../templates/views/resource', 'edit-log.htm'),
            'plugin-data': Path.resolve(__dirname, '../templates/views', 'plugin.htm'),
            'mobile-survey-manager-data': Path.resolve(__dirname, '../templates/views', 'mobile-survey-designer.htm'),
            'graph-settings-data': Path.resolve(__dirname, '../templates/views/graph', 'graph-settings.htm'),
            'graph-functions-data': Path.resolve(__dirname, '../templates/views/graph', 'function-manager.htm'),
            'graph-base-data': Path.resolve(__dirname, '../templates/views/graph', 'graph-base.htm'),
            'function-templates': Path.resolve(__dirname, '../templates', 'javascript.htm'),
            'component-templates': Path.resolve(__dirname, '../templates', 'javascript.htm'),
            'widgets': Path.resolve(__dirname, '../templates', 'javascript.htm'),
            'view-data': Path.resolve(__dirname, '../templates', 'base-manager.htm'),
            'graph-manager-data': Path.resolve(__dirname, '../templates/views', 'graph.htm'),
            'turf': Path.resolve(__dirname, '../node_modules/@turf/turf', 'turf.min'),
            'plugins/knockout-select2': Path.resolve(__dirname, '../plugins', 'knockout-select2.js'),
            'jquery-validate': Path.resolve(__dirname, '../node_modules/jquery-validation/dist', 'jquery.validate.min'),
            'jquery-ui/draggable': Path.resolve(__dirname, '../node_modules/jqueryui', 'jquery-ui.min.js'),
            'jquery-ui/sortable': Path.resolve(__dirname, '../node_modules/jqueryui', 'jquery-ui.min.js'),
            // 'require': Path.resolve(__dirname, '../node_modules/requirejs', 'require.js'),
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
                test: /\.htm$/i,
                loader: "html-loader",
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