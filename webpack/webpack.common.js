const Path = require('path');
const fs = require('fs');
const webpack = require('webpack');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');

const buildJavascriptFilepathLookup = function(path, outerAcc) {
    return fs.readdirSync(path).reduce((acc, name) => {
        if (fs.lstatSync(path + '/' + name).isDirectory() ) {
            return buildJavascriptFilepathLookup(path + '/' + name, acc);
        }
        else {
            const subPath = (path + '/' + name).split('js/')[1];
            const parsedPath = Path.parse(subPath);
            const pathName = parsedPath['dir'] + '/' + parsedPath['name']

            return { 
                ...acc, 
                [pathName]: { 'import': `/arches/app/media/js/${subPath}`, 'filename': `js/[name].js` } 
            };
        }
    }, outerAcc);
};
const entryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, '../arches/app/media/js'), {});


const buildTemplateFilePathLookup = function(path, outerAcc) {
    return fs.readdirSync(path).reduce((acc, name) => {
        if (fs.lstatSync(path + '/' + name).isDirectory() ) {
            return buildTemplateFilePathLookup(path + '/' + name, acc);
        }
        else {
            const subPath = (path + '/' + name).split('templates/')[1];
            const parsedPath = Path.parse(subPath);
            const filename = parsedPath['dir'] + '/' + parsedPath['base'];

            return { 
                ...acc, 
                [`templates/${filename}`]: Path.resolve(__dirname, `../arches/app/templates/${subPath}`)
            };
        }
    }, outerAcc);
};
const templatePathConfiguration = buildTemplateFilePathLookup(Path.resolve(__dirname, '../arches/app/templates'), {});


const buildHtmlWebpackPluginList = function(path, outerAcc) {
    const list = fs.readdirSync(path).reduce((acc, name) => {
        if (fs.lstatSync(path + '/' + name).isDirectory() ) {
            return buildHtmlWebpackPluginList(path + '/' + name, acc);
        }
        else {
            const subPath = (path + '/' + name).split('app/templates/')[1];
            const parsedPath = Path.parse(subPath);
            
            var filename = parsedPath['name'];
            if (parsedPath['dir']) {
               filename = parsedPath['dir'] + '/' + parsedPath['name'];
            }
            
            acc.push(new HtmlWebpackPlugin({
                template: `../../../../arches/app/templates/${filename}${parsedPath['ext']}`, // relative path to the HTML files
                filename: `templates/${filename}${parsedPath['ext']}`, // output HTML files
                chunks:  [ Path.resolve(__dirname, `../arches/app/media/js/${filename}.js`) ] // respective JS files
            }));
            return acc;
        }
    }, outerAcc);
    return list;
};
const htmlWebpackPluginList = buildHtmlWebpackPluginList(Path.resolve(__dirname, '../arches/app/templates'), []);


var javascriptRelativeFilepathToAbsoluteFilepathLookup = Object.keys(entryPointConfiguration).reduce((acc, path) => {
    acc[path + '$'] = Path.resolve(__dirname, `../arches/app/media/js/${path}.js`);
    return acc;
}, {});


