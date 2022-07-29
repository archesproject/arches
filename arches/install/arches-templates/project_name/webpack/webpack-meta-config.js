const Path = require('path');
const { 
    USER_DEFINED_ARCHES_CORE_DIRECTORY, 
    USER_DEFINED_PROJECT_ROOT_DIRECTORY,
    USER_DEFINED_DJANGO_SERVER_ADDRESS, 
    USER_DEFINED_WEBPACK_DEVELOPMENT_SERVER_PORT,
    USER_DEFINED_PUBLIC_PATH,
    USER_DEFINED_PROJECT_NODE_MODULES_ALIASES,
} = require('./webpack-user-config');


const projectPath =  Path.parse(__dirname)['dir'];

const archesCoreDirectory = USER_DEFINED_ARCHES_CORE_DIRECTORY || Path.resolve(projectPath, '../../arches/arches');
const projectRootDirectory = USER_DEFINED_PROJECT_ROOT_DIRECTORY || projectPath;
const djangoServerAddress = USER_DEFINED_DJANGO_SERVER_ADDRESS || "http://localhost:8000/";
const webpackDevelopmentServerPort = USER_DEFINED_WEBPACK_DEVELOPMENT_SERVER_PORT || 9000;
const publicPath = USER_DEFINED_PUBLIC_PATH || "/static/";
const projectNodeModulesAliases = USER_DEFINED_PROJECT_NODE_MODULES_ALIASES || JSON.stringify({
    // "example-node-module": "Path.resolve(__dirname, `${PROJECT_ROOT_DIRECTORY}/media/node_modules/example-node-module`)",
});

module.exports = {
    ARCHES_CORE_DIRECTORY: archesCoreDirectory,
    PROJECT_ROOT_DIRECTORY: projectRootDirectory,
    DJANGO_SERVER_ADDRESS: djangoServerAddress,
    WEBPACK_DEVELOPMENT_SERVER_PORT: webpackDevelopmentServerPort,
    PUBLIC_PATH: publicPath,
    PROJECT_NODE_MODULES_ALIASES: projectNodeModulesAliases,
}