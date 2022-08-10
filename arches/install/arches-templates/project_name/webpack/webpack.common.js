const fetch = require('cross-fetch');
const Path = require('path');
const webpack = require('webpack');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');

const { buildTemplateFilePathLookup } = require('./webpack-utils/build-template-filepath-lookup');
const { buildJavascriptFilepathLookup } = require('./webpack-utils/build-javascript-filepath-lookup');
const { buildImageFilePathLookup } = require('./webpack-utils/build-image-filepath-lookup');

var USER_DEFINED_ARCHES_CORE_DIRECTORY;
var USER_DEFINED_APP_ROOT_DIRECTORY;
var USER_DEFINED_DJANGO_SERVER_ADDRESS;
var USER_DEFINED_PUBLIC_PATH;
var USER_DEFINED_PROJECT_NODE_MODULES_ALIASES;

try {
    var { 
        USER_DEFINED_ARCHES_CORE_DIRECTORY, 
        USER_DEFINED_APP_ROOT_DIRECTORY,
        USER_DEFINED_DJANGO_SERVER_ADDRESS, 
        USER_DEFINED_PUBLIC_PATH,
        USER_DEFINED_PROJECT_NODE_MODULES_ALIASES,
    } = require('./webpack-user-config');
} catch (e) {}

const { 
    ARCHES_CORE_DIRECTORY, 
    APP_ROOT_DIRECTORY,
    DJANGO_SERVER_ADDRESS, 
    PROJECT_NODE_MODULES_ALIASES,
    PUBLIC_PATH,
} = require('./webpack-meta-config');


let archesCoreDirectory = USER_DEFINED_ARCHES_CORE_DIRECTORY || ARCHES_CORE_DIRECTORY;
let appRootDirectory = USER_DEFINED_APP_ROOT_DIRECTORY || APP_ROOT_DIRECTORY;
let projectNodeModulesAliases = USER_DEFINED_PROJECT_NODE_MODULES_ALIASES || PROJECT_NODE_MODULES_ALIASES;
let djangoServerAddress = USER_DEFINED_DJANGO_SERVER_ADDRESS || DJANGO_SERVER_ADDRESS;
let publicPath = USER_DEFINED_PUBLIC_PATH || PUBLIC_PATH;
let isTestEnvironment = false;

for (let arg of process.argv) {
    const keyValuePair = arg.split('=');
    const key = keyValuePair[0].toLowerCase();
    const value = keyValuePair[1];

    if (key === 'arches_core_directory') {
        archesCoreDirectory = value;
    }
    if (key === 'app_root_directory') {
        appRootDirectory = value;
    }
    if (key === 'django_server_address') {
        djangoServerAddress = value;
    }
    if (key === 'public_path') {
        publicPath = value;
    }
    if (key === 'test') {
        isTestEnvironment = value;
    }
}

const archesCoreEntryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, `${archesCoreDirectory}/app/media/js`), {});
const projectEntryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, `${appRootDirectory}/media/js`), {});

const archesCoreJavascriptRelativeFilepathToAbsoluteFilepathLookup = Object.keys(archesCoreEntryPointConfiguration).reduce((acc, path) => {
    acc[path + '$'] = Path.resolve(__dirname, `${archesCoreDirectory}/app/media/js/${path}.js`);
    return acc;
}, {});

const projectJavascriptRelativeFilepathToAbsoluteFilepathLookup = Object.keys(projectEntryPointConfiguration).reduce((acc, path) => {
    acc[path + '$'] = Path.resolve(__dirname, `${appRootDirectory}/media/js/${path}.js`);
    return acc;
}, {});

const javascriptRelativeFilepathToAbsoluteFilepathLookup = { 
    ...archesCoreJavascriptRelativeFilepathToAbsoluteFilepathLookup,
    ...projectJavascriptRelativeFilepathToAbsoluteFilepathLookup 
};

const { ARCHES_CORE_NODE_MODULES_ALIASES } = require(`${archesCoreDirectory}/../webpack/webpack-meta-config.js`);
const parsedArchesCoreNodeModulesAliases = Object.entries(JSON.parse(ARCHES_CORE_NODE_MODULES_ALIASES)).reduce((acc, [alias, executeableString]) => {
    // eval() should be safe here, it's running developer-defined code during build
    acc[alias] = eval(executeableString);
    return acc;
}, {});

