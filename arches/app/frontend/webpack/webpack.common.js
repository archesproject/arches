const Path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');

const fs = require('fs');

const fileNames = function(path, outer_acc) {
    return fs.readdirSync(path).reduce((acc, v) => {
        if (fs.lstatSync(path + '/' + v).isDirectory() ) {
            return fileNames(path + '/' + v, acc);
        }
        else {
            var foo = (path + '/' + v).slice(12)
            var bar = foo.slice(0, foo.length - 3)
            // console.log(bar)
            return { ...acc, [bar]: { 'import': `${path}/${v}`, 'filename': `js/[name].js` } };
        }
    }, outer_acc);
};


var bar = fileNames('../media/js', {});

var baz = Object.keys(bar).reduce((acc, key) => {
    // var foo = (key).slice(0, key.length - 3)
    // console.log(key)
    acc[key] = Path.resolve(__dirname, '../../media/js', key)
    return acc;
}, {});


// images
const fooFileNames = function(path, outer_acc) {
    return fs.readdirSync(path).reduce((acc, v) => {
        if (fs.lstatSync(path + '/' + v).isDirectory() ) {
            return fooFileNames(path + '/' + v, acc);
        }
        else {
            var foo = (path + '/' + v).slice(13)
            // console.log("()", foo)
            acc[foo] = { 'import': Path.relative(__dirname, `${path}/${v}`).slice(3), 'filename': `img/[name]` };

            return acc;
        }

    }, outer_acc);
};


var bar_img = fooFileNames(Path.relative(__dirname, 'media/img'), {});

// var baz_img = Object.keys(bar).reduce((acc, key) => {
//     var foo = (key).slice(0, key.length - 4)
//     acc[foo] = Path.resolve(__dirname, '../img', key)
//     return acc;
// }, {});


// css files
const quxFileNames = function(path, outer_acc) {
    return fs.readdirSync(path).reduce((acc, v) => {
        if (fs.lstatSync(path + '/' + v).isDirectory() ) {
            return quxFileNames(path + '/' + v, acc);
        }
        else {
            var foo = (path + '/' + v).slice(13)
            return { ...acc, [foo]: { 'import': `../media/css/${foo}`, 'filename': `./css/${foo}` } };
        }

    }, outer_acc);
};

qux_css = quxFileNames('../media/css', {})


//

const quuxFileNames = function(path, outer_acc) {
    return fs.readdirSync(path).reduce((acc, v) => {
        if (fs.lstatSync(path + '/' + v).isDirectory() ) {
            return quuxFileNames(path + '/' + v, acc);
        }
        else {
            var foo = (path + '/' + v).slice(13)
            
            acc.push(new HtmlWebpackPlugin({
                template: `../templates/${foo}`, // relative path to the HTML files
                filename: `templates/${foo}`, // output HTML files
                // chunks: [`${foo}`] // respective JS files
            }));
            return acc;
            // return { ...acc, [foo]: { 'import': `../templates/${foo}` } };
        }

    }, outer_acc);
};

var quux = quuxFileNames('../templates', [])

// qux = Object.keys(qux_css).reduce((acc, key) => {
//     var foo = (key).slice(0, key.length - 4)
//     acc[foo] = Path.resolve(__dirname, '../css', key)
//     return acc;
// }, {});

// const foo_plugins = fileNames('./plugins', {})
// var bar_plugins = Object.keys(foo_plugins).reduce((acc, key) => {
//     var foo = (key).slice(0, key.length - 3)
//     acc[foo] = Path.resolve(__dirname, '../js', key)
//     return acc;
// }, {});
// console.log("HI", qux_css);
// console.log("HI", bar_img)


var aaa = {
    ...bar,
    // ...bar_img,
}

console.log(bar)

