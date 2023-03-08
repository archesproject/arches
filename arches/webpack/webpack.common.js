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
            console.log('Data imported from settings.py:', parsedData)
            
            const APP_ROOT = parsedData['APP_ROOT'];
            const INSTALLED_PACKAGES = parsedData['INSTALLED_PACKAGES'];
            const INSTALLED_PACKAGES_PATH = parsedData['INSTALLED_PACKAGES_PATH'];
            const ROOT_DIR = parsedData['ROOT_DIR'];
            const STATIC_URL = parsedData['STATIC_URL']
            const PUBLIC_SERVER_ADDRESS = parsedData['PUBLIC_SERVER_ADDRESS']
            const WEBPACK_DEVELOPMENT_SERVER_PORT = parsedData['WEBPACK_DEVELOPMENT_SERVER_PORT']

            // BEGIN create entry point configurations
        
            const archesCoreEntryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'js'), {});
            const projectEntryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, APP_ROOT, 'media', 'js'), {});

            const installedPackagesEntrypointConfiguration = INSTALLED_PACKAGES.reduce((acc, installedPackage) => {                
                return {
                    ...acc,
                    ...buildJavascriptFilepathLookup(Path.resolve(__dirname, INSTALLED_PACKAGES_PATH, installedPackage, 'media', 'js'), {})
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
            const installedPackagesJavascriptRelativeFilepathToAbsoluteFilepathLookup = Object.entries(installedPackagesEntrypointConfiguration).reduce((acc, [path, config]) => {
                acc[path + '$'] = Path.resolve(__dirname, path, config['import']);
                return acc;
            }, {});

            // order is important! Arches core files are overwritten by project files, project files are overwritten by installedPackage files
            const javascriptRelativeFilepathToAbsoluteFilepathLookup = { 
                ...archesCoreJavascriptRelativeFilepathToAbsoluteFilepathLookup,
                ...projectJavascriptRelativeFilepathToAbsoluteFilepathLookup,
                ...installedPackagesJavascriptRelativeFilepathToAbsoluteFilepathLookup
            };

            // END create JavaScript filepath lookups
            // BEGIN create node modules aliases
            
            const { ARCHES_CORE_NODE_MODULES_ALIASES } = require(Path.resolve(__dirname, ROOT_DIR, 'webpack', 'webpack-node-modules-aliases.js'));
            const parsedArchesCoreNodeModulesAliases = Object.entries(JSON.parse(ARCHES_CORE_NODE_MODULES_ALIASES)).reduce((acc, [alias, executeableString]) => {
                // eval() should be safe here, it's running developer-defined code during build
                acc[alias] = eval(executeableString);
                return acc;
            }, {});

            let parsedProjectNodeModulesAliases = {};
            if (PROJECT_NODE_MODULES_ALIASES) {
                parsedProjectNodeModulesAliases = Object.entries(JSON.parse(PROJECT_NODE_MODULES_ALIASES)).reduce((acc, [alias, executeableString]) => {
                    if (parsedArchesCoreNodeModulesAliases[alias]) {
                        console.warn(
                            '\x1b[33m%s\x1b[0m',  // yellow
                            `"${alias}" has failed to load, it has already been defined in the Arches application.`
                        )
                    }
                    else {
                        // eval() should be safe here, it's running developer-defined code during build
                        acc[alias] = eval(executeableString);
                    }
                    return acc;
                }, {});
            }

            let parsedInstalledPackagesNodeModulesAliases = {};
            for (const installedPackage of INSTALLED_PACKAGES) {
                try {
                    const { installedPackageNodeModuleAliases } = require(
                        Path.resolve(__dirname, INSTALLED_PACKAGES_PATH, installedPackage, 'webpack', 'webpack-node-modules-aliases.js')
                    );
                    
                    for (const [alias, executeableString] of Object.entries(JSON.parse(installedPackageNodeModuleAliases))) {
                        if (
                            parsedArchesCoreNodeModulesAliases[alias]
                            || parsedProjectNodeModulesAliases[alias]
                            || parsedArchesCoreNodeModulesAliases[alias]
                        ) {
                            console.warn(
                                '\x1b[33m%s\x1b[0m',  // yellow
                                `"${alias}" has failed to load, it has already been defined in the project, another installed package, or the Arches application.`
                            )
                        }
                        else {
                            // eval() should be safe here, it's running developer-defined code during build
                            parsedInstalledPackagesNodeModulesAliases[alias] = eval(executeableString);
                        }
                    }
                } catch (error) {
                    continue;
                }
            }
            
            // order is important! Arches core files are overwritten by project files, project files are overwritten by installedPackage files
            const nodeModulesAliases = {
                ...parsedArchesCoreNodeModulesAliases,
                ...parsedProjectNodeModulesAliases,
                ...parsedInstalledPackagesNodeModulesAliases
            };

            // END create node modules aliases
            // BEGIN create template filepath lookup
            
            const coreArchesTemplatePathConfiguration = buildTemplateFilePathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'templates'), {});
            const projectTemplatePathConfiguration = buildTemplateFilePathLookup(Path.resolve(__dirname, APP_ROOT, 'templates'), {});

            const installedPackagesTemplatePathConfiguration = INSTALLED_PACKAGES.reduce((acc, installedPackage) => {                
                return {
                    ...acc,
                    ...buildTemplateFilePathLookup(Path.resolve(__dirname, INSTALLED_PACKAGES_PATH, installedPackage, 'templates'), {})
                };
            }, {});

            // order is important! Arches core files are overwritten by project files, project files are overwritten by installedPackage files
            const templateFilepathLookup = { 
                ...coreArchesTemplatePathConfiguration,
                ...projectTemplatePathConfiguration,
                ...installedPackagesTemplatePathConfiguration
            };

            // END create template filepath lookup
            // BEGIN create image filepath lookup

            const coreArchesImagePathConfiguration = buildImageFilePathLookup(STATIC_URL, Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'img'), {});
            const projectImagePathConfiguration = buildImageFilePathLookup(STATIC_URL, Path.resolve(__dirname, APP_ROOT, 'media', 'img'), {});

            const installedPackagesImagePathConfiguration = INSTALLED_PACKAGES.reduce((acc, installedPackage) => {                
                return {
                    ...acc,
                    ...buildImageFilePathLookup(STATIC_URL, Path.resolve(__dirname, INSTALLED_PACKAGES_PATH, installedPackage, 'media', 'img'), {})
                };
            }, {});

            // order is important! Arches core files are overwritten by project files, project files are overwritten by installedPackage files
            const imageFilepathLookup = { 
                ...coreArchesImagePathConfiguration,
                ...projectImagePathConfiguration,
                ...installedPackagesImagePathConfiguration
            };

            // END create image filepath lookup
            
            resolve({
                entry: { 
                    ...archesCoreEntryPointConfiguration,
                    ...projectEntryPointConfiguration,
                    ...installedPackagesEntrypointConfiguration
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
                        APP_ROOT_DIRECTORY: JSON.stringify(APP_ROOT),
                        ARCHES_CORE_DIRECTORY: JSON.stringify(ROOT_DIR),
                        INSTALLED_PACKAGES: JSON.stringify(INSTALLED_PACKAGES),
                        INSTALLED_PACKAGES_DIRECTORY: JSON.stringify(INSTALLED_PACKAGES_PATH)
                    }),
                    new webpack.ProvidePlugin({
                        $:  Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', 'jquery', 'dist', 'jquery.min'),
                        jQuery:  Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', 'jquery', 'dist', 'jquery.min'),
                        jquery:  Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', 'jquery', 'dist', 'jquery.min')
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
                            exclude: [/node_modules/, /load-component-dependencies/],
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

                                    let templatePath;
                                    if (resourcePath.includes(INSTALLED_PACKAGES_PATH)) {  // installed package component
                                        const packagePath = resourcePath.split(INSTALLED_PACKAGES_PATH)[1];  // first split off installed packages path
                                        const [_emptyValueBeforeFirstSlash, _packageName, ...subPath] = packagePath.split('/') // then split off package name
                                        templatePath = '/' + subPath.join('/');
                                    }
                                    else if (resourcePath.includes(APP_ROOT)) {  // project-level component
                                        templatePath = resourcePath.split(APP_ROOT)[1];
                                    }
                                    else {  // arches core component
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
