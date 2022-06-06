const Path = require('path');


const projectPath =  Path.parse(__dirname)['dir'];

module.exports = {
    ARCHES_CORE_PATH: Path.resolve(projectPath, '../../arches/arches/app'),
    PROJECT_PATH: projectPath,
}