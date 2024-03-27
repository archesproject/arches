/* eslint-disable */

const fetch = require('cross-fetch');
const fs = require('fs');
const Path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');

const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const { spawn } = require("child_process");
const { VueLoaderPlugin } = require("vue-loader");

const { buildImageFilePathLookup } = require('./webpack-utils/build-image-filepath-lookup');
const { buildJavascriptFilepathLookup } = require('./webpack-utils/build-javascript-filepath-lookup');
const { buildTemplateFilePathLookup } = require('./webpack-utils/build-template-filepath-lookup');
const { buildCSSFilepathLookup } = require('./webpack-utils/build-css-filepath-lookup');

module.exports = () => {
    return new Promise((resolve, _reject) => {
        const createWebpackConfig = function(data) {  // reads from application's settings.py
            if (!data) {
                console.error(
                    '\x1b[31m%s\x1b[0m',  // red
                    "Webpack did not receive application data! Aborting..."
                )
                return;
            }
            // prevents subsequent builds, this usually happens when using application containers.
            projectSettings.stdout.removeAllListeners()

            const parsedData = JSON.parse(data);
            console.log('Data imported from settings.py:', parsedData)
            
            const APP_ROOT = parsedData['APP_ROOT'];
            const ARCHES_APPLICATIONS = parsedData['ARCHES_APPLICATIONS'];
            const ARCHES_APPLICATIONS_PATHS = parsedData['ARCHES_APPLICATIONS_PATHS'];
            const SITE_PACKAGES_DIRECTORY = parsedData['SITE_PACKAGES_DIRECTORY'];
            const ROOT_DIR = parsedData['ROOT_DIR'];
            const STATIC_URL = parsedData['STATIC_URL']
            const PUBLIC_SERVER_ADDRESS = parsedData['PUBLIC_SERVER_ADDRESS']
            const WEBPACK_DEVELOPMENT_SERVER_PORT = parsedData['WEBPACK_DEVELOPMENT_SERVER_PORT']

            // BEGIN create entry point configurations
        
            const archesCoreEntryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'js'), {});
            const projectEntryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, APP_ROOT, 'media', 'js'), {});

            const archesApplicationsEntrypointConfiguration = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => {   
                return {
                    ...acc,
                    ...buildJavascriptFilepathLookup(Path.resolve(__dirname, ARCHES_APPLICATIONS_PATHS[archesApplication], 'media', 'js'), {})
                };
            }, {});

            // END create entry point configurations
            // BEGIN create JavaScript filepath lookups

            const archesCoreJavascriptRelativeFilepathToAbsoluteFilepathLookup = Object.entries(archesCoreEntryPointConfiguration).reduce((acc, [path, config]) => {
                acc[path + '$'] = Path.resolve(__dirname, path, config['import']);
                return acc;
            }, {});
            const projectJavascriptRelativeFilepathToAbsoluteFilepathLookup = Object.entries(projectEntryPointConfiguration).reduce((acc, [path, config]) => {
                acc[path + '$'] = Path.resolve(__dirname, path, config['import']);
                return acc;
            }, {});
            const archesApplicationsJavascriptRelativeFilepathToAbsoluteFilepathLookup = Object.entries(archesApplicationsEntrypointConfiguration).reduce((acc, [path, config]) => {
                acc[path + '$'] = Path.resolve(__dirname, path, config['import']);
                return acc;
            }, {});

            // order is important! Arches core files are overwritten by arches-application files, arches-application files are overwritten by project files
            const javascriptRelativeFilepathToAbsoluteFilepathLookup = { 
                ...archesCoreJavascriptRelativeFilepathToAbsoluteFilepathLookup,
                ...archesApplicationsJavascriptRelativeFilepathToAbsoluteFilepathLookup,
                ...projectJavascriptRelativeFilepathToAbsoluteFilepathLookup,
            };

            // END create JavaScript filepath lookups
            // BEGIN create node modules aliases
            const parsedPackageJSONFilepaths = {};

            let archesCorePackageJSONFilepath = Path.resolve(__dirname, ROOT_DIR, '../package.json')
            if (!fs.existsSync(archesCorePackageJSONFilepath)) {
                archesCorePackageJSONFilepath = Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', 'arches', 'package.json')
            }

            const archesCorePackageJSON = require(archesCorePackageJSONFilepath);
            parsedPackageJSONFilepaths[Path.join(archesCorePackageJSON.name, 'package.json').replace(/\\/g, '/')] = archesCorePackageJSONFilepath;

            const parsedArchesCoreNodeModulesAliases = Object.entries(archesCorePackageJSON['nodeModulesPaths']).reduce((acc, [alias, subPath]) => {
                if (subPath.slice(0, 7) === 'plugins') {  // handles for node_modules -esque plugins in arches core
                    acc[alias] = Path.resolve(__dirname, ROOT_DIR, 'app', 'media', subPath);
                }
                else {
                    acc[alias] = Path.resolve(__dirname, APP_ROOT, 'media', subPath);
                }
                return acc;
            }, {});

            let parsedProjectNodeModulesAliases = {};
            let projectPackageJSON;

            const projectJSONFilepath = Path.resolve(__dirname, APP_ROOT, 'package.json');
            if (fs.existsSync(projectJSONFilepath)) {  // handles running Arches without a project
                projectPackageJSON = require(projectJSONFilepath);
                parsedPackageJSONFilepaths[Path.join(projectPackageJSON.name, 'package.json').replace(/\\/g, '/')] = projectJSONFilepath;

                parsedProjectNodeModulesAliases = Object.entries(projectPackageJSON['nodeModulesPaths']).reduce((acc, [alias, subPath]) => {
                    if (parsedArchesCoreNodeModulesAliases[alias]) {
                        console.warn(
                            '\x1b[33m%s\x1b[0m',  // yellow
                            `"${alias}" has failed to load, it has already been defined in the Arches application.`
                        )
                    }
                    else {
                        acc[alias] = Path.resolve(__dirname, APP_ROOT, 'media', subPath);
                    }
                    return acc;
                }, {});
            }

            let parsedArchesApplicationsNodeModulesAliases = {};
            for (const archesApplication of ARCHES_APPLICATIONS) {
                try {
                    let archesApplicationJSONFilepath;

                    if (!ARCHES_APPLICATIONS_PATHS[archesApplication].includes('site-packages')) {  
                        // if the path doesn't include site-packages then we can assume it's linked via egg/wheel
                        archesApplicationJSONFilepath = Path.resolve(__dirname, ARCHES_APPLICATIONS_PATHS[archesApplication], '..', 'package.json');
                    }
                    else {
                        archesApplicationJSONFilepath = Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', archesApplication, 'package.json')
                    }
                    
                    const archesApplicationPackageJSON = require(archesApplicationJSONFilepath);
                    parsedPackageJSONFilepaths[Path.join(archesApplicationPackageJSON.name, 'package.json').replace(/\\/g, '/')] = archesApplicationJSONFilepath;

                    for (const [alias, subPath] of Object.entries(archesApplicationPackageJSON['nodeModulesPaths'])) {
                        if (
                            parsedArchesApplicationsNodeModulesAliases[alias]
                            || parsedProjectNodeModulesAliases[alias]
                            || parsedArchesCoreNodeModulesAliases[alias]
                        ) {
                            console.warn(
                                '\x1b[33m%s\x1b[0m',  // yellow
                                `"${alias}" is already loaded! It has might have been defined in the project, another arches application, or the Arches software.`
                            )
                        }
                        else {
                            parsedArchesApplicationsNodeModulesAliases[alias] = Path.resolve(__dirname, APP_ROOT, 'media', subPath);
                        }
                    }
                } catch (error) {
                    continue;
                }
            }

            // order is important! Arches core files are overwritten by arches-application files, arches-application files are overwritten by project files
            const nodeModulesAliases = {
                ...parsedArchesCoreNodeModulesAliases,
                ...parsedArchesApplicationsNodeModulesAliases,
                ...parsedProjectNodeModulesAliases,
            };

            // END create node modules aliases
            // BEGIN create template filepath lookup
            
            const coreArchesTemplatePathConfiguration = buildTemplateFilePathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'templates'), {});
            const projectTemplatePathConfiguration = buildTemplateFilePathLookup(Path.resolve(__dirname, APP_ROOT, 'templates'), {});

            const archesApplicationsTemplatePathConfiguration = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => {   
                return {
                    ...acc,
                    ...buildTemplateFilePathLookup(Path.resolve(__dirname, ARCHES_APPLICATIONS_PATHS[archesApplication], 'templates'), {})
                };
            }, {});

            // order is important! Arches core files are overwritten by arches-application files, arches-application files are overwritten by project files
            const templateFilepathLookup = { 
                ...coreArchesTemplatePathConfiguration,
                ...archesApplicationsTemplatePathConfiguration,
                ...projectTemplatePathConfiguration,
            };

            // END create template filepath lookup
            // BEGIN create image filepath lookup

            const coreArchesImagePathConfiguration = buildImageFilePathLookup(STATIC_URL, Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'img'), {});
            const projectImagePathConfiguration = buildImageFilePathLookup(STATIC_URL, Path.resolve(__dirname, APP_ROOT, 'media', 'img'), {});

            const archesApplicationsImagePathConfiguration = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => {   
                return {
                    ...acc,
                    ...buildImageFilePathLookup(STATIC_URL, Path.resolve(__dirname, ARCHES_APPLICATIONS_PATHS[archesApplication], 'media', 'img'), {})
                };
            }, {});

            // order is important! Arches core files are overwritten by arches-application files, arches-application files are overwritten by project files
            const imageFilepathLookup = { 
                ...coreArchesImagePathConfiguration,
                ...archesApplicationsImagePathConfiguration,
                ...projectImagePathConfiguration,
            };

            // END create image filepath lookup
            // BEGIN create CSS filepath lookup

            const coreArchesCSSFilepathConfiguration = buildCSSFilepathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'css'), {});
            const projectCSSFilepathConfiguration = buildCSSFilepathLookup(Path.resolve(__dirname, APP_ROOT, 'media', 'css'), {});

            const archesApplicationsCSSFilepaths = [];
            const archesApplicationsCSSFilepathConfiguration = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => { 
                const path = Path.resolve(__dirname, ARCHES_APPLICATIONS_PATHS[archesApplication], 'media', 'css');
                archesApplicationsCSSFilepaths.push(path);

                return {
                    ...acc,
                    ...buildCSSFilepathLookup(path, {})
                };
            }, {});

            const CSSFilepathLookup = {
                ...coreArchesCSSFilepathConfiguration,
                ...archesApplicationsCSSFilepathConfiguration,
                ...projectCSSFilepathConfiguration,
            };

            // END create CSS filepath lookup
            // BEGIN create vue filepath lookup

            const archesApplicationsVuePaths = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => { 
                const path = Path.resolve(__dirname, ARCHES_APPLICATIONS_PATHS[archesApplication], 'src');
                acc.push(path);
                
                return acc;
            }, []);

            // END create vue filepath lookup
            // BEGIN create universal constants

            const universalConstants = {
                APP_ROOT_DIRECTORY: JSON.stringify(APP_ROOT).replace(/\\/g ,'/'),
                ARCHES_CORE_DIRECTORY: JSON.stringify(ROOT_DIR).replace(/\\/g ,'/'),
                ARCHES_APPLICATIONS: JSON.stringify(ARCHES_APPLICATIONS),
                SITE_PACKAGES_DIRECTORY: JSON.stringify(SITE_PACKAGES_DIRECTORY).replace(/\\/g ,'/'),
            };

            let linkedApplicationPathCount = 0;
            for (const archesApplication of ARCHES_APPLICATIONS) {
                if (!ARCHES_APPLICATIONS_PATHS[archesApplication].includes('site-packages')) {
                    universalConstants[`LINKED_APPLICATION_PATH_${linkedApplicationPathCount}`] = JSON.stringify(
                        ARCHES_APPLICATIONS_PATHS[archesApplication]
                    ).replace(/\\/g ,'/');
                    linkedApplicationPathCount += 1;
                }
            }

            // END create universal constants
            
            resolve({
                entry: { 
                    ...archesCoreEntryPointConfiguration,
                    ...archesApplicationsEntrypointConfiguration,
                    ...projectEntryPointConfiguration,
                    ...CSSFilepathLookup,
                },
                devServer: {
                    port: WEBPACK_DEVELOPMENT_SERVER_PORT,
                },
                output: {
                    path: Path.resolve(__dirname, APP_ROOT, 'media', 'build'),
                    publicPath: STATIC_URL,
                    libraryTarget: 'amd-require',
                    clean: true,
                    assetModuleFilename: 'img/[hash][ext][query]',
                },
                plugins: [
                    new CleanWebpackPlugin(),
                    new webpack.DefinePlugin(universalConstants),
                    new webpack.DefinePlugin({
                        __VUE_OPTIONS_API__: 'true',
                        __VUE_PROD_DEVTOOLS__: 'false',
                        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false'
                    }),
                    new webpack.ProvidePlugin({
                        $:  Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', 'jquery', 'dist', 'jquery.min'),
                        jQuery:  Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', 'jquery', 'dist', 'jquery.min'),
                        jquery:  Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', 'jquery', 'dist', 'jquery.min')
                    }),
                    new MiniCssExtractPlugin(),
                    new BundleTracker({ filename: Path.resolve(__dirname, `webpack-stats.json`) }),
                    new VueLoaderPlugin(),
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
                        ...parsedPackageJSONFilepaths,
                        '@': [Path.resolve(__dirname, APP_ROOT, 'src'), ...archesApplicationsVuePaths, Path.resolve(__dirname, ROOT_DIR, 'app', 'src')],
                        'node_modules': Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules')
                    },
                },
                module: {
                    rules: [
                        {
                            test: /\.tsx?$/,
                            exclude: /node_modules/,
                            loader: Path.join(APP_ROOT, 'media', 'node_modules', 'ts-loader'),
                            options: { 
                                appendTsSuffixTo: [/\.vue$/],
                                transpileOnly: true
                            }
                        },
                        {
                            test: /\.vue$/,
                            exclude: /node_modules/,
                            loader:Path.join(APP_ROOT, 'media', 'node_modules', 'vue-loader'),
                        },
                        {
                            test: /\.mjs$/,
                            include: /node_modules/,
                            type: 'javascript/auto',
                        },
                        {
                            test: /\.js$/,
                            exclude: [/node_modules/, /load-component-dependencies/],
                            loader: Path.join(APP_ROOT, 'media', 'node_modules', 'babel-loader'),
                            options: {
                                presets: ['@babel/preset-env'],
                                cacheDirectory: Path.join(APP_ROOT, 'media', 'node_modules', '.cache', 'babel-loader'),
                            }
                        },
                        {
                            test: /\.css$/,
                            exclude: [
                                /node_modules/,
                                Path.resolve(__dirname, APP_ROOT, 'media', 'css'),
                                Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'css'),
                                ...archesApplicationsCSSFilepaths
                            ],
                            use: [
                                {
                                    'loader': Path.join(APP_ROOT, 'media', 'node_modules', 'style-loader'),
                                },
                                {
                                    'loader': Path.join(APP_ROOT, 'media', 'node_modules', 'css-loader'),
                                },
                            ],
                        },
                        {
                            test: /\.s?css$/i,
                            exclude: [
                                /node_modules/,
                                Path.resolve(__dirname, APP_ROOT, 'src'),
                                Path.resolve(__dirname, ROOT_DIR, 'app', 'src'),
                                ...archesApplicationsVuePaths,
                            ],
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
                                    options: {
                                        sassOptions: {
                                            indentWidth: 4,
                                            includePaths: [
                                                Path.resolve(__dirname, APP_ROOT, 'media', 'css'),
                                                ...archesApplicationsCSSFilepaths,
                                                Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'css'),
                                            ],
                                        },
                                    },
                                }
                            ],
                        },
                        {
                            test: /\.html?$/i,
                            exclude: /node_modules/,
                            loader: Path.join(APP_ROOT, 'media', 'node_modules', 'html-loader'),
                            options: {
                                esModule: false,
                                minimize: {
                                    removeComments: false,
                                },
                                preprocessor: async (content, loaderContext) => {
                                    const resourcePath = loaderContext['resourcePath'];

                                    let templatePath;

                                    if (resourcePath.includes(APP_ROOT)) {  // project-level component
                                        templatePath = resourcePath.split(APP_ROOT)[1];
                                    }

                                    for (const archesApplicationPath of Object.values(ARCHES_APPLICATIONS_PATHS)) {  // arches application component
                                        if (!templatePath && resourcePath.includes(archesApplicationPath)) {
                                            templatePath = resourcePath.split(archesApplicationPath)[1];
                                        }
                                    }

                                    if (!templatePath) {  // arches core component
                                        templatePath = resourcePath.split(Path.join(ROOT_DIR, 'app'))[1];
                                    }

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
                                                let serverAddress = PUBLIC_SERVER_ADDRESS;
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
                                                '\x1b[31m%s\x1b[0m',  // red
                                                `"${templatePath}" has failed to load! Falling back to un-rendered file.`
                                            );
                                            resp = {
                                               text: () => (
                                                    new Promise((resolve, _reject) => {
                                                        /*
                                                            if run in a test environment, failures will return a empty string which will
                                                            still allow the bundle to build.
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
                            exclude: /node_modules/,
                            use: Path.join(APP_ROOT, 'media', 'node_modules', 'raw-loader'),
                        },
                        {
                            test: /\.(png|svg|jpg|jpeg|gif)$/i,
                            exclude: /node_modules/,
                            type: 'asset/resource',
                        },
                    ],
                },
            });
        };

        let projectSettings = spawn(
            'python',
            [Path.resolve(__dirname, Path.parse(__dirname)['dir'], 'settings.py')]
        );
        projectSettings.stderr.on("data", process.stderr.write);
        projectSettings.stdout.on("data", createWebpackConfig);

        projectSettings.on('error', () => {
            projectSettings = spawn(
                'python3',
                [Path.resolve(__dirname, Path.parse(__dirname)['dir'], 'settings.py')]
            );
            projectSettings.stderr.on("data", process.stderr.write);
            projectSettings.stdout.on("data", createWebpackConfig);
        });

    });
};