module.exports = {
    entry: aaa,
    output: {
        path: Path.resolve(__dirname, '../../media/build'),
        publicPath: '/foo/',
    },
    // optimization: {
    //     splitChunks: {
    //         chunks: 'all',
    //         cacheGroups: {
    //             vendor: {
    //                 test: /[\\/]node_modules[\\/]/,
    //                 name(module) {
    //                     // Extracts node_modules to separate packages
    //                     const packagePath = module.context.match(
    //                         /[\\/]node_modules[\\/](.*?)([\\/]|$)/
    //                     );

    //                     let packageName = null;

    //                     if (packagePath) { 
    //                         packageName = packagePath[1]; 
    //                         return `js/npm.${packageName.replace("@", "")}`;
    //                     }

    //                 }
    //             },
    //         }
    //     },
    // },
    plugins: [
        new CleanWebpackPlugin(),
        new CopyWebpackPlugin({ patterns: [{ from: Path.resolve(__dirname, '../public'), to: 'public' }, {from: Path.resolve(__dirname, '../../media/img'), to: 'img'} ] }),
        // new HtmlWebpackPlugin({
        //     template: Path.resolve(__dirname, '../../templates/index.htm'),
        // }),
        new BundleTracker({ filename: './webpack-stats.json' }),
    ].concat(quux),
    resolve: {
        modules: [Path.resolve(__dirname, '../../media/node_modules')],
        alias: {
            ...baz,
            // ...qux,
            'arches': Path.resolve(__dirname, '../../templates', 'javascript.htm'),
            'report-templates': Path.resolve(__dirname, '../../templates', 'javascript.htm'),
            'card-components': Path.resolve(__dirname, '../../templates', 'javascript.htm'),
            'file-renderers': Path.resolve(__dirname, '../../templates', 'javascript.htm'),
            'resource-edit-history-data': Path.resolve(__dirname, '../../templates/views/resource', 'edit-log.htm'),
            'plugin-data': Path.resolve(__dirname, '../../templates/views', 'plugin.htm'),
            'mobile-survey-manager-data': Path.resolve(__dirname, '../../templates/views', 'mobile-survey-designer.htm'),
            'graph-settings-data': Path.resolve(__dirname, '../../templates/views/graph', 'graph-settings.htm'),
            'graph-functions-data': Path.resolve(__dirname, '../../templates/views/graph', 'function-manager.htm'),
            'graph-base-data': Path.resolve(__dirname, '../../templates/views/graph', 'graph-base.htm'),
            'function-templates': Path.resolve(__dirname, '../../templates', 'javascript.htm'),
            'component-templates': Path.resolve(__dirname, '../../templates', 'javascript.htm'),
            'geocoder-templates': Path.resolve(__dirname, '../../templates', 'javascript.htm'),
            'search-components': Path.resolve(__dirname, '../../templates', 'javascript.htm'),
            'datatype-config-components': Path.resolve(__dirname, '../../templates', 'javascript.htm'),
            'widgets': Path.resolve(__dirname, '../../templates', 'javascript.htm'),
            'view-data': Path.resolve(__dirname, '../../templates', 'base-manager.htm'),
            'profile-manager-data': Path.resolve(__dirname, '../../templates/views', 'user-profile-manager.htm'),
            'graph-manager-data': Path.resolve(__dirname, '../../templates/views', 'graph.htm'),
            'graph-designer-data': Path.resolve(__dirname, '../../templates/views', 'graph-designer.htm'),
            'map-layer-manager-data': Path.resolve(__dirname, '../../templates/views', 'map-layer-manager.htm'),
            'resource-editor-data': Path.resolve(__dirname, '../../templates/views/resource', 'editor.htm'),
            // 'turf': Path.resolve(__dirname, '../node_modules/@turf/turf', 'turf.min'),
            'plugins/knockout-select2': Path.resolve(__dirname, '../plugins', 'knockout-select2.js'),
            // 'jquery-validate': Path.resolve(__dirname, '../node_modules/jquery-validation/dist', 'jquery.validate.min'),
            'jquery-ui/draggable': Path.resolve(__dirname, '../node_modules/jqueryui', 'jquery-ui.min.js'),
            'jquery-ui/sortable': Path.resolve(__dirname, '../node_modules/jqueryui', 'jquery-ui.min.js'),
            // 'underscore': Path.resolve(__dirname, '../node_modules/underscore', 'underscore-min.js'),
            // 'knockout': Path.resolve(__dirname, '../node_modules/knockout/build/output/knockout-latest'),
            // 'knockout-mapping': Path.resolve(__dirname, '../node_modules/knockout-mapping/dist/', 'knockout.mapping.min'),
            // 'jquery': Path.resolve(__dirname, '../node_modules/jquery-migrate/dist/', 'jquery-migrate.min'),
            // 'jquery-ui': Path.resolve(__dirname, '../node_modules/jqueryui/jquery-ui.min'),
            // 'select2': Path.resolve(__dirname, '../node_modules/select2/select2'),
            // 'moment': Path.resolve(__dirname, '../node_modules/moment/min/', 'moment.min'),
            // 'backbone': Path.resolve(__dirname, '../node_modules/backbone/backbone-min'),
            // 'bootstrap': Path.resolve(__dirname, '../node_modules/bootstrap/dist/js/', 'bootstrap.min'),
            // 'uuid': Path.resolve(__dirname, '../node_modules/uuidjs/dist/', 'uuid.core'),
            // 'js-cookie': Path.resolve(__dirname, '../node_modules/js-cookie/src/', 'js.cookie'),
            // 'dropzone': Path.resolve(__dirname, '../node_modules/dropzone/dist/min/', 'dropzone-amd-module.min'),
            // 'jqtree': Path.resolve(__dirname, '../node_modules/jqtree/', 'tree.jquery'),
            // 'cytoscape': Path.resolve(__dirname, '../node_modules/cytoscape/dist/', 'cytoscape.min'),
            // 'cytoscape-cola': Path.resolve(__dirname, '../node_modules/cytoscape-cola/cytoscape-cola'),
            // 'webcola': Path.resolve(__dirname, '../node_modules/webcola/WebCola/', 'cola.min'),
            // 'geohash': Path.resolve(__dirname, '../node_modules/latlon-geohash/latlon-geohash'),
            // 'chosen': Path.resolve(__dirname, '../node_modules/chosen-js/', 'chosen.jquery.min'),
            // 'leaflet': Path.resolve(__dirname, '../node_modules/leaflet/dist/leaflet'),
            // 'leaflet-iiif': Path.resolve(__dirname, '../node_modules/leaflet-iiif/leaflet-iiif'),
            // 'leaflet-draw': Path.resolve(__dirname, '../node_modules/leaflet-draw/dist/', 'leaflet.draw'),
            // 'leaflet-fullscreen': Path.resolve(__dirname, '../node_modules/leaflet.fullscreen/', 'Control.FullScreen'),
            // 'leaflet-side-by-side': Path.resolve(__dirname, '../plugins/leaflet-side-by-side/index'),
            // 'geojson-extent': Path.resolve(__dirname, '../node_modules/@mapbox/geojson-extent/geojson-extent'),
            // 'geojsonhint': Path.resolve(__dirname, '../node_modules/@mapbox/geojsonhint/geojsonhint'),
            // 'bootstrap-datetimepicker': Path.resolve(__dirname, '../node_modules/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min'),
            // 'mapbox-gl': Path.resolve(__dirname, '../node_modules/mapbox-gl/dist/mapbox-gl'),
            // 'mapbox-gl-draw': Path.resolve(__dirname, '../node_modules/@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw'),
            // 'mapbox-gl-geocoder': Path.resolve(__dirname, '../node_modules/@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.min'),
            // 'text': Path.resolve(__dirname, '../node_modules/requirejs-text/text'),
            // 'dom-4': Path.resolve(__dirname, '../node_modules/dom4/build/dom4'),
            // 'togeojson': Path.resolve(__dirname, '../node_modules/@tmcw/togeojson/dist/togeojson.umd'),
            // 'ckeditor-jquery': Path.resolve(__dirname, '../node_modules/ckeditor/adapters/jquery'),
            // 'datatables.net': Path.resolve(__dirname, '../node_modules/datatables.net/js/jquery.dataTables.min'),
            // 'datatables.net-bs': Path.resolve(__dirname, '../node_modules/datatables.net-bs/js/dataTables.bootstrap.min'),
            // 'datatables.net-buttons': Path.resolve(__dirname, '../node_modules/datatables.net-buttons/js/dataTables.buttons.min'),
            // 'datatables.net-buttons-print': Path.resolve(__dirname, '../node_modules/datatables.net-buttons/js/buttons.print.min'),
            // 'datatables.net-buttons-html5': Path.resolve(__dirname, '../node_modules/datatables.net-buttons/js/buttons.html5.min'),
            // 'datatables.net-buttons-bs': Path.resolve(__dirname, '../node_modules/datatables.net-buttons-bs/js/buttons.bootstrap.min'),
            // 'datatables.net-responsive': Path.resolve(__dirname, '../node_modules/datatables.net-responsive/js/dataTables.responsive'),
            // 'datatables.net-responsive-bs': Path.resolve(__dirname, '../node_modules/datatables.net-responsive-bs/js/responsive.bootstrap'),
            'templates/views/components/iiif-popup.htm': Path.resolve(__dirname, '../../templates/views/components/iiif-popup.htm'),
            'templates/views/components/cards/related-resources-map-popup.htm': Path.resolve(__dirname, '../../templates/views/components/cards/related-resources-map-popup.htm'),
            'templates/views/components/map-popup.htm': Path.resolve(__dirname, '../../templates/views/components/map-popup.htm'),
            'templates/views/components/cards/map-popup.htm': Path.resolve(__dirname, '../../templates/views/components/cards/map-popup.htm'),

            // 'views/page-view': Path.resolve(__dirname, '../build/js/views/page-view.js'),

            'nifty': Path.resolve(__dirname, '../../media/plugins', 'nifty'),
            'async': Path.resolve(__dirname, '../../media/node_modules/requirejs-plugins/src/async'),
            'text': Path.resolve(__dirname, '../../media/node_modules/requirejs-text/text'),
            'jquery-lib': Path.resolve(__dirname, '../../media/node_modules/jquery/dist/jquery.min'),
            'jquery': Path.resolve(__dirname, '../../media/node_modules/jquery-migrate/dist/jquery-migrate.min'),
            'js-cookie': Path.resolve(__dirname, '../../media/node_modules/js-cookie/src/js.cookie'),
            'select2': Path.resolve(__dirname, '../../media/node_modules/select2/select2'),
            'bootstrap': Path.resolve(__dirname, '../../media/node_modules/bootstrap/dist/js/bootstrap.min'),
            'jquery-ui': Path.resolve(__dirname, '../../media/node_modules/jqueryui/jquery-ui.min'),
            'backbone': Path.resolve(__dirname, '../../media/node_modules/backbone/backbone-min'),
            'underscore': Path.resolve(__dirname, '../../media/node_modules/underscore/underscore-min'),
            'jquery-validate': Path.resolve(__dirname, '../../media/node_modules/jquery-validation/dist/jquery.validate.min'),
            'd3': Path.resolve(__dirname, '../../media/node_modules/d3/dist/d3.min'),
            'dropzone': Path.resolve(__dirname, '../../media/node_modules/dropzone/dist/min/dropzone-amd-module.min'),
            'ckeditor': Path.resolve(__dirname, '../../media/node_modules/ckeditor/ckeditor'),
            'ckeditor-jquery': Path.resolve(__dirname, '../../media/node_modules/ckeditor/adapters/jquery'),
            'knockout': Path.resolve(__dirname, '../../media/node_modules/knockout/build/output/knockout-latest'),
            'knockout-mapping': Path.resolve(__dirname, '../../media/node_modules/knockout-mapping/dist/knockout.mapping.min'),
            'moment': Path.resolve(__dirname, '../../media/node_modules/moment/min/moment.min'),
            'bootstrap-datetimepicker': Path.resolve(__dirname, '../../media/node_modules/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min'),
            'blueimp-gallery': Path.resolve(__dirname, '../../media/node_modules/blueimp-gallery/js/blueimp-gallery.min'),
            'blueimp-jquery': Path.resolve(__dirname, '../../media/node_modules/blueimp-gallery/js/jquery.blueimp-gallery.min'),
            'blueimp-helper': Path.resolve(__dirname, '../../media/node_modules/blueimp-gallery/js/blueimp-helper.min'),
            'datatables.net': Path.resolve(__dirname, '../../media/node_modules/datatables.net/js/jquery.dataTables.min'),
            'datatables.net-bs': Path.resolve(__dirname, '../../media/node_modules/datatables.net-bs/js/dataTables.bootstrap.min'),
            'datatables.net-buttons': Path.resolve(__dirname, '../../media/node_modules/datatables.net-buttons/js/dataTables.buttons.min'),
            'datatables.net-buttons-print': Path.resolve(__dirname, '../../media/node_modules/datatables.net-buttons/js/buttons.print.min'),
            'datatables.net-buttons-html5': Path.resolve(__dirname, '../../media/node_modules/datatables.net-buttons/js/buttons.html5.min'),
            'datatables.net-buttons-bs': Path.resolve(__dirname, '../../media/node_modules/datatables.net-buttons-bs/js/buttons.bootstrap.min'),
            'datatables.net-responsive': Path.resolve(__dirname, '../../media/node_modules/datatables.net-responsive/js/dataTables.responsive'),
            'datatables.net-responsive-bs': Path.resolve(__dirname, '../../media/node_modules/datatables.net-responsive-bs/js/responsive.bootstrap'),
            'chosen': Path.resolve(__dirname, '../../media/node_modules/chosen-js/chosen.jquery.min'),
            'mapbox-gl': Path.resolve(__dirname, '../../media/node_modules/mapbox-gl/dist/mapbox-gl'),
            'mapbox-gl-draw': Path.resolve(__dirname, '../../media/node_modules/@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw'),
            'mapbox-gl-geocoder': Path.resolve(__dirname, '../../media/node_modules/@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.min'),
            'proj4': Path.resolve(__dirname, '../../media/node_modules/proj4/dist/proj4'),
            'noUiSlider': Path.resolve(__dirname, '../../media/node_modules/nouislider/distribute/nouislider.min'),
            'geojson-extent': Path.resolve(__dirname, '../../media/node_modules/@mapbox/geojson-extent/geojson-extent'),
            'geojsonhint': Path.resolve(__dirname, '../../media/node_modules/@mapbox/geojsonhint/geojsonhint'),
            'bootstrap-colorpicker': Path.resolve(__dirname, '../../media/node_modules/bootstrap-colorpicker/dist/js/bootstrap-colorpicker.min'),
            'uuid': Path.resolve(__dirname, '../../media/node_modules/uuidjs/dist/uuid.core'),
            'turf': Path.resolve(__dirname, '../../media/node_modules/@turf/turf/turf.min'),
            'geohash': Path.resolve(__dirname, '../../media/node_modules/latlon-geohash/latlon-geohash'),
            'leaflet': Path.resolve(__dirname, '../../media/node_modules/leaflet/dist/leaflet'),
            'leaflet-iiif': Path.resolve(__dirname, '../../media/node_modules/leaflet-iiif/leaflet-iiif'),
            'leaflet-draw': Path.resolve(__dirname, '../../media/node_modules/leaflet-draw/dist/leaflet.draw'),
            'leaflet-fullscreen': Path.resolve(__dirname, '../../media/node_modules/leaflet.fullscreen/Control.FullScreen'),
            'leaflet-side-by-side': Path.resolve(__dirname, '../../media/plugins', 'leaflet-side-by-side/index'),
            'metismenu': Path.resolve(__dirname, '../../media/node_modules/metismenu/dist/metisMenu.min'),
            'knockstrap': Path.resolve(__dirname, '../../media/node_modules/knockstrap/build/knockstrap.min'),
            'jqtree': Path.resolve(__dirname, '../../media/node_modules/jqtree/tree.jquery'),
            // 'core-js':Path.resolve(__dirname, '../../media/node_modules/core-js/client/shim.min'),
            'dom-4': Path.resolve(__dirname, '../../media/node_modules/dom4/build/dom4'),
            'numeral': Path.resolve(__dirname, '../../media/node_modules/numeral/numeral'),
            'togeojson': Path.resolve(__dirname, '../../media/node_modules/@tmcw/togeojson/dist/togeojson.umd'),
            'cytoscape': Path.resolve(__dirname, '../../media/node_modules/cytoscape/dist/cytoscape.min'),
            'cytoscape-cola': Path.resolve(__dirname, '../../media/node_modules/cytoscape-cola/cytoscape-cola'),
            'webcola': Path.resolve(__dirname, '../../media/node_modules/webcola/WebCola/cola.min'),


            'themepunch-tools': Path.resolve(__dirname, '../../media/plugins', 'revolution-slider/rs-plugin/js/jquery.themepunch.tools.min'),
            'revolution-slider': Path.resolve(__dirname, '../../media/plugins', 'revolution-slider'),

            // 'requirejs': Path.resolve(__dirname, '../node_modules/requirejs', 'require.js'),
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
                test: /\.txt$/i,
                use: 'raw-loader',
            },
            {
                test: /\.(png|svg|jpg|jpeg|gif)$/i,
                type: 'asset/resource',
            },
            // {
            //     test: /\.(ico|jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2)(\?.*)?$/,
            //     use: {
            //         loader: 'file-loader',
            //         options: {
            //             name: 'img/[name].[ext]',
            //             // outputPath: 'img'
            //             outputPath: (url, resourcePath, context) => {
            //                 // `resourcePath` is original absolute path to asset
            //                 // `context` is directory where stored asset (`rootContext`) or `context` option
                
            //                 // To get relative path you can use
            //                 const relativePath = Path.relative(context, resourcePath);
                
            //                 // if (/my-custom-image\.png/.test(resourcePath)) {
            //                 //   return `other_output_path/${url}`;
            //                 // }
                
            //                 // if (/images/.test(context)) {
            //                 //   return `image_output_path/${url}`;
            //                 // }
                
            //                 // return `output_path/${url}`;

            //                 return relativePath
            //               },
            //         },
            //     },
            // },
        ],
    },
};