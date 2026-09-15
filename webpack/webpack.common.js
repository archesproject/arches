/* eslint-disable */

const fs = require('fs');
const Path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');

const { CleanWebpackPlugin } = require('clean-webpack-plugin');

const { requireVueLoaderWithTypeResolutionPatch } = require('./webpack-utils/patch-vue-compiler-sfc-type-resolution');
const { VueLoaderPlugin } = requireVueLoaderWithTypeResolutionPatch();

const { buildFilepathLookup } = require('./webpack-utils/build-filepath-lookup');

module.exports = () => {
    return new Promise((resolve, _reject) => {
        // BEGIN get data from `webpack-metadata.json`

        const rawData = fs.readFileSync(Path.join(__dirname, "..", "frontend_configuration", 'webpack-metadata.json'), 'utf-8');
        const parsedData = JSON.parse(rawData);

        console.log('Data imported from webpack-metadata.json:', parsedData);

        global.APP_ROOT = parsedData['APP_ROOT'];
        global.ARCHES_APPLICATIONS = parsedData['ARCHES_APPLICATIONS'];
        global.ARCHES_APPLICATIONS_PATHS = parsedData['ARCHES_APPLICATIONS_PATHS'];
        global.RESOLVABLE_APPLICATION_PATHS = parsedData['RESOLVABLE_APPLICATION_PATHS'] || {};
        global.SITE_PACKAGES_DIRECTORY = parsedData['SITE_PACKAGES_DIRECTORY'];
        global.ROOT_DIR = parsedData['ROOT_DIR'];
        global.STATIC_URL = parsedData['STATIC_URL'];
        global.WEBPACK_DEVELOPMENT_SERVER_PORT = parsedData['WEBPACK_DEVELOPMENT_SERVER_PORT'];

        // END get data from `webpack-metadata.json`
        // BEGIN identify bundled applications that are resolvable but not installed

        // Bundled applications always ship their source with arches, so their internal
        // imports (JS, templates, `@/<app>` Vue paths) must resolve even when a project
        // has not enabled them. They must NOT contribute entry points, templates, or
        // static files of their own -- those still come from installed applications only.
        const resolvableOnlyApplicationLabels = Object.keys(RESOLVABLE_APPLICATION_PATHS).filter(
            (label) => !ARCHES_APPLICATIONS.includes(label)
        );

        // END identify bundled applications that are resolvable but not installed
        // BEGIN workaround for handling node_modules paths in arches-core vs projects

        let PROJECT_RELATIVE_NODE_MODULES_PATH;
        if (APP_ROOT.includes(ROOT_DIR)) {  // should only return truthy for running Arches-core without a project
            PROJECT_RELATIVE_NODE_MODULES_PATH = Path.resolve(ROOT_DIR, '..', 'node_modules');
        }
        else {
            PROJECT_RELATIVE_NODE_MODULES_PATH = Path.resolve(APP_ROOT, '..', 'node_modules');
        }

        // END workaround for handling node_modules paths in arches-core vs projects
        // BEGIN create entry point configurations

        const archesCoreEntryPointConfiguration = buildFilepathLookup(Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'js'));

        const runningWithoutProject = APP_ROOT.includes(ROOT_DIR);
        const projectEntryPointConfiguration = runningWithoutProject
            ? {}
            : buildFilepathLookup(Path.resolve(__dirname, APP_ROOT, 'media', 'js'));

        const archesApplicationsEntrypointConfiguration = ARCHES_APPLICATIONS.reduce((acc, archesApplication) => {
            return {
                ...acc,
                ...buildFilepathLookup(Path.resolve(__dirname, ARCHES_APPLICATIONS_PATHS[archesApplication], 'media', 'js'))
            };
        }, {});

        // order is important! Arches core files are overwritten by arches-application files, arches-application files are overwritten by project files
        const entryPoints = {
            ...archesCoreEntryPointConfiguration,
            ...archesApplicationsEntrypointConfiguration,
            ...projectEntryPointConfiguration,
        };

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

        // resolvable-but-not-installed bundled applications: alias-only, not merged into `entryPoints`
        const resolvableOnlyApplicationsJavascriptEntrypointConfiguration = resolvableOnlyApplicationLabels.reduce((acc, label) => {
            return {
                ...acc,
                ...buildFilepathLookup(Path.resolve(__dirname, RESOLVABLE_APPLICATION_PATHS[label], 'media', 'js'))
            };
        }, {});
        const resolvableOnlyApplicationsJavascriptRelativeFilepathToAbsoluteFilepathLookup = Object.entries(resolvableOnlyApplicationsJavascriptEntrypointConfiguration).reduce((acc, [path, config]) => {
            acc[path + '$'] = Path.resolve(__dirname, path, config['import']);
            return acc;
        }, {});

        // order is important! Arches core files are overwritten by arches-application files, arches-application files are overwritten by project files
        const javascriptRelativeFilepathToAbsoluteFilepathLookup = {
            ...archesCoreJavascriptRelativeFilepathToAbsoluteFilepathLookup,
            ...resolvableOnlyApplicationsJavascriptRelativeFilepathToAbsoluteFilepathLookup,
            ...archesApplicationsJavascriptRelativeFilepathToAbsoluteFilepathLookup,
            ...projectJavascriptRelativeFilepathToAbsoluteFilepathLookup,
        };

        // END create JavaScript filepath lookups
        // BEGIN create node modules aliases
        let archesCorePackageJSONFilepath = Path.resolve(__dirname, ROOT_DIR, '..', 'package.json');
        if (!fs.existsSync(archesCorePackageJSONFilepath)) {
            archesCorePackageJSONFilepath = Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH, 'arches', 'package.json');
        }

        const archesCorePackageJSON = require(archesCorePackageJSONFilepath);

        const parsedArchesCoreNodeModulesAliases = Object.entries(archesCorePackageJSON['nodeModulesPaths']).reduce((acc, [alias, subPath]) => {
            // handles for node_modules -esque sources shipped inside arches core's media directory
            if (subPath.startsWith('plugins/') || subPath.startsWith('js/')) {
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

        // resolvable-but-not-installed bundled applications: alias-only, not merged into entry points
        const resolvableOnlyApplicationsTemplatePathConfiguration = resolvableOnlyApplicationLabels.reduce((acc, label) => {
            return {
                ...acc,
                ...buildFilepathLookup(Path.resolve(__dirname, RESOLVABLE_APPLICATION_PATHS[label], 'templates'))
            };
        }, {});

        // order is important! Arches core files are overwritten by arches-application files, arches-application files are overwritten by project files
        const templateFilepathLookup = {
            ...coreArchesTemplatePathConfiguration,
            ...resolvableOnlyApplicationsTemplatePathConfiguration,
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

        // resolvable-but-not-installed bundled applications: alias-only, so their internal
        // `@/<app>/...` imports resolve even though they contribute no CSS/entry points
        const resolvableOnlyApplicationVuePaths = resolvableOnlyApplicationLabels.map(
            (label) => Path.resolve(__dirname, RESOLVABLE_APPLICATION_PATHS[label], 'src')
        );

        // END create vue filepath lookup
        // BEGIN create universal constants

        const universalConstants = {
            APP_ROOT_DIRECTORY: JSON.stringify(APP_ROOT).replace(/\\/g, '/'),
            ARCHES_APPLICATIONS: JSON.stringify(ARCHES_APPLICATIONS),
            ARCHES_CORE_DIRECTORY: JSON.stringify(ROOT_DIR).replace(/\\/g, '/'),
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
                ...entryPoints,
                ...CSSFilepathLookup,
            },
            output: {
                assetModuleFilename: '[name].[contenthash][ext]',
                chunkFilename: 'chunks/[name].[contenthash].js',
                clean: true,
                filename: '[name].[contenthash].js',
                path: Path.resolve(__dirname, APP_ROOT, 'media', 'build'),
                publicPath: STATIC_URL,
            },
            optimization: {
                moduleIds: 'deterministic',
                chunkIds: 'deterministic',
                runtimeChunk: { name: 'chunks/runtime' },
                splitChunks: {
                    chunks: 'all',
                    maxInitialRequests: 25,
                    maxAsyncRequests: 25,
                    cacheGroups: {
                        vendors: {
                            test: /[\\/]node_modules[\\/]/,
                            enforce: true,
                            priority: -10,
                            reuseExistingChunk: true,
                            filename: 'chunks/vendors.[contenthash].js'
                        },
                        commons: {
                            minChunks: 2,
                            enforce: true,
                            priority: -20,
                            reuseExistingChunk: true,
                            filename: 'chunks/commons.[contenthash].js'
                        },
                    },
                },
                concatenateModules: true,
                removeAvailableModules: true,
            },
            plugins: [
                new CleanWebpackPlugin(),
                new webpack.DefinePlugin(universalConstants),
                new webpack.DefinePlugin({
                    ARCHES_URLS: webpack.DefinePlugin.runtimeValue(
                        () => fs.readFileSync(
                            Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH, '..', 'frontend_configuration', 'urls.json'),
                            'utf-8'
                        ),
                        true  // should be re-evaluated on rebuild
                    ),
                }),
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
                ...Object.keys(entryPoints).map(name => {
                    return new webpack.EntryPlugin(
                        __dirname,
                        Path.resolve(__dirname, ROOT_DIR, 'app', 'media', 'js', 'template-loader'),
                        { name: name },
                    )
                }),
                new MiniCssExtractPlugin({
                    filename: '[name].[contenthash].css',
                }),
                new BundleTracker({
                    path: Path.resolve(__dirname),
                    filename: 'webpack-stats.json',
                }),
                new VueLoaderPlugin(),
            ],
            resolve: {
                extensions: ['.ts', '.tsx', '.wasm', '.mjs', '.js', '.json'],
                modules: [Path.resolve(__dirname, PROJECT_RELATIVE_NODE_MODULES_PATH)],
                alias: {
                    ...javascriptRelativeFilepathToAbsoluteFilepathLookup,
                    ...templateFilepathLookup,
                    ...imageFilepathLookup,
                    ...nodeModulesAliases,
                    '@': [Path.resolve(__dirname, APP_ROOT, 'src'), ...archesApplicationsVuePaths, ...resolvableOnlyApplicationVuePaths, Path.resolve(__dirname, ROOT_DIR, 'app', 'src')],
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
                        test: /\.(d\.ts|(spec|test)\.tsx?)$/,
                        type: "asset/source",
                    },
                    {
                        test: /\.tsx?$/,
                        exclude: [/node_modules/, /\.d\.ts$/, /\.(spec|test)\.tsx?$/],
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
                        // maplibre-gl loads its tile-parsing worker as a separate script at
                        // runtime; emit it as a standalone static asset so `new URL(...)`
                        // resolves to a real, fetchable file instead of being inlined.
                        test: /maplibre-gl-worker(-dev)?\.mjs$/,
                        type: 'asset/resource',
                        generator: {
                            filename: 'js/[name][ext]',
                        },
                    },
                    {
                        // the worker script above imports this module by relative path at
                        // *runtime*, a path webpack can't see (it never parses inside an
                        // asset/resource file), so it must be emitted alongside it as a real
                        // file too. Bindings code triggers this explicitly with a `?asset`
                        // suffix; the plain (no-query) import used by the main-thread bundle
                        // still gets bundled normally by the rule below.
                        test: /maplibre-gl-shared(-dev)?\.mjs$/,
                        resourceQuery: /asset/,
                        type: 'asset/resource',
                        generator: {
                            filename: 'js/[name][ext]',
                        },
                    },
                    {
                        test: /\.mjs$/,
                        include: /node_modules/,
                        exclude: /maplibre-gl-worker(-dev)?\.mjs$/,
                        resourceQuery: { not: /asset/ },
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
                            ...resolvableOnlyApplicationVuePaths,
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
                        test: /\.(woff2?|eot|ttf|otf)$/i,
                        type: 'asset/resource',
                        generator: {
                            filename: 'fonts/[name].[contenthash][ext]',
                        },
                    },
                    {
                        test: /\.htm$/i,
                        type: 'asset/resource',
                        generator: {
                            filename: (pathData) => {
                                return pathData.module.rawRequest;
                            },
                            publicPath: '',  // this ensures that Knockout can render the template on page load
                            emit: false,
                        },
                    },
                    {
                        test: /\.(txt|DS_Store)$/i,
                        type: 'asset/resource',
                        generator: {
                            emit: false,
                        },
                    },

                    {
                        test: /\.(png|jpe?g|gif|svg)$/,
                        type: 'asset/resource',
                        generator: {
                            filename: 'img/[name].[contenthash][ext]',
                        },
                    },
                ],
            },
        });
    });
};
