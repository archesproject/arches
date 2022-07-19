const fetch = require('cross-fetch');
const Path = require('path');
const webpack = require('webpack');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');

const { buildTemplateFilePathLookup } = require('./webpack-utils/build-template-filepath-lookup');
const { buildJavascriptFilepathLookup } = require('./webpack-utils/build-javascript-filepath-lookup');
const { ARCHES_CORE_DIRECTORY, PROJECT_PATH, DJANGO_SERVER_ADDRESS } = require('./webpack-metadata');


let archesCoreDirectory = ARCHES_CORE_DIRECTORY;
let djangoServerAddress = DJANGO_SERVER_ADDRESS;
let isTestEnvironment = false;

for (let arg of process.argv) {
    const keyValuePair = arg.split('=');

    if (keyValuePair[0] === 'arches_core_directory') {
        archesCoreDirectory = keyValuePair[1];
    }
    if (keyValuePair[0] === 'django_server_address') {
        djangoServerAddress = keyValuePair[1];
    }
    if (keyValuePair[0] === 'test') {
        isTestEnvironment = keyValuePair[1];
    }
}

const archesCoreEntryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, `${archesCoreDirectory}/app/media/js`), {});
const projectEntryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, `${PROJECT_PATH}/media/js`), {});

const archesCoreJavascriptRelativeFilepathToAbsoluteFilepathLookup = Object.keys(archesCoreEntryPointConfiguration).reduce((acc, path) => {
    acc[path + '$'] = Path.resolve(__dirname, `${archesCoreDirectory}/app/media/js/${path}.js`);
    return acc;
}, {});

const projectJavascriptRelativeFilepathToAbsoluteFilepathLookup = Object.keys(projectEntryPointConfiguration).reduce((acc, path) => {
    acc[path + '$'] = Path.resolve(__dirname, `${PROJECT_PATH}/media/js/${path}.js`);
    return acc;
}, {});

const javascriptRelativeFilepathToAbsoluteFilepathLookup = { 
    ...archesCoreJavascriptRelativeFilepathToAbsoluteFilepathLookup,
    ...projectJavascriptRelativeFilepathToAbsoluteFilepathLookup 
};

const templateFilepathLookup = buildTemplateFilePathLookup(
    Path.resolve(__dirname, `${archesCoreDirectory}/app/templates`),
    Path.resolve(__dirname, `${PROJECT_PATH}/templates`)
);

