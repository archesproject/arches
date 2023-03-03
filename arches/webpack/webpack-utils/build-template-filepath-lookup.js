const Path = require('path');
const fs = require('fs');

const _buildTemplateFilePathLookup = function(path, outerAcc, templateDirectoryPath) {
    const outerPath = templateDirectoryPath || path;   // original `path` arg is persisted through recursion

    return fs.readdirSync(path).reduce((acc, name) => {
        if (fs.lstatSync(Path.join(path, name)).isDirectory() ) {
            return _buildTemplateFilePathLookup(
                Path.join(path, name), 
                acc, 
                outerPath
            );
        }
        else {
            let subPath = (Path.join(path, name)).split(/templates(.*)/s)[1];  // splits only on first occurance
            subPath = subPath.substring(1);

            const parsedPath = Path.parse(subPath);
            const filename = parsedPath['dir'] ? Path.join(parsedPath['dir'], parsedPath['base']) : parsedPath['base'];

            return { 
                ...acc, 
                [Path.join('templates', filename)]: Path.resolve(__dirname, Path.join(outerPath, subPath))
            };
        }
    }, outerAcc);
};

const buildTemplateFilePathLookup = function(archesTemplatePath, projectTemplatePath) {
    const coreArchesTemplateFilePathConfiguration = _buildTemplateFilePathLookup(archesTemplatePath, {});
    const projectTemplatePathConfiguration = _buildTemplateFilePathLookup(projectTemplatePath, {});

    return { 
        ...coreArchesTemplateFilePathConfiguration,
        ...projectTemplatePathConfiguration 
    };
};

module.exports = { buildTemplateFilePathLookup };