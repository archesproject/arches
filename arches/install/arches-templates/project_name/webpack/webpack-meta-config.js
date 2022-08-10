const Path = require('path');
const projectPath =  Path.parse(__dirname)['dir'];

const archesCoreDirectory = Path.resolve(projectPath, '../../arches/arches');
const projectRootDirectory = projectPath;
const djangoServerAddress = "http://localhost:8000/";
const webpackDevelopmentServerPort = 9000;
const publicPath = "/static/";
const projectNodeModulesAliases = JSON.stringify({
    // "example-node-module": "Path.resolve(__dirname, `${projectRootDirectory}/media/node_modules/example-node-module`)",
});

module.exports = {
    ARCHES_CORE_DIRECTORY: archesCoreDirectory,
    PROJECT_ROOT_DIRECTORY: projectRootDirectory,
    DJANGO_SERVER_ADDRESS: djangoServerAddress,
    WEBPACK_DEVELOPMENT_SERVER_PORT: webpackDevelopmentServerPort,
    PUBLIC_PATH: publicPath,
    PROJECT_NODE_MODULES_ALIASES: projectNodeModulesAliases,
}