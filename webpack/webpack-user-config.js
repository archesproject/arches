// Example:
/**
const Path = require('path');
const currentPath =  Path.parse(__dirname)['dir'];

module.exports = {
    USER_DEFINED_ARCHES_CORE_DIRECTORY: Path.resolve(currentPath, '../../../arches/arches'),
    USER_DEFINED_APP_ROOT_DIRECTORY: Path.resolve(currentPath),
    USER_DEFINED_DJANGO_SERVER_ADDRESS: 'http://localhost:8000/',
    USER_DEFINED_WEBPACK_DEVELOPMENT_SERVER_PORT: 9000,
    USER_DEFINED_PUBLIC_PATH: "/static/",
    USER_DEFINED_PROJECT_NODE_MODULES_ALIASES: null,
}
 */

module.exports = {
    USER_DEFINED_ARCHES_CORE_DIRECTORY: null,
    USER_DEFINED_APP_ROOT_DIRECTORY: null,
    USER_DEFINED_DJANGO_SERVER_ADDRESS: null,
    USER_DEFINED_WEBPACK_DEVELOPMENT_SERVER_PORT: null,
    USER_DEFINED_PUBLIC_PATH: null,
}