module.exports = {
    entry: { 
        ...archesCoreEntryPointConfiguration,
        ...projectEntryPointConfiguration 
    },
    output: {
        path: Path.resolve(__dirname, `${PROJECT_PATH}/media/build`),
        publicPath: '/static/',
        libraryTarget: 'amd-require',
        clean: true,
    },
    plugins: [
        new CleanWebpackPlugin(),
        new CopyWebpackPlugin({ 
            patterns: [
                {
                    from: Path.resolve(__dirname, `${archesCoreDirectory}/app/media/img`), 
                    to: 'img',
                    priority: 5,
                }, 
                {
                    from: Path.resolve(__dirname, `${PROJECT_PATH}/media/img`), 
                    to: 'img',
                    priority: 10,
                    force: true
                } 
            ] 
        }),
        new webpack.DefinePlugin({
            ARCHES_CORE_DIRECTORY: `'${archesCoreDirectory}'`,
            PROJECT_PATH: `'${PROJECT_PATH}'`
        }),
        new webpack.ProvidePlugin({
            jquery:  Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/jquery/dist/jquery.min`),
            jQuery:  Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/jquery/dist/jquery.min`),
            $:  Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/jquery/dist/jquery.min`),
        }),
        new BundleTracker({ filename: Path.resolve(__dirname, `webpack-stats.json`) }),
    ],
    resolveLoader: {
        alias: {
            text: 'raw-loader'
        }
    },
    resolve: {
        modules: [Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules`)],
        alias: {
            ...javascriptRelativeFilepathToAbsoluteFilepathLookup,
            ...templateFilepathLookup,
            'plugins/knockout-select2': Path.resolve(__dirname, `${archesCoreDirectory}/app/media/plugins`, 'knockout-select2.js'),
            'nifty': Path.resolve(__dirname, `${archesCoreDirectory}/app/media/plugins`, 'nifty'),
            'leaflet-side-by-side': Path.resolve(__dirname, `${archesCoreDirectory}/app/media/plugins`, 'leaflet-side-by-side/index'),
            'themepunch-tools': Path.resolve(__dirname, `${PROJECT_PATH}/media/plugins`, 'revolution-slider/rs-plugin/js/jquery.themepunch.tools.min'),
            'revolution-slider': Path.resolve(__dirname, `${PROJECT_PATH}/media/plugins`, 'revolution-slider'),
            
            'async': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/requirejs-plugins/src/async`),
            'text': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/requirejs-text/text`),
            'jquery': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/jquery/dist/jquery.min`),
            'js-cookie': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/js-cookie/src/js.cookie`),
            'select2': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/select2/select2`),
            'bootstrap': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/bootstrap/dist/js/bootstrap.min`),
            'jquery-ui': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/jqueryui/jquery-ui.min`),
            'backbone': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/backbone/backbone-min`),
            'underscore': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/underscore/underscore-min`),
            'jquery-validate': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/jquery-validation/dist/jquery.validate.min`),
            'd3': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/d3/dist/d3.min`),
            'dropzone': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/dropzone/dist/min/dropzone-amd-module.min`),
            'ckeditor': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/ckeditor/ckeditor`),
            'ckeditor-jquery': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/ckeditor/adapters/jquery`),
            'knockout': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/knockout/build/output/knockout-latest`),
            'knockout-mapping': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/knockout-mapping/dist/knockout.mapping.min`),
            'moment': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/moment/moment.js`),
            'bootstrap-datetimepicker': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min`),
            'blueimp-gallery': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/blueimp-gallery/js/blueimp-gallery.min`),
            'blueimp-jquery': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/blueimp-gallery/js/jquery.blueimp-gallery.min`),
            'blueimp-helper': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/blueimp-gallery/js/blueimp-helper.min`),
            'datatables.net': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/datatables.net/js/jquery.dataTables.min`),
            'datatables.net-bs': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/datatables.net-bs/js/dataTables.bootstrap.min`),
            'datatables.net-buttons': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/datatables.net-buttons/js/dataTables.buttons.min`),
            'datatables.net-buttons-print': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/datatables.net-buttons/js/buttons.print.min`),
            'datatables.net-buttons-html5': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/datatables.net-buttons/js/buttons.html5.min`),
            'datatables.net-buttons-bs': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/datatables.net-buttons-bs/js/buttons.bootstrap.min`),
            'datatables.net-responsive': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/datatables.net-responsive/js/dataTables.responsive`),
            'datatables.net-responsive-bs': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/datatables.net-responsive-bs/js/responsive.bootstrap`),
            'chosen': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/chosen-js/chosen.jquery.min`),
            'mapbox-gl': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/mapbox-gl/dist/mapbox-gl`),
            'mapbox-gl-draw': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw`),
            'mapbox-gl-geocoder': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.min`),
            'proj4': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/proj4/dist/proj4`),
            'noUiSlider': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/nouislider/distribute/nouislider.min`),
            'geojson-extent': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/@mapbox/geojson-extent/geojson-extent`),
            'geojsonhint': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/@mapbox/geojsonhint/geojsonhint`),
            'bootstrap-colorpicker': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/bootstrap-colorpicker/dist/js/bootstrap-colorpicker.min`),
            'uuid': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/uuidjs/dist/uuid.core`),
            'turf': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/@turf/turf/turf.min`),
            'geohash': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/latlon-geohash/latlon-geohash`),
            'leaflet': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/leaflet/dist/leaflet`),
            'leaflet-iiif': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/leaflet-iiif/leaflet-iiif`),
            'leaflet-draw': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/leaflet-draw/dist/leaflet.draw`),
            'leaflet-fullscreen': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/leaflet.fullscreen/Control.FullScreen`),
            'metismenu': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/metismenu/dist/metisMenu.min`),
            'knockstrap': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/knockstrap/build/knockstrap.min`),
            'jqtree': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/jqtree/tree.jquery`),
            'dom-4': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/dom4/build/dom4`),
            'numeral': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/numeral/numeral`),
            'togeojson': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/@tmcw/togeojson/dist/togeojson.umd`),
            'cytoscape': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/cytoscape/dist/cytoscape.min`),
            'cytoscape-cola': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/cytoscape-cola/cytoscape-cola`),
            'webcola': Path.resolve(__dirname, `${PROJECT_PATH}/media/node_modules/webcola/WebCola/cola.min`),
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
                loader: `${PROJECT_PATH}/media/node_modules/html-loader`,
                options: {
                    esModule: false,
                    minimize: {
                        removeComments: false,
                    },
                    preprocessor: async (content, loaderContext) => {
                        const resourcePath = loaderContext['resourcePath'];
                        const projectResourcePathData = resourcePath.split(`${PROJECT_PATH}/`);
                        const templatePath = projectResourcePathData.length > 1 ? projectResourcePathData[1] : resourcePath.split(`${archesCoreDirectory}/app/`)[1]; 

                        let resp;

                        const renderTemplate = async(failureCount=0) => {
                            /*
                                Sometimes Django can choke on the number of requests, this function will 
                                continue attempting to render the template until successful or 5 failures.
                            */ 
                            if (failureCount < 5) {
                                try {
                                    resp = await fetch(djangoServerAddress + templatePath);
                                }
                                catch(e) { 
                                    failureCount += 1;
                                    console.warn(
                                        `"${templatePath}" has failed to load. Retrying (${failureCount} / 5)...`
                                    );
                                    return await renderTemplate(failureCount=failureCount);
                                }
                            }
                            else {
                                console.error(`"${templatePath}" has failed to load! Falling back to un-rendered file.`);
                                resp = {
                                   text: () => (
                                        new Promise((resolve, _reject) => {
                                            /*
                                                if isTestEnvironment is true, failures will return a empty string which will
                                                still allow the package to build.
                                            */ 
                                            
                                            resolve(isTestEnvironment ? '' : content);  
                                        })
                                   )
                                };
                            }
                        };

                        await renderTemplate();

                        const responseText = await resp.text();
                        return responseText;
                    }
                }
            },
            {
                test: /\.txt$/i,
                use: `${PROJECT_PATH}/media/node_modules/raw-loader`,
            },
            {
                test: /\.(png|svg|jpg|jpeg|gif)$/i,
                type: 'asset/resource',
            },
        ],
    },
};

