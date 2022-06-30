const Path = require('path');


const projectPath = Path.resolve(Path.parse(__dirname)['dir'], './arches/app');

module.exports = {
    ARCHES_CORE_PATH: projectPath,
    PROJECT_PATH: projectPath,
    APPLICATION_SERVER_ADDRESS: "http://localhost:8000/",
}