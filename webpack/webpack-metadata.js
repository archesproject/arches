const Path = require('path');


const projectPath = Path.resolve(Path.parse(__dirname)['dir'], './arches');

module.exports = {
    ARCHES_CORE_DIRECTORY: projectPath,
    PROJECT_PATH: projectPath + '/app',
    DJANGO_SERVER_ADDRESS: "http://localhost:8000/",
    WEBPACK_DEVELOPMENT_SERVER_PORT: 9000,
}