module.exports = {
    entry: entryPointConfiguration,
    output: {
        path: Path.resolve(__dirname, '../arches/app/media/build'),
        publicPath: '/foo/',
        libraryTarget: 'amd-require',
        clean: true,
    },
    plugins: [
        new CleanWebpackPlugin(),
        new CopyWebpackPlugin({ patterns: [{from: Path.resolve(__dirname, '../arches/app/media/img'), to: 'img'} ] }),
        new webpack.ProvidePlugin({
            jquery:  Path.resolve(__dirname, '../arches/app/media/node_modules/jquery/dist/jquery.min'),
            jQuery:  Path.resolve(__dirname, '../arches/app/media/node_modules/jquery/dist/jquery.min'),
            $:  Path.resolve(__dirname, '../arches/app/media/node_modules/jquery/dist/jquery.min'),
        }),
        new BundleTracker({ filename: './webpack/webpack-stats.json' }),
    ].concat(htmlWebpackPluginList),
    resolveLoader: {
        alias: {
            text: 'text-loader'
        }
    },
    resolve: {
        modules: [Path.resolve(__dirname, '../arches/app/media/node_modules')],
        alias: {
            ...javascriptRelativeFilepathToAbsoluteFilepathLookup,
            ...templatePathConfiguration,
            'arches': Path.resolve(__dirname, '../arches/app/templates', 'javascript.htm'),
            'report-templates': Path.resolve(__dirname, '../arches/app/templates', 'javascript.htm'),
            'card-components': Path.resolve(__dirname, '../arches/app/templates', 'javascript.htm'),
            'file-renderers': Path.resolve(__dirname, '../arches/app/templates', 'javascript.htm'),
            'function-templates': Path.resolve(__dirname, '../arches/app/templates', 'javascript.htm'),
            'component-templates': Path.resolve(__dirname, '../arches/app/templates', 'javascript.htm'),
            'geocoder-templates': Path.resolve(__dirname, '../arches/app/templates', 'javascript.htm'),
            'search-components': Path.resolve(__dirname, '../arches/app/templates', 'javascript.htm'),
            'datatype-config-components': Path.resolve(__dirname, '../arches/app/templates', 'javascript.htm'),
            'widgets': Path.resolve(__dirname, '../arches/app/templates', 'javascript.htm'),
            'plugins/knockout-select2': Path.resolve(__dirname, '../arches/app/media/plugins', 'knockout-select2.js'),
            'jquery-ui/draggable': Path.resolve(__dirname, '../node_modules/jqueryui', 'jquery-ui.min.js'),
            'jquery-ui/sortable': Path.resolve(__dirname, '../node_modules/jqueryui', 'jquery-ui.min.js'),

            'nifty': Path.resolve(__dirname, '../arches/app/media/plugins', 'nifty'),
            'async': Path.resolve(__dirname, '../arches/app/media/node_modules/requirejs-plugins/src/async'),
            'text': Path.resolve(__dirname, '../arches/app/media/node_modules/requirejs-text/text'),
            'jquery': Path.resolve(__dirname, '../arches/app/media/node_modules/jquery/dist/jquery.min'),
            // 'jquery': Path.resolve(__dirname, '../arches/app/media/node_modules/jquery-migrate/dist/jquery-migrate.min'),
            'js-cookie': Path.resolve(__dirname, '../arches/app/media/node_modules/js-cookie/src/js.cookie'),
            'select2': Path.resolve(__dirname, '../arches/app/media/node_modules/select2/select2'),
            'bootstrap': Path.resolve(__dirname, '../arches/app/media/node_modules/bootstrap/dist/js/bootstrap.min'),
            'jquery-ui': Path.resolve(__dirname, '../arches/app/media/node_modules/jqueryui/jquery-ui.min'),
            'backbone': Path.resolve(__dirname, '../arches/app/media/node_modules/backbone/backbone-min'),
            'underscore': Path.resolve(__dirname, '../arches/app/media/node_modules/underscore/underscore-min'),
            'jquery-validate': Path.resolve(__dirname, '../arches/app/media/node_modules/jquery-validation/dist/jquery.validate.min'),
            'd3': Path.resolve(__dirname, '../arches/app/media/node_modules/d3/dist/d3.min'),
            'dropzone': Path.resolve(__dirname, '../arches/app/media/node_modules/dropzone/dist/min/dropzone-amd-module.min'),
            'ckeditor': Path.resolve(__dirname, '../arches/app/media/node_modules/ckeditor/ckeditor'),
            'ckeditor-jquery': Path.resolve(__dirname, '../arches/app/media/node_modules/ckeditor/adapters/jquery'),
            'knockout': Path.resolve(__dirname, '../arches/app/media/node_modules/knockout/build/output/knockout-latest'),
            'knockout-mapping': Path.resolve(__dirname, '../arches/app/media/node_modules/knockout-mapping/dist/knockout.mapping.min'),
            'moment': Path.resolve(__dirname, '../arches/app/media/node_modules/moment/min/moment.min'),
            'bootstrap-datetimepicker': Path.resolve(__dirname, '../arches/app/media/node_modules/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min'),
            'blueimp-gallery': Path.resolve(__dirname, '../arches/app/media/node_modules/blueimp-gallery/js/blueimp-gallery.min'),
            'blueimp-jquery': Path.resolve(__dirname, '../arches/app/media/node_modules/blueimp-gallery/js/jquery.blueimp-gallery.min'),
            'blueimp-helper': Path.resolve(__dirname, '../arches/app/media/node_modules/blueimp-gallery/js/blueimp-helper.min'),
            'datatables.net': Path.resolve(__dirname, '../arches/app/media/node_modules/datatables.net/js/jquery.dataTables.min'),
            'datatables.net-bs': Path.resolve(__dirname, '../arches/app/media/node_modules/datatables.net-bs/js/dataTables.bootstrap.min'),
            'datatables.net-buttons': Path.resolve(__dirname, '../arches/app/media/node_modules/datatables.net-buttons/js/dataTables.buttons.min'),
            'datatables.net-buttons-print': Path.resolve(__dirname, '../arches/app/media/node_modules/datatables.net-buttons/js/buttons.print.min'),
            'datatables.net-buttons-html5': Path.resolve(__dirname, '../arches/app/media/node_modules/datatables.net-buttons/js/buttons.html5.min'),
            'datatables.net-buttons-bs': Path.resolve(__dirname, '../arches/app/media/node_modules/datatables.net-buttons-bs/js/buttons.bootstrap.min'),
            'datatables.net-responsive': Path.resolve(__dirname, '../arches/app/media/node_modules/datatables.net-responsive/js/dataTables.responsive'),
            'datatables.net-responsive-bs': Path.resolve(__dirname, '../arches/app/media/node_modules/datatables.net-responsive-bs/js/responsive.bootstrap'),
            'chosen': Path.resolve(__dirname, '../arches/app/media/node_modules/chosen-js/chosen.jquery.min'),
            'mapbox-gl': Path.resolve(__dirname, '../arches/app/media/node_modules/mapbox-gl/dist/mapbox-gl'),
            'mapbox-gl-draw': Path.resolve(__dirname, '../arches/app/media/node_modules/@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw'),
            'mapbox-gl-geocoder': Path.resolve(__dirname, '../arches/app/media/node_modules/@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.min'),
            'proj4': Path.resolve(__dirname, '../arches/app/media/node_modules/proj4/dist/proj4'),
            'noUiSlider': Path.resolve(__dirname, '../arches/app/media/node_modules/nouislider/distribute/nouislider.min'),
            'geojson-extent': Path.resolve(__dirname, '../arches/app/media/node_modules/@mapbox/geojson-extent/geojson-extent'),
            'geojsonhint': Path.resolve(__dirname, '../arches/app/media/node_modules/@mapbox/geojsonhint/geojsonhint'),
            'bootstrap-colorpicker': Path.resolve(__dirname, '../arches/app/media/node_modules/bootstrap-colorpicker/dist/js/bootstrap-colorpicker.min'),
            'uuid': Path.resolve(__dirname, '../arches/app/media/node_modules/uuidjs/dist/uuid.core'),
            'turf': Path.resolve(__dirname, '../arches/app/media/node_modules/@turf/turf/turf.min'),
            'geohash': Path.resolve(__dirname, '../arches/app/media/node_modules/latlon-geohash/latlon-geohash'),
            'leaflet': Path.resolve(__dirname, '../arches/app/media/node_modules/leaflet/dist/leaflet'),
            'leaflet-iiif': Path.resolve(__dirname, '../arches/app/media/node_modules/leaflet-iiif/leaflet-iiif'),
            'leaflet-draw': Path.resolve(__dirname, '../arches/app/media/node_modules/leaflet-draw/dist/leaflet.draw'),
            'leaflet-fullscreen': Path.resolve(__dirname, '../arches/app/media/node_modules/leaflet.fullscreen/Control.FullScreen'),
            'leaflet-side-by-side': Path.resolve(__dirname, '../arches/app/media/plugins', 'leaflet-side-by-side/index'),
            'metismenu': Path.resolve(__dirname, '../arches/app/media/node_modules/metismenu/dist/metisMenu.min'),
            'knockstrap': Path.resolve(__dirname, '../arches/app/media/node_modules/knockstrap/build/knockstrap.min'),
            'jqtree': Path.resolve(__dirname, '../arches/app/media/node_modules/jqtree/tree.jquery'),
            'dom-4': Path.resolve(__dirname, '../arches/app/media/node_modules/dom4/build/dom4'),
            'numeral': Path.resolve(__dirname, '../arches/app/media/node_modules/numeral/numeral'),
            'togeojson': Path.resolve(__dirname, '../arches/app/media/node_modules/@tmcw/togeojson/dist/togeojson.umd'),
            'cytoscape': Path.resolve(__dirname, '../arches/app/media/node_modules/cytoscape/dist/cytoscape.min'),
            'cytoscape-cola': Path.resolve(__dirname, '../arches/app/media/node_modules/cytoscape-cola/cytoscape-cola'),
            'webcola': Path.resolve(__dirname, '../arches/app/media/node_modules/webcola/WebCola/cola.min'),
            'themepunch-tools': Path.resolve(__dirname, '../arches/app/media/plugins', 'revolution-slider/rs-plugin/js/jquery.themepunch.tools.min'),
            'revolution-slider': Path.resolve(__dirname, '../arches/app/media/plugins', 'revolution-slider'),
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
                test: /\.html?$/i,
                use: ["./arches/app/media/node_modules/html-loader"],
            },
            {
                test: /\.txt$/i,
                use: './arches/app/media/node_modules/raw-loader',
            },
            {
                test: /\.(png|svg|jpg|jpeg|gif)$/i,
                type: 'asset/resource',
            },
        ],
    },
};

