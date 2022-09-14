/* eslint-disable */

const fetch = require('cross-fetch');
const Path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');

const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const { spawn } = require("child_process");

const { buildTemplateFilePathLookup } = require('./webpack-utils/build-template-filepath-lookup');
const { buildJavascriptFilepathLookup } = require('./webpack-utils/build-javascript-filepath-lookup');
const { buildImageFilePathLookup } = require('./webpack-utils/build-image-filepath-lookup');
const { PROJECT_NODE_MODULES_ALIASES } = require('./webpack-node-modules-aliases');


module.exports = () => {
    return new Promise((resolve, _reject) => {
        const createWebpackConfig = function(data) {  // reads from application's settings.py
            const parsedData = JSON.parse(data);
            
            const ROOT_DIR = parsedData['ROOT_DIR'];
            const APP_ROOT = parsedData['APP_ROOT'];
            const STATIC_URL = parsedData['STATIC_URL']
            const ARCHES_NAMESPACE_FOR_DATA_EXPORT = parsedData['ARCHES_NAMESPACE_FOR_DATA_EXPORT']
            const WEBPACK_DEVELOPMENT_SERVER_PORT = parsedData['WEBPACK_DEVELOPMENT_SERVER_PORT']

            console.log('Data imported from settings.py:', parsedData)
        
            const archesCoreEntryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'js'), {});
            const projectEntryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, APP_ROOT, 'media', 'js'), {});
            
            const archesCoreJavascriptRelativeFilepathToAbsoluteFilepathLookup = Object.keys(archesCoreEntryPointConfiguration).reduce((acc, path) => {
                acc[path + '$'] = Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'js', `${path}.js`);
                return acc;
            }, {});
            
            const projectJavascriptRelativeFilepathToAbsoluteFilepathLookup = Object.keys(projectEntryPointConfiguration).reduce((acc, path) => {
                acc[path + '$'] = Path.resolve(__dirname, APP_ROOT, 'media', 'js', `${path}.js`);
                return acc;
            }, {});
            
            const javascriptRelativeFilepathToAbsoluteFilepathLookup = { 
                ...archesCoreJavascriptRelativeFilepathToAbsoluteFilepathLookup,
                ...projectJavascriptRelativeFilepathToAbsoluteFilepathLookup 
            };
            
            const { ARCHES_CORE_NODE_MODULES_ALIASES } = require(Path.resolve(__dirname, ROOT_DIR, 'webpack', 'webpack-node-modules-aliases.js'));
            const parsedArchesCoreNodeModulesAliases = Object.entries(JSON.parse(ARCHES_CORE_NODE_MODULES_ALIASES)).reduce((acc, [alias, executeableString]) => {
                // eval() should be safe here, it's running developer-defined code during build
                acc[alias] = eval(executeableString);
                return acc;
            }, {});

            let parsedProjectNodeModulesAliases = {};
            if (PROJECT_NODE_MODULES_ALIASES) {
                parsedProjectNodeModulesAliases = Object.entries(JSON.parse(PROJECT_NODE_MODULES_ALIASES)).reduce((acc, [alias, executeableString]) => {
                    // eval() should be safe here, it's running developer-defined code during build
                    acc[alias] = eval(executeableString);
                    return acc;
                }, {});
                
            }
            
            const nodeModulesAliases = {
                ...parsedArchesCoreNodeModulesAliases,
                ...parsedProjectNodeModulesAliases
            };
            
            const templateFilepathLookup = buildTemplateFilePathLookup(
                Path.resolve(__dirname, ROOT_DIR, 'app', 'templates'),
                Path.resolve(__dirname, APP_ROOT, 'templates')
            );
            
            const imageFilepathLookup = buildImageFilePathLookup(
                STATIC_URL,
                Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'img'),
                Path.resolve(__dirname, APP_ROOT, 'media', 'img')
            );
            
            resolve({
                entry: { 
                    ...archesCoreEntryPointConfiguration,
                    ...projectEntryPointConfiguration 
                },
                output: {
                    path: Path.resolve(__dirname, APP_ROOT, 'media', 'build'),
                    publicPath: STATIC_URL,
                    libraryTarget: 'amd-require',
                    clean: true,
                },
                plugins: [
                    new CleanWebpackPlugin(),
                    new webpack.DefinePlugin({
                        ARCHES_CORE_DIRECTORY: `'${ROOT_DIR}'`,
                        APP_ROOT_DIRECTORY: `'${APP_ROOT}'`
                    }),
                    new webpack.ProvidePlugin({
                        jquery:  Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', 'jquery', 'dist', 'jquery.min'),
                        jQuery:  Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', 'jquery', 'dist', 'jquery.min'),
                        $:  Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', 'jquery', 'dist', 'jquery.min')
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
                    modules: [Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules')],
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
                            loader: Path.join(APP_ROOT, 'media', 'node_modules', 'babel-loader'),
                            options: {
                                presets: ['@babel/preset-env'],
                                cacheDirectory: Path.join(APP_ROOT, 'media', 'node_modules', '.cache', 'babel-loader'),
                            }
                        },
                        {
                            test: /\.s?css$/i,
                            use: [
                                {
                                    'loader': MiniCssExtractPlugin.loader,
                                },
                                {
                                    'loader': Path.join(APP_ROOT, 'media', 'node_modules', 'css-loader'),
                                },
                                {
                                    'loader': Path.join(APP_ROOT, 'media', 'node_modules', 'postcss-loader'),
                                },
                                {
                                    'loader': Path.join(APP_ROOT, 'media', 'node_modules', 'sass-loader'),
                                }
                            ],
                        },
                        {
                            test: /\.html?$/i,
                            loader: Path.join(APP_ROOT, 'media', 'node_modules', 'html-loader'),
                            options: {
                                esModule: false,
                                minimize: {
                                    removeComments: false,
                                },
                                preprocessor: async (content, loaderContext) => {
                                    const resourcePath = loaderContext['resourcePath'];
                                    const projectResourcePathData = resourcePath.split(APP_ROOT);
                                    const templatePath = projectResourcePathData.length > 1 ? projectResourcePathData[1] : resourcePath.split(Path.join(ROOT_DIR, 'app'))[1]; 

                                    let isTestEnvironment = false;

                                    for (let arg of process.argv) {
                                        const keyValuePair = arg.split('=');
                                        const key = keyValuePair[0].toLowerCase();
                                    
                                        if (key === 'test') {
                                            isTestEnvironment = true;
                                        }
                                    }

                                    let resp;
                                    
                                    console.log(`Loading "${templatePath}" from Django server...`)
            
                                    const renderTemplate = async(failureCount=0) => {
                                        /*
                                            Sometimes Django can choke on the number of requests, this function will 
                                            continue attempting to render the template until successful or 5 failures.
                                        */ 
                                        if (failureCount < 5) {
                                            try {
                                                let serverAddress = ARCHES_NAMESPACE_FOR_DATA_EXPORT;
                                                if (serverAddress.charAt(serverAddress.length - 1) === '/') {
                                                    serverAddress = serverAddress.slice(0, -1)
                                                }
                                                resp = await fetch(serverAddress + templatePath);
                                            }
                                            catch(e) { 
                                                failureCount += 1;
                                                console.warn(
                                                    '\x1b[33m%s\x1b[0m',  // yellow
                                                    `"${templatePath}" has failed to load. Retrying (${failureCount} / 5)...`
                                                );
                                                return await renderTemplate(failureCount=failureCount);
                                            }
                                        }
                                        else {
                                            console.error(
                                                '\x1b[31m%s\x1b[0m',  // yellow
                                                `"${templatePath}" has failed to load! Falling back to un-rendered file.`
                                            );
                                            resp = {
                                               text: () => (
                                                    new Promise((resolve, _reject) => {
                                                        /*
                                                            if run in a test environment, failures will return a empty string which will
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
                            test: /\.(txt|DS_Store)$/i,
                            use: Path.join(APP_ROOT, 'media', 'node_modules', 'raw-loader'),
                        },
                        {
                            test: /\.(png|svg|jpg|jpeg|gif)$/i,
                            type: 'asset/resource',
                        },
                    ],
                },
            });
        };

        let projectSettings = spawn(
            'python3',
            [Path.resolve(__dirname, Path.parse(__dirname)['dir'], 'settings.py')]
        );
        projectSettings.stderr.on("data", process.stderr.write);
        projectSettings.stdout.on("data", createWebpackConfig);

        projectSettings.on('error', () => {
            projectSettings = spawn(
                'python',
                [Path.resolve(__dirname, Path.parse(__dirname)['dir'], 'settings.py')]
            );
            projectSettings.stderr.on("data", process.stderr.write);
            projectSettings.stdout.on("data", createWebpackConfig);
        });

    });
};
