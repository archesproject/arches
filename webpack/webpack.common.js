const fetch = require('cross-fetch');
const Path = require('path');
const webpack = require('webpack');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');

const { buildTemplateFilePathLookup } = require('./webpack-utils/build-template-filepath-lookup');
const { buildJavascriptFilepathLookup } = require('./webpack-utils/build-javascript-filepath-lookup');
const { ARCHES_CORE_DIRECTORY, PROJECT_ROOT_DIRECTORY, DJANGO_SERVER_ADDRESS, ARCHES_CORE_NODE_MODULES_ALIASES } = require('./webpack-metadata');


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
const projectEntryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, `${PROJECT_ROOT_DIRECTORY}/media/js`), {});

const archesCoreJavascriptRelativeFilepathToAbsoluteFilepathLookup = Object.keys(archesCoreEntryPointConfiguration).reduce((acc, path) => {
    acc[path + '$'] = Path.resolve(__dirname, `${archesCoreDirectory}/app/media/js/${path}.js`);
    return acc;
}, {});

const projectJavascriptRelativeFilepathToAbsoluteFilepathLookup = Object.keys(projectEntryPointConfiguration).reduce((acc, path) => {
    acc[path + '$'] = Path.resolve(__dirname, `${PROJECT_ROOT_DIRECTORY}/media/js/${path}.js`);
    return acc;
}, {});

const javascriptRelativeFilepathToAbsoluteFilepathLookup = { 
    ...archesCoreJavascriptRelativeFilepathToAbsoluteFilepathLookup,
    ...projectJavascriptRelativeFilepathToAbsoluteFilepathLookup 
};

const archesCoreNodeModulesAliases = Object.entries(JSON.parse(ARCHES_CORE_NODE_MODULES_ALIASES)).reduce((acc, [alias, executeableString]) => {
    // eval() should be safe here, it's running developer-defined code during build
    acc[alias] = eval(executeableString);
    return acc;
}, {});

const templateFilepathLookup = buildTemplateFilePathLookup(
    Path.resolve(__dirname, `${archesCoreDirectory}/app/templates`),
    Path.resolve(__dirname, `${PROJECT_ROOT_DIRECTORY}/templates`)
);

module.exports = {
    entry: { 
        ...archesCoreEntryPointConfiguration,
        ...projectEntryPointConfiguration 
    },
    output: {
        path: Path.resolve(__dirname, `${PROJECT_ROOT_DIRECTORY}/media/build`),
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
                    from: Path.resolve(__dirname, `${PROJECT_ROOT_DIRECTORY}/media/img`), 
                    to: 'img',
                    priority: 10,
                    force: true
                } 
            ] 
        }),
        new webpack.DefinePlugin({
            ARCHES_CORE_DIRECTORY: `'${archesCoreDirectory}'`,
            PROJECT_ROOT_DIRECTORY: `'${PROJECT_ROOT_DIRECTORY}'`
        }),
        new webpack.ProvidePlugin({
            jquery:  Path.resolve(__dirname, `${PROJECT_ROOT_DIRECTORY}/media/node_modules/jquery/dist/jquery.min`),
            jQuery:  Path.resolve(__dirname, `${PROJECT_ROOT_DIRECTORY}/media/node_modules/jquery/dist/jquery.min`),
            $:  Path.resolve(__dirname, `${PROJECT_ROOT_DIRECTORY}/media/node_modules/jquery/dist/jquery.min`),
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
        modules: [Path.resolve(__dirname, `${PROJECT_ROOT_DIRECTORY}/media/node_modules`)],
        alias: {
            ...javascriptRelativeFilepathToAbsoluteFilepathLookup,
            ...templateFilepathLookup,
            ...archesCoreNodeModulesAliases,
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
                loader: `${PROJECT_ROOT_DIRECTORY}/media/node_modules/babel-loader`,
                options: {
                    presets: ['@babel/preset-env'],
                    cacheDirectory: `${PROJECT_ROOT_DIRECTORY}/media/node_modules/.cache/babel-loader`,
                }
            },
            {
                test: /\.s?css$/i,
                use: [
                    {
                        'loader': MiniCssExtractPlugin.loader,
                    },
                    {
                        'loader': `${PROJECT_ROOT_DIRECTORY}/media/node_modules/css-loader`,
                    },
                    {
                        'loader': `${PROJECT_ROOT_DIRECTORY}/media/node_modules/postcss-loader`,
                    },
                    {
                        'loader': `${PROJECT_ROOT_DIRECTORY}/media/node_modules/sass-loader`,
                    }
                ],
            },
            {
                test: /\.html?$/i,
                loader: `${PROJECT_ROOT_DIRECTORY}/media/node_modules/html-loader`,
                options: {
                    esModule: false,
                    minimize: {
                        removeComments: false,
                    },
                    preprocessor: async (content, loaderContext) => {
                        const resourcePath = loaderContext['resourcePath'];
                        const projectResourcePathData = resourcePath.split(`${PROJECT_ROOT_DIRECTORY}/`);
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
                use: `${PROJECT_ROOT_DIRECTORY}/media/node_modules/raw-loader`,
            },
            {
                test: /\.(png|svg|jpg|jpeg|gif)$/i,
                type: 'asset/resource',
            },
        ],
    },
};

