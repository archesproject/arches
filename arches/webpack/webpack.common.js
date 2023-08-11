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

const { buildTemplateFilePathLookup } = require('./webpack-utils/build-template-filepath-lookup');
const { buildJavascriptFilepathLookup } = require('./webpack-utils/build-javascript-filepath-lookup');
const { buildImageFilePathLookup } = require('./webpack-utils/build-image-filepath-lookup');
const { buildVueFilePathLookup } = require('./webpack-utils/build-vue-filepath-lookup');
const { PROJECT_NODE_MODULES_ALIASES } = require('./webpack-node-modules-aliases');


module.exports = () => {
    return new Promise((resolve, _reject) => {
        const createWebpackConfig = function(data) {  // reads from application's settings.py
            const parsedData = JSON.parse(data);
            console.log('Data imported from settings.py:', parsedData)
            
            const APP_ROOT = parsedData['APP_ROOT'];
            const ARCHES_APPLICATIONS = parsedData['ARCHES_APPLICATIONS'];
            const ARCHES_APPLICATIONS_PATH = parsedData['ARCHES_APPLICATIONS_PATH'];
            const ROOT_DIR = parsedData['ROOT_DIR'];
            const STATIC_URL = parsedData['STATIC_URL']
            const PUBLIC_SERVER_ADDRESS = parsedData['PUBLIC_SERVER_ADDRESS']
            const WEBPACK_DEVELOPMENT_SERVER_PORT = parsedData['WEBPACK_DEVELOPMENT_SERVER_PORT']

            // BEGIN build config to handle eggfiles
            let eggFilePaths;

            try {
                eggFilePaths = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => {   
                    const archesApplicationEggFile = archesApplication.replaceAll('_', '-').concat('.egg-link'); 

                    let updatedFilepath = fs.readFileSync(
                        Path.resolve(__dirname, ARCHES_APPLICATIONS_PATH, archesApplicationEggFile), { encoding: 'utf8' }
                    )
                    updatedFilepath = updatedFilepath.replace(/(\r\n|\n|\r)/gm, "");  // remove newlines
                    updatedFilepath = updatedFilepath.replace(/\./g, "");  // remove dots

                    return {
                        ...acc,
                        [archesApplication]: updatedFilepath,
                    }
                }, {});
            }
            catch{}

            // END build config to handle eggfiles

            // BEGIN create entry point configurations
        
            const archesCoreEntryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'js'), {});
            const projectEntryPointConfiguration = buildJavascriptFilepathLookup(Path.resolve(__dirname, APP_ROOT, 'media', 'js'), {});

            const archesApplicationsEntrypointConfiguration = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => {   
                let filepath = Path.resolve(__dirname, ARCHES_APPLICATIONS_PATH, archesApplication, 'media', 'js');

                if (eggFilePaths && archesApplication in eggFilePaths) {
                    filepath = Path.resolve(__dirname, eggFilePaths[archesApplication], archesApplication, 'media', 'js');
                }
                return {
                    ...acc,
                    ...buildJavascriptFilepathLookup(filepath, {})
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

            // order is important! Arches core files are overwritten by project files, project files are overwritten by archesApplication files
            const javascriptRelativeFilepathToAbsoluteFilepathLookup = { 
                ...archesCoreJavascriptRelativeFilepathToAbsoluteFilepathLookup,
                ...projectJavascriptRelativeFilepathToAbsoluteFilepathLookup,
                ...archesApplicationsJavascriptRelativeFilepathToAbsoluteFilepathLookup
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

            let parsedArchesApplicationsNodeModulesAliases = {};
            for (const archesApplication of ARCHES_APPLICATIONS) {
                try {
                    let filepath = Path.resolve(__dirname, ARCHES_APPLICATIONS_PATH, archesApplication, 'webpack', 'webpack-node-modules-aliases.js')

                    if (eggFilePaths && archesApplication in eggFilePaths) {
                        filepath = Path.resolve(__dirname, eggFilePaths[archesApplication], archesApplication, 'webpack', 'webpack-node-modules-aliases.js');
                    }

                    const { ARCHES_APPLICATION_NODE_MODULES_ALIASES } = require(filepath);
                    
                    for (const [alias, executeableString] of Object.entries(JSON.parse(ARCHES_APPLICATION_NODE_MODULES_ALIASES))) {
                        if (
                            parsedArchesApplicationsNodeModulesAliases[alias]
                            || parsedProjectNodeModulesAliases[alias]
                            || parsedArchesCoreNodeModulesAliases[alias]
                        ) {
                            console.warn(
                                '\x1b[33m%s\x1b[0m',  // yellow
                                `"${alias}" has failed to load, it has already been defined in the project, another arches application, or the Arches application.`
                            )
                        }
                        else {
                            // eval() should be safe here, it's running developer-defined code during build
                            parsedArchesApplicationsNodeModulesAliases[alias] = eval(executeableString);
                        }
                    }
                } catch (error) {
                    continue;
                }
            }

            // order is important! Arches core files are overwritten by project files, project files are overwritten by archesApplication files
            const nodeModulesAliases = {
                ...parsedArchesCoreNodeModulesAliases,
                ...parsedProjectNodeModulesAliases,
                ...parsedArchesApplicationsNodeModulesAliases
            };

            // END create node modules aliases
            // BEGIN create template filepath lookup
            
            const coreArchesTemplatePathConfiguration = buildTemplateFilePathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'templates'), {});
            const projectTemplatePathConfiguration = buildTemplateFilePathLookup(Path.resolve(__dirname, APP_ROOT, 'templates'), {});

            const archesApplicationsTemplatePathConfiguration = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => {   
                let filepath = Path.resolve(__dirname, ARCHES_APPLICATIONS_PATH, archesApplication, 'templates');

                if (eggFilePaths && archesApplication in eggFilePaths) {
                    filepath = Path.resolve(__dirname, eggFilePaths[archesApplication], archesApplication, 'templates');
                }

                return {
                    ...acc,
                    ...buildTemplateFilePathLookup(filepath, {})
                };
            }, {});

            // order is important! Arches core files are overwritten by project files, project files are overwritten by archesApplication files
            const templateFilepathLookup = { 
                ...coreArchesTemplatePathConfiguration,
                ...projectTemplatePathConfiguration,
                ...archesApplicationsTemplatePathConfiguration
            };

            // END create template filepath lookup
            // BEGIN create image filepath lookup

            const coreArchesImagePathConfiguration = buildImageFilePathLookup(STATIC_URL, Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'img'), {});
            const projectImagePathConfiguration = buildImageFilePathLookup(STATIC_URL, Path.resolve(__dirname, APP_ROOT, 'media', 'img'), {});

            const archesApplicationsImagePathConfiguration = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => {   
                let filepath = Path.resolve(__dirname, ARCHES_APPLICATIONS_PATH, archesApplication, 'media', 'img');

                if (eggFilePaths && archesApplication in eggFilePaths) {
                    filepath = Path.resolve(__dirname, eggFilePaths[archesApplication], archesApplication, 'media', 'img');
                }

                return {
                    ...acc,
                    ...buildImageFilePathLookup(STATIC_URL, filepath, {})
                };
            }, {});

            // order is important! Arches core files are overwritten by project files, project files are overwritten by archesApplication files
            const imageFilepathLookup = { 
                ...coreArchesImagePathConfiguration,
                ...projectImagePathConfiguration,
                ...archesApplicationsImagePathConfiguration
            };

            // END create image filepath lookup
            // BEGIN create vue filepath lookup
            
            const coreArchesVuePathConfiguration = buildVueFilePathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'frontend'), {});
            const projectVuePathConfiguration = buildVueFilePathLookup(Path.resolve(__dirname, APP_ROOT, 'frontend'), {});

            const archesApplicationsVuePathConfiguration = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => {                
                return {
                    ...acc,
                    ...buildVueFilePathLookup(Path.resolve(__dirname, ARCHES_APPLICATIONS_PATH, archesApplication, 'frontend'), {})
                };
            }, {});

            // order is important! Arches core files are overwritten by project files, project files are overwritten by archesApplication files
            const vueFilepathLookup = { 
                ...coreArchesVuePathConfiguration,
                ...projectVuePathConfiguration,
                ...archesApplicationsVuePathConfiguration
            };

            // END create vue filepath lookup
            // BEGIN create universal constants
            const universalConstants = {
                APP_ROOT_DIRECTORY: JSON.stringify(APP_ROOT).replace(/\\/g ,'/'),
                ARCHES_CORE_DIRECTORY: JSON.stringify(ROOT_DIR).replace(/\\/g ,'/'),
                ARCHES_APPLICATIONS: JSON.stringify(ARCHES_APPLICATIONS),
                ARCHES_APPLICATIONS_DIRECTORY: JSON.stringify(ARCHES_APPLICATIONS_PATH).replace(/\\/g ,'/'),
            }
            let eggFileCount = 0;
            for (const value of Object.values(eggFilePaths)) {
                universalConstants[`EGG_FILE_PATH_${eggFileCount}`] = JSON.stringify(value).replace(/\\/g ,'/');
                eggFileCount += 1;
            }
            // END create universal constants
            
            resolve({
                entry: { 
                    ...archesCoreEntryPointConfiguration,
                    ...projectEntryPointConfiguration,
                    ...archesApplicationsEntrypointConfiguration,
                    ...vueFilepathLookup,
                },
                devServer: {
                    port: WEBPACK_DEVELOPMENT_SERVER_PORT,
                },
                output: {
                    path: Path.resolve(__dirname, APP_ROOT, 'media', 'build'),
                    publicPath: STATIC_URL,
                    libraryTarget: 'amd-require',
                    clean: true,
                },
                plugins: [
                    new CleanWebpackPlugin(),
                    new webpack.DefinePlugin(universalConstants),
                    new webpack.ProvidePlugin({
                        $:  Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', 'jquery', 'dist', 'jquery.min'),
                        jQuery:  Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', 'jquery', 'dist', 'jquery.min'),
                        jquery:  Path.resolve(__dirname, APP_ROOT, 'media', 'node_modules', 'jquery', 'dist', 'jquery.min')
                    }),
                    new MiniCssExtractPlugin(),
                    new BundleTracker({ filename: Path.resolve(__dirname, `webpack-stats.json`) }),
                    new VueLoaderPlugin(),
                    {
                        apply: (compiler) => {
                            compiler.hooks.afterEmit.tap("webpack", () => {
                                fs.writeFile(
                                    Path.resolve(__dirname, APP_ROOT, 'media', 'build', '.gitignore'), 
                                    "# Ignore everything in this directory\n*\n# Except this file\n!.gitignore\n",
                                     err => {
                                        if (err) {
                                            console.error(
                                                '\x1b[31m%s\x1b[0m',  // red
                                                err
                                            );
                                        }
                                    }
                                );
                            });
                        },
                    },
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
                        ...vueFilepathLookup,
                        ...nodeModulesAliases,
                    },
                },
                module: {
                    rules: [
                        {
                            test: /\.vue$/,
                            loader: Path.join(APP_ROOT, 'media', 'node_modules', 'vue-loader'),
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
                            test: /\.scss$/i,
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

                                    if (eggFilePaths) {  // handles egg files
                                        for (const eggFilePath of Object.keys(eggFilePaths)) {
                                            if (resourcePath.includes(eggFilePath)) {
                                                templatePath = resourcePath.split(eggFilePath)[2];
                                            }
                                        }
                                    }

                                    if (!templatePath && resourcePath.includes(ARCHES_APPLICATIONS_PATH)) {  // arches application component
                                        const archesAppPath = resourcePath.split(ARCHES_APPLICATIONS_PATH)[1];  // first split off arches applications path
                                        const [_emptyValueBeforeFirstSlash, _appName, ...subPath] = archesAppPath.split('/') // then split off arches application name
                                        templatePath = '/' + subPath.join('/');
                                    }
                                    else if (!templatePath && resourcePath.includes(APP_ROOT)) {  // project-level component
                                        templatePath = resourcePath.split(APP_ROOT)[1];
                                    }
                                    else if (!templatePath) {  // arches core component
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