const parsedProjectNodeModulesAliases = Object.entries(JSON.parse(projectNodeModulesAliases)).reduce((acc, [alias, executeableString]) => {
    // eval() should be safe here, it's running developer-defined code during build
    acc[alias] = eval(executeableString);
    return acc;
}, {});

const nodeModulesAliases = {
    ...parsedArchesCoreNodeModulesAliases,
    ...parsedProjectNodeModulesAliases
};

const templateFilepathLookup = buildTemplateFilePathLookup(
    Path.resolve(__dirname, `${archesCoreDirectory}/app/templates`),
    Path.resolve(__dirname, `${appRootDirectory}/templates`)
);

const imageFilepathLookup = buildImageFilePathLookup(
    publicPath,
    Path.resolve(__dirname, `${archesCoreDirectory}/app/media/img`),
    Path.resolve(__dirname, `${appRootDirectory}/media/img`)
);

module.exports = {
    entry: { 
        ...archesCoreEntryPointConfiguration,
        ...projectEntryPointConfiguration 
    },
    output: {
        path: Path.resolve(__dirname, `${appRootDirectory}/media/build`),
        publicPath: publicPath,
        libraryTarget: 'amd-require',
        clean: true,
    },
    plugins: [
        new CleanWebpackPlugin(),
        new webpack.DefinePlugin({
            ARCHES_CORE_DIRECTORY: `'${archesCoreDirectory}'`,
            APP_ROOT_DIRECTORY: `'${appRootDirectory}'`
        }),
        new webpack.ProvidePlugin({
            jquery:  Path.resolve(__dirname, `${appRootDirectory}/media/node_modules/jquery/dist/jquery.min`),
            jQuery:  Path.resolve(__dirname, `${appRootDirectory}/media/node_modules/jquery/dist/jquery.min`),
            $:  Path.resolve(__dirname, `${appRootDirectory}/media/node_modules/jquery/dist/jquery.min`)
        }),
        new MiniCssExtractPlugin(),
        new BundleTracker({ filename: Path.resolve(__dirname, `webpack-stats.json`) }),
    ],
    resolveLoader: {
        alias: {
            text: 'raw-loader'
        }
    },
    resolve: {
        modules: [Path.resolve(__dirname, `${appRootDirectory}/media/node_modules`)],
        alias: {
            ...javascriptRelativeFilepathToAbsoluteFilepathLookup,
            ...templateFilepathLookup,
            ...imageFilepathLookup,
            ...nodeModulesAliases,
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
                test: /\.js$/,
                exclude: /node_modules/,
                loader: `${appRootDirectory}/media/node_modules/babel-loader`,
                options: {
                    presets: ['@babel/preset-env'],
                    cacheDirectory: `${appRootDirectory}/media/node_modules/.cache/babel-loader`,
                }
            },
            {
                test: /\.s?css$/i,
                use: [
                    {
                        'loader': MiniCssExtractPlugin.loader,
                    },
                    {
                        'loader': `${appRootDirectory}/media/node_modules/css-loader`,
                    },
                    {
                        'loader': `${appRootDirectory}/media/node_modules/postcss-loader`,
                    },
                    {
                        'loader': `${appRootDirectory}/media/node_modules/sass-loader`,
                    }
                ],
            },
            {
                test: /\.html?$/i,
                loader: `${appRootDirectory}/media/node_modules/html-loader`,
                options: {
                    esModule: false,
                    minimize: {
                        removeComments: false,
                    },
                    preprocessor: async (content, loaderContext) => {
                        const resourcePath = loaderContext['resourcePath'];
                        const projectResourcePathData = resourcePath.split(`${appRootDirectory}/`);
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
                use: `${appRootDirectory}/media/node_modules/raw-loader`,
            },
            {
                test: /\.(png|svg|jpg|jpeg|gif)$/i,
                type: 'asset/resource',
            },
        ],
    },
};