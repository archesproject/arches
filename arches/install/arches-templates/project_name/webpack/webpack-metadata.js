const Path = require('path');


const projectPath =  Path.parse(__dirname)['dir'];

module.exports = {
    ARCHES_CORE_DIRECTORY: Path.resolve(projectPath, '../../arches/arches'),
    PROJECT_PATH: projectPath,
    DJANGO_SERVER_ADDRESS: "http://localhost:8000/",
    WEBPACK_DEVELOPMENT_SERVER_PORT: 9000,
}