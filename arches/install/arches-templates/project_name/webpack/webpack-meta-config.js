const Path = require('path');
const projectPath =  Path.parse(__dirname)['dir'];

const archesCoreDirectory = Path.resolve(projectPath, '../../arches/arches');
const appRootDirectory = projectPath;
const djangoServerAddress = "http://localhost:8000/";
const webpackDevelopmentServerPort = 9000;
const publicPath = "/static/";
const projectNodeModulesAliases = JSON.stringify({
    // "example-node-module": "Path.resolve(__dirname, `${appRootDirectory}/media/node_modules/example-node-module`)",
});

module.exports = {
    ARCHES_CORE_DIRECTORY: archesCoreDirectory,
    APP_ROOT_DIRECTORY: appRootDirectory,
    DJANGO_SERVER_ADDRESS: djangoServerAddress,
    WEBPACK_DEVELOPMENT_SERVER_PORT: webpackDevelopmentServerPort,
    PUBLIC_PATH: publicPath,
    PROJECT_NODE_MODULES_ALIASES: projectNodeModulesAliases,
}