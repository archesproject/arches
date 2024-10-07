/* eslint-disable */

const fetch = require('cross-fetch');
const fs = require('fs');
const Path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');

const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const { VueLoaderPlugin } = require("vue-loader");

const { buildFilepathLookup } = require('./webpack-utils/build-filepath-lookup');

module.exports = () => {
    return new Promise((resolve, _reject) => {
        // BEGIN get data from `.frontend-configuration-settings.json`

        const rawData = fs.readFileSync(Path.join(__dirname, "..", '.frontend-configuration-settings.json'), 'utf-8');
        const parsedData = JSON.parse(rawData);

        console.log('Data imported from .frontend-configuration-settings.json:', parsedData);
    
        global.APP_ROOT = parsedData['APP_ROOT'];
        global.ARCHES_APPLICATIONS = parsedData['ARCHES_APPLICATIONS'];
        global.ARCHES_APPLICATIONS_PATHS = parsedData['ARCHES_APPLICATIONS_PATHS'];
        global.SITE_PACKAGES_DIRECTORY = parsedData['SITE_PACKAGES_DIRECTORY'];
        global.ROOT_DIR = parsedData['ROOT_DIR'];
        global.STATIC_URL = parsedData['STATIC_URL'];
        global.PUBLIC_SERVER_ADDRESS = parsedData['PUBLIC_SERVER_ADDRESS'];
        global.WEBPACK_DEVELOPMENT_SERVER_PORT = parsedData['WEBPACK_DEVELOPMENT_SERVER_PORT'];

        // END get data from `.frontend-configuration-settings.json`
        // BEGIN workaround for handling node_modules paths in arches-core vs projects

        let PROJECT_RELATIVE_NODE_MODULES_PATH;
        if (APP_ROOT.includes(ROOT_DIR)) {  // should only return truthy for running Arches-core without a project
            PROJECT_RELATIVE_NODE_MODULES_PATH = Path.resolve(APP_ROOT, '..', '..', 'node_modules');
        }
        else {
            PROJECT_RELATIVE_NODE_MODULES_PATH = Path.resolve(APP_ROOT, '..', 'node_modules');
        }

        // END workaround for handling node_modules paths in arches-core vs projects
        // BEGIN create entry point configurations

        const archesCoreEntryPointConfiguration = buildFilepathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'js'));
        const projectEntryPointConfiguration = buildFilepathLookup(Path.resolve(__dirname, APP_ROOT, 'media', 'js'));

        const archesApplicationsEntrypointConfiguration = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => {
            return {
                ...acc,
                ...buildFilepathLookup(Path.resolve(__dirname, ARCHES_APPLICATIONS_PATHS[archesApplication], 'media', 'js'))
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

        let archesCorePackageJSONFilepath = Path.resolve(__dirname, ROOT_DIR, '..', 'package.json');
        if (!fs.existsSync(archesCorePackageJSONFilepath)) {
            archesCorePackageJSONFilepath = Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH, 'arches', 'package.json');
        }

        const archesCorePackageJSON = require(archesCorePackageJSONFilepath);
        parsedPackageJSONFilepaths[Path.join(archesCorePackageJSON.name, 'package.json').replace(/\\/g, '/')] = archesCorePackageJSONFilepath;

        const parsedArchesCoreNodeModulesAliases = Object.entries(archesCorePackageJSON['nodeModulesPaths']).reduce((acc, [alias, subPath]) => {
            if (subPath.slice(0, 7) === 'plugins') {  // handles for node_modules -esque plugins in arches core
                acc[alias] = Path.resolve(__dirname, ROOT_DIR, 'app', 'media', subPath);
            }
            else {
                acc[alias] = Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH, '..', subPath);
            }
            return acc;
        }, {});

        let parsedProjectNodeModulesAliases = {};
        let projectPackageJSON;

        const projectJSONFilepath = Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH, 'package.json');
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
                    acc[alias] = Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH, '..', subPath);
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
                    archesApplicationJSONFilepath = Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH, archesApplication, 'package.json');
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
                        parsedArchesApplicationsNodeModulesAliases[alias] = Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH, '..', subPath);
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

        const coreArchesTemplatePathConfiguration = buildFilepathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'templates'));
        const projectTemplatePathConfiguration = buildFilepathLookup(Path.resolve(__dirname, APP_ROOT, 'templates'));

        const archesApplicationsTemplatePathConfiguration = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => {
            return {
                ...acc,
                ...buildFilepathLookup(Path.resolve(__dirname, ARCHES_APPLICATIONS_PATHS[archesApplication], 'templates'))
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

        const coreArchesImagePathConfiguration = buildFilepathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'img'), STATIC_URL);
        const projectImagePathConfiguration = buildFilepathLookup(Path.resolve(__dirname, APP_ROOT, 'media', 'img'), STATIC_URL);

        const archesApplicationsImagePathConfiguration = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => {
            return {
                ...acc,
                ...buildFilepathLookup(Path.resolve(__dirname, ARCHES_APPLICATIONS_PATHS[archesApplication], 'media', 'img'), STATIC_URL)
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

        const coreArchesCSSFilepathConfiguration = buildFilepathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'css'));
        const projectCSSFilepathConfiguration = buildFilepathLookup(Path.resolve(__dirname, APP_ROOT, 'media', 'css'));

        const archesApplicationsCSSFilepaths = [];
        const archesApplicationsCSSFilepathConfiguration = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => {
            const path = Path.resolve(__dirname, ARCHES_APPLICATIONS_PATHS[archesApplication], 'media', 'css');
            archesApplicationsCSSFilepaths.push(path);

            return {
                ...acc,
                ...buildFilepathLookup(path)
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
            APP_ROOT_DIRECTORY: JSON.stringify(APP_ROOT).replace(/\\/g, '/'),
            ARCHES_CORE_DIRECTORY: JSON.stringify(ROOT_DIR).replace(/\\/g, '/'),
            ARCHES_APPLICATIONS: JSON.stringify(ARCHES_APPLICATIONS),
            SITE_PACKAGES_DIRECTORY: JSON.stringify(SITE_PACKAGES_DIRECTORY).replace(/\\/g, '/'),
        };

        let linkedApplicationPathCount = 0;
        for (const archesApplication of ARCHES_APPLICATIONS) {
            if (!ARCHES_APPLICATIONS_PATHS[archesApplication].includes('site-packages')) {
                universalConstants[`LINKED_APPLICATION_PATH_${linkedApplicationPathCount}`] = JSON.stringify(
                    ARCHES_APPLICATIONS_PATHS[archesApplication]
                ).replace(/\\/g, '/');
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
                    $: Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH, 'jquery', 'dist', 'jquery.min'),
                    jQuery: Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH, 'jquery', 'dist', 'jquery.min'),
                    jquery: Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH, 'jquery', 'dist', 'jquery.min')
                }),
                new MiniCssExtractPlugin(),
                new BundleTracker({ 
                    path: Path.resolve(__dirname),
                    filename: 'webpack-stats.json' 
                }),
                new VueLoaderPlugin(),
            ],
            resolveLoader: {
                alias: {
                    text: 'raw-loader'
                }
            },
            resolve: {
                modules: [Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH)],
                alias: {
                    ...javascriptRelativeFilepathToAbsoluteFilepathLookup,
                    ...templateFilepathLookup,
                    ...imageFilepathLookup,
                    ...nodeModulesAliases,
                    ...parsedPackageJSONFilepaths,
                    '@': [Path.resolve(__dirname, APP_ROOT, 'src'), ...archesApplicationsVuePaths, Path.resolve(__dirname, ROOT_DIR, 'app', 'src')],
                    'node_modules': Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH),
                    'arches/arches/app': Path.resolve(__dirname, ROOT_DIR, 'app'),  // ensure project-level imports of arches components point to local file
                    ...Object.fromEntries(ARCHES_APPLICATIONS.map(app => [  // ensure project-level imports of arches application components point to local file
                        Path.join(app, app), Path.resolve(__dirname, ARCHES_APPLICATIONS_PATHS[app])
                    ])),
                },
            },
            module: {
                rules: [
                    {
                        test: /\.tsx?$/,
                        exclude: /node_modules/,
                        loader: Path.join(PROJECT_RELATIVE_NODE_MODULES_PATH, 'ts-loader'),
                        options: {
                            appendTsSuffixTo: [/\.vue$/],
                            transpileOnly: true,
                            configFile: Path.resolve(__dirname, '..', 'tsconfig.json')
                        }
                    },
                    {
                        test: /\.vue$/,
                        exclude: /node_modules/,
                        loader: Path.join(PROJECT_RELATIVE_NODE_MODULES_PATH, 'vue-loader'),
                    },
                    {
                        test: /\.mjs$/,
                        include: /node_modules/,
                        type: 'javascript/auto',
                    },
                    {
                        test: /\.js$/,
                        exclude: [/node_modules/, /load-component-dependencies/],
                        loader: Path.join(PROJECT_RELATIVE_NODE_MODULES_PATH, 'babel-loader'),
                        options: {
                            presets: ['@babel/preset-env'],
                            cacheDirectory: Path.join(PROJECT_RELATIVE_NODE_MODULES_PATH, '.cache', 'babel-loader'),
                        }
                    },
                    {
                        test: /\.css$/,
                        exclude: [
                            Path.resolve(__dirname, APP_ROOT, 'media', 'css'),
                            Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'css'),
                            ...archesApplicationsCSSFilepaths
                        ],
                        use: [
                            {
                                'loader': Path.join(PROJECT_RELATIVE_NODE_MODULES_PATH, 'style-loader'),
                            },
                            {
                                'loader': Path.join(PROJECT_RELATIVE_NODE_MODULES_PATH, 'css-loader'),
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
                                'loader': Path.join(PROJECT_RELATIVE_NODE_MODULES_PATH, 'css-loader'),
                            },
                            {
                                'loader': Path.join(PROJECT_RELATIVE_NODE_MODULES_PATH, 'postcss-loader'),
                            },
                            {
                                'loader': Path.join(PROJECT_RELATIVE_NODE_MODULES_PATH, 'sass-loader'),
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
                        loader: Path.join(PROJECT_RELATIVE_NODE_MODULES_PATH, 'html-loader'),
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

                                const renderTemplate = async (failureCount = 0) => {
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

                                            if (resp.status === 500) {
                                                throw new Error();
                                            }
                                        }
                                        catch (e) {
                                            failureCount += 1;
                                            console.warn(
                                                '\x1b[33m%s\x1b[0m',  // yellow
                                                `"${templatePath}" has failed to load. Retrying (${failureCount} / 5)...`
                                            );
                                            return await renderTemplate(failureCount = failureCount);
                                        }
                                    }
                                    else {
                                        if (!isTestEnvironment) {
                                            loaderContext.emitError(Error(`Unable to fetch ${templatePath} from the Django server.`))
                                        }
                                        else {
                                            console.warn(
                                                '\x1b[31m%s\x1b[0m',  // red
                                                `"${templatePath}" has failed to load! Test environment detected, falling back to un-rendered file.`
                                            );
                                        }

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
                        use: Path.join(PROJECT_RELATIVE_NODE_MODULES_PATH, 'raw-loader'),
                    },
                    {
                        test: /\.(png|svg|jpg|jpeg|gif)$/i,
                        exclude: /node_modules/,
                        type: 'asset/resource',
                    },
                ],
            },
        });
    });
